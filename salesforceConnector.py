import subprocess
import json
import os
from typing import Tuple


def connect_to_sf_environment(username: str, domain: str) -> Tuple[str, str]:
    """Retrieve access token and instance URL for a Salesforce org via Salesforce CLI.

    Note: domain is currently unused (kept for backward compatibility). The function relies on the
    Salesforce CLI alias (username) to fetch credentials. On failure, it attempts a JWT-based reauth
    using environment variables '<ALIAS>_CLIENT_ID' and '<ALIAS>_USERNAME' and a local 'server.key'.
    """
    if not username:
        raise ValueError("username (org alias) is required")

    env_name = username.lower()

    def run_json(cmd: list) -> dict:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{err.decode('utf-8', 'ignore')}")
        try:
            return json.loads(out.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON from sf CLI: {e}\nOutput: {out[:200]!r}")

    try:
        sfdx_info = run_json(["sf", "force:org:display", "--target-org", env_name, "--json"])
    except Exception:
        sfdx_info = {}

    if 'result' in sfdx_info:
        access_token = sfdx_info['result']['accessToken']
        instance_url = sfdx_info['result']['instanceUrl']
        return access_token, instance_url

    # Fallback: try JWT reauth
    client_id = os.environ.get(f"{username}_CLIENT_ID") or os.environ.get(username.capitalize() + '_CLIENT_ID')
    username_email = os.environ.get(f"{username}_USERNAME") or os.environ.get(username.capitalize() + '_USERNAME')
    if not client_id or not username_email:
        raise RuntimeError("Missing JWT environment variables '<alias>_CLIENT_ID' and '<alias>_USERNAME'")

    # Perform JWT login
    _ = subprocess.Popen(
        ["sf", "org", "login", "jwt", "--client-id", client_id, "--jwt-key-file", "server.key", "--username", username_email, "--alias", env_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).communicate()

    sfdx_info = run_json(["sf", "force:org:display", "--target-org", env_name, "--json"])
    access_token = sfdx_info['result']['accessToken']
    instance_url = sfdx_info['result']['instanceUrl']

    return access_token, instance_url