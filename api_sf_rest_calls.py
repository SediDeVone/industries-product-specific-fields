from typing import List, Dict, Any
from simple_salesforce import Salesforce


def _sf_client(access_token: str, instance_url: str) -> Salesforce:
    """Create a simple_salesforce client from token and instance URL."""
    if not access_token:
        raise ValueError("access_token is required")
    if not instance_url:
        raise ValueError("instance_url is required")
    host = instance_url.replace('https://', '').replace('http://', '')
    return Salesforce(instance=host, session_id=access_token, version='60.0')


def prepare_object_fields_describe(access_token: str, instance_url: str, object_to_export: str, all_fields: bool) -> List[str]:
    """Return list of field API names for the given object.

    If all_fields is False, returns only fields that are either updateable or createable.
    Raises a ValueError if the object is not queryable.
    """
    sf = _sf_client(access_token, instance_url)
    try:
        describe = getattr(sf, object_to_export).describe()
    except Exception as e:
        raise RuntimeError(f"Failed to describe object '{object_to_export}': {e}") from e

    if not describe.get('queryable', False):
        raise ValueError("This object is not queryable")

    fields: List[str] = []
    for f in describe.get('fields', []):
        if all_fields:
            fields.append(f['name'])
        elif f.get('updateable') or f.get('createable'):
            fields.append(f['name'])

    return fields


def download_all(access_token: str, instance_url: str, object_to_export: str, variant_query: str, all_fields: bool, limit: int) -> List[Dict[str, Any]]:
    """Download records for the given object with a simple SELECT query.

    variant_query should start with a space and a WHERE/ORDER BY clause (e.g., ' WHERE IsDeleted = false').
    Note: Avoid passing untrusted input into variant_query to prevent SOQL injection.
    """
    sf = _sf_client(access_token, instance_url)
    fields = prepare_object_fields_describe(access_token, instance_url, object_to_export, all_fields)

    if not fields:
        return []

    # Basic guardrails for variant_query to reduce malformed queries
    vq = variant_query or ''
    if vq and not vq.startswith(' '):
        vq = ' ' + vq

    query = "SELECT %s FROM %s%s LIMIT %i" % (
        ", ".join(fields),
        object_to_export,
        vq,
        limit,
    )

    res = sf.query_all(query)
    rows = res.get('records', [])

    for r in rows:
        if isinstance(r, dict) and 'attributes' in r:
            r.pop('attributes', None)

    return rows
