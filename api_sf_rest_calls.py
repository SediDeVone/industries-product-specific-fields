from simple_salesforce import Salesforce


def _sf_client(access_token, instance_url):
    host = instance_url.replace('https://', '').replace('http://', '')
    return Salesforce(instance=host, session_id=access_token, version='60.0')


def prepare_object_fields_describe(access_token, instance_url, object_to_export, all_fields):
    sf = _sf_client(access_token, instance_url)
    describe = getattr(sf, object_to_export).describe()

    if not describe.get('queryable', False):
        raise Exception("This object is not queryable")

    fields = []
    for f in describe.get('fields', []):
        if all_fields:
            fields.append(f['name'])
        elif f.get('updateable') or f.get('createable'):
            fields.append(f['name'])

    return fields


def download_all(access_token, instance_url, object_to_export, variant_query, all_fields, limit):
    sf = _sf_client(access_token, instance_url)
    fields = prepare_object_fields_describe(access_token, instance_url, object_to_export, all_fields)

    query = "SELECT %s FROM %s%s LIMIT %i" % (
        ", ".join(fields),
        object_to_export,
        variant_query,
        limit
    )

    res = sf.query_all(query)
    rows = res.get('records', [])

    for r in rows:
        if isinstance(r, dict) and 'attributes' in r:
            r.pop('attributes', None)

    return rows
