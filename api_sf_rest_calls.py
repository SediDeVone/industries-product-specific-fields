import requests
import csv
from salesforce_bulk import SalesforceBulk, CsvDictsAdapter


def sf_api_call(access_token, instance_url, action, parameters={}, method='get', data={}):
    headers = {
        'Content-type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer %s' % access_token
    }

    if method == 'get':
        r = requests.request(method, instance_url + action, headers=headers, params=parameters, timeout=30)
    elif method in ['post', 'patch']:
        r = requests.request(method, instance_url + action, headers=headers, json=data, params=parameters, timeout=10)
    else:
        # other methods not implemented in this example
        raise ValueError('Method should be get or post or patch.')

    print('Debug: API %s call: %s' % (method, r.url))

    if r.status_code < 300:
        if method == 'patch':
            return None
        else:
            return r.json()
    else:
        raise Exception('API error when calling %s : %s' % (r.url, r.content))


def upload_data(dict_data, object_name, authorize_object):
    bulk = SalesforceBulk(
        username=authorize_object.username, password=authorize_object.password,
        security_token=authorize_object.security_token,
        host=authorize_object.host, sandbox=authorize_object.is_sandbox
    )

    # Fix with proper external field name mapping
    job = bulk.create_upsert_job(object_name, 'Legacy_ID__c', contentType='CSV', concurrency='Serial')

    parsed_data = CsvDictsAdapter(iter(dict_data))
    batch = bulk.post_batch(job, parsed_data)
    bulk.wait_for_batch(job, batch)
    bulk.close_job(job)

    print("Done. Data Uploaded.")


def upload_file(file_name, object_name, authorize_object, is_update):
    bulk = SalesforceBulk(
        username=authorize_object.username, password=authorize_object.password,
        security_token=authorize_object.security_token,
        host=authorize_object.host, sandbox=authorize_object.is_sandbox
    )

    if is_update:
        job = bulk.create_update_job(object_name, contentType='CSV', concurrency='Serial')
    else:
        job = bulk.create_insert_job(object_name, contentType='CSV', concurrency='Serial', pk_chunking=50)

    reader = csv.DictReader(open(file_name))
    disbursals = []
    for row in reader:
        disbursals.append(row)

    parsed_data = CsvDictsAdapter(iter(disbursals))
    batch = bulk.post_batch(job, parsed_data)
    bulk.wait_for_batch(job, batch)
    bulk.close_job(job)

    print("Done. Data Uploaded.")


def prepare_object_fields_describe(access_token, instance_url, object_to_export, all_fields, persistent_external_id):
    describe = sf_api_call(access_token, instance_url, '/services/data/v43.0/sobjects/%s/describe' % object_to_export)

    if not describe.get('queryable', False):
        raise Exception("This object is not queryable")

    fields = []
    for f in describe.get('fields'):
        if f['name'] == 'Agreement_Number__c':
            fields.append(f['name'])

        if all_fields or (persistent_external_id and (f['name'] == 'Id' or f['name'] == 'PersonContactId')):
            fields.append(f['name'])
        elif f['updateable'] or f['createable']:
            fields.append(f['name'])

    return fields


def prepare_object_record_types_describe(access_token, instance_url, object_to_export):
    describe = sf_api_call(access_token, instance_url, '/services/data/v43.0/sobjects/%s/describe' % object_to_export)

    if not describe.get('queryable', False):
        raise Exception("This object is not queryable")

    record_types = dict()
    for f in describe.get('recordTypeInfos'):
        record_types[f['developerName']] = f['recordTypeId']

    return record_types


# Exporting all the records of an object with all fields
def download_all(access_token, instance_url, object_to_export, variant_query, all_fields, limit, persistent_external_id):
    fields = prepare_object_fields_describe(access_token, instance_url, object_to_export, all_fields, persistent_external_id)

    query = "SELECT %s FROM %s%s LIMIT %i" % (
        ", ".join(fields),
        object_to_export,
        variant_query,
        limit
    )

    call = sf_api_call(access_token, instance_url, '/services/data/v43.0/queryAll/', {'q': query})

    rows = call.get('records', [])

    next = call.get('nextRecordsUrl', None)

    while next:
        call = sf_api_call(access_token, instance_url, next)
        rows.extend(call.get('records', []))
        next = call.get('nextRecordsUrl', None)

    return rows
