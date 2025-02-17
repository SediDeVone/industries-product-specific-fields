import json
import os

from model_definition import AuthorizationObject, Variant, SFDCObject

NAMESPACE = ''
DEFAULT_USER_ID = ''
EXTERNAL_FIELD_NAME = 'Legacy_ID__c'
AUTHORISATION_DICT = dict()
OBJECTS = []
OBJECTS_WITHOUT_EXTERNAL_ID = []
IS_DELETED_QUERY = ' WHERE isDeleted = false'


def import_json_data(rel_path):
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "r") as read_file:
        data = json.load(read_file)

        global EXTERNAL_FIELD_NAME
        EXTERNAL_FIELD_NAME = data['external field name']

        global NAMESPACE
        NAMESPACE = data['namespace']

        global DEFAULT_USER_ID
        DEFAULT_USER_ID = data['default user id']

        global OBJECTS_WITHOUT_EXTERNAL_ID
        OBJECTS_WITHOUT_EXTERNAL_ID = data['objects to skip adding external Id']

        print("Creating authorization data...")
        prepare_authorization_dict(data)

        print("Creating custom objects data...")
        prepare_objects_data(data)


def retrieve_objects_without_external_id():
    return OBJECTS_WITHOUT_EXTERNAL_ID


def retrieve_external_field_name():
    return EXTERNAL_FIELD_NAME


def retrieve_namespace():
    return NAMESPACE


def retrieve_default_user_id():
    return DEFAULT_USER_ID


def prepare_authorization_dict(data):
    global AUTHORISATION_DICT
    for environment_access in data['environment_access']:
        environment = AuthorizationObject(
            environment_access['name'],
            environment_access['username'],
            environment_access['password'],
            environment_access['security_token'],
            environment_access['host'],
            environment_access['consumer_key'],
            environment_access['consumer_secret'],
            environment_access['is_sandbox']
        )

        AUTHORISATION_DICT[environment.name] = environment


def prepare_objects_data(data):
    global OBJECTS
    for object_data in data['objects']:
        object_variants = []
        object_record_type_mapping = dict()

        for variant in object_data['variants']:
            object_variants.append(Variant(variant['name'], variant['soql_query']))

        for record_type_mapping in object_data['record_type_mapping']:
            object_record_type_mapping[record_type_mapping['source_name']] = record_type_mapping['target_name']

        sfdc_object = SFDCObject(
            object_data['name'],
            object_variants,
            object_data['matching_api_name'],
            object_data['dependencies'],
            object_record_type_mapping,
            object_data['default_retrieve_query']
        )

        OBJECTS.append(sfdc_object)
