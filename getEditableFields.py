from api_sf_rest_calls import prepare_object_fields_describe, download_all
from salesforceConnector import connect_to_sf_environment
import argparse


def get_editable_field_per_product(object_name, product_id_field, default_retrieve_query, org_alias, domain='test'):
    object_limit = 50000

    source_access_token, source_instance_url = connect_to_sf_environment(org_alias, domain)

    createable_fields = prepare_object_fields_describe(source_access_token, source_instance_url, object_name,
                                                   False, False)

    retrieved_records = download_all(source_access_token, source_instance_url, object_name,
                                          default_retrieve_query, True, object_limit, False)

    product_records = download_all(source_access_token, source_instance_url, 'Product2',
                                          default_retrieve_query, True, object_limit, False)
    product_dict = convert_objects_to_dict(product_records, 'Id')

    fields_map = dict()
    for main_record in retrieved_records:
        if main_record[product_id_field] in product_dict:
            product_name = product_dict[main_record[product_id_field]]['Name']
            if product_name in fields_map:
                appropiate_fields = fields_map[product_name]
            else:
                appropiate_fields = set()

            for field_name in createable_fields:
                field_value = main_record[field_name]
                if field_value is not None and field_value != "" and field_value != 0 and field_value != False:
                    appropiate_fields.add(field_name)

            fields_map[product_name] = appropiate_fields
    # print(fields_map)
    for key, value in fields_map.items():
        print(key, value)


def get_editable_field_per_product_and_action(object_name, product_id_field, default_retrieve_query, action_field_name, sub_action_field_name, org_alias, domain='test'):
    object_limit = 50000

    source_access_token, source_instance_url = connect_to_sf_environment(org_alias, domain)

    createable_fields = prepare_object_fields_describe(source_access_token, source_instance_url, object_name,
                                                   False, False)

    retrieved_records = download_all(source_access_token, source_instance_url, object_name,
                                          default_retrieve_query, True, object_limit, False)

    product_records = download_all(source_access_token, source_instance_url, 'Product2',
                                          default_retrieve_query, True, object_limit, False)
    product_dict = convert_objects_to_dict(product_records, 'Id')

    fields_map = dict()
    for main_record in retrieved_records:
        product_name = product_dict[main_record[product_id_field]]['Name']
        action_name = main_record[action_field_name]
        sub_action_name = main_record[sub_action_field_name]
        final_action_name = prepare_action_name(action_name, sub_action_name)

        if product_name in fields_map:
            appropiate_fields_per_action = fields_map[product_name]
        else:
            appropiate_fields_per_action = dict()
            fields_map[product_name] = appropiate_fields_per_action

        if final_action_name in appropiate_fields_per_action:
            appropiate_fields = appropiate_fields_per_action[final_action_name]
        else:
            appropiate_fields = set()

        for field_name in createable_fields:
            field_value = main_record[field_name]
            if field_value is not None and field_value != "" and field_value != 0 and field_value != False:
                appropiate_fields.add(field_name)

        fields_map[product_name][final_action_name] = appropiate_fields

    for key, value in fields_map.items():
        print(key, value)


def prepare_action_name(action_name, subaction_name):
    if action_name is None:
        _action_name = ''
    else:
        _action_name = action_name

    if subaction_name is None:
        _subaction_name = ''
    else:
        _subaction_name = subaction_name

    return _action_name + ' ' + _subaction_name


def convert_objects_to_dict(main_records, field_name):
    main_records_dict = dict()
    for main_record in main_records:
        if field_name in main_record:
            main_records_dict[main_record[field_name]] = main_record

    return main_records_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze editable fields per product in Salesforce objects')
    parser.add_argument('--org', dest='org_alias', required=True, help='Salesforce CLI alias (org name), e.g., org-qa')
    parser.add_argument('--domain', dest='domain', default='test', help='Salesforce domain (login domain), default: test')
    args = parser.parse_args()

    print('----------------- PER PRODUCT ----------------------')
    # Get Schema for Quote Line Items
    print('----------------- QLI ----------------------')
    get_editable_field_per_product('QuoteLineItem', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
    print('--------------------------------------------')
    # Get Schema for Quote Line Items
    print('----------------- ORP ----------------------')
    get_editable_field_per_product('OrderItem', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
    print('-------------------------------------')
    # Get Schema for Quote Line Items
    print('----------------- Asset --------------------')
    get_editable_field_per_product('Asset', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
    print('--------------------------------------------')

    # print('----------------- PER PRODUCT AND ACTION----------------------')
    # # Get Schema for Quote Line Items
    # print('----------------- QLI ----------------------')
    # get_editable_field_per_product_and_action('QuoteLineItem', 'Product2Id', ' WHERE isDeleted = false', 'vlocity_cmt__Action__c', 'vlocity_cmt__SubAction__c', args.org_alias, args.domain)
    # print('--------------------------------------------')
    # # Get Schema for Quote Line Items
    # print('----------------- ORP ----------------------')
    # get_editable_field_per_product_and_action('OrderItem', 'Product2Id', ' WHERE isDeleted = false', 'vlocity_cmt__Action__c', 'vlocity_cmt__SubAction__c', args.org_alias, args.domain)
    # print('-------------------------------------')
