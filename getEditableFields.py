from api_sf_rest_calls import prepare_object_fields_describe, download_all
from salesforceConnector import connect_to_sf_environment
import argparse
import datetime
import os
from typing import Dict, List, Set


def get_editable_field_per_product(object_name: str, product_id_field: str, default_retrieve_query: str, org_alias: str, domain: str = 'test') -> Dict[str, Set[str]]:
    """Compute set of non-empty fields per product for the given SObject.

    Returns a mapping: Product2.Name -> set(field API names)
    """
    object_limit = 50000

    source_access_token, source_instance_url = connect_to_sf_environment(org_alias, domain)

    createable_fields = prepare_object_fields_describe(source_access_token, source_instance_url, object_name, False)

    retrieved_records = download_all(source_access_token, source_instance_url, object_name,
                                     default_retrieve_query, True, object_limit)

    product_records = download_all(source_access_token, source_instance_url, 'Product2',
                                   default_retrieve_query, True, object_limit)
    product_dict = convert_objects_to_dict(product_records, 'Id')

    fields_map: Dict[str, Set[str]] = dict()
    for main_record in retrieved_records:
        product_id = main_record.get(product_id_field)
        if product_id and product_id in product_dict:
            product_name = product_dict[product_id].get('Name')
            if not product_name:
                continue
            appropiate_fields = fields_map.get(product_name, set())

            for field_name in createable_fields:
                field_value = main_record.get(field_name)
                if field_value not in (None, "", 0, False):
                    appropiate_fields.add(field_name)

            fields_map[product_name] = appropiate_fields

    return fields_map


def get_editable_field_per_product_and_action(object_name: str, product_id_field: str, default_retrieve_query: str, action_field_name: str, sub_action_field_name: str, org_alias: str, domain: str = 'test') -> Dict[str, Dict[str, Set[str]]]:
    """Compute non-empty fields per product broken down by action and sub-action.

    Returns: Product2.Name -> { Action/SubAction label -> set(field API names) }
    """
    object_limit = 50000

    source_access_token, source_instance_url = connect_to_sf_environment(org_alias, domain)

    createable_fields = prepare_object_fields_describe(source_access_token, source_instance_url, object_name, False)

    retrieved_records = download_all(source_access_token, source_instance_url, object_name,
                                     default_retrieve_query, True, object_limit)

    product_records = download_all(source_access_token, source_instance_url, 'Product2',
                                   default_retrieve_query, True, object_limit)
    product_dict = convert_objects_to_dict(product_records, 'Id')

    fields_map: Dict[str, Dict[str, Set[str]]] = dict()
    for main_record in retrieved_records:
        product_id = main_record.get(product_id_field)
        if not product_id or product_id not in product_dict:
            continue
        product_name = product_dict[product_id].get('Name')
        if not product_name:
            continue
        action_name = main_record.get(action_field_name)
        sub_action_name = main_record.get(sub_action_field_name)
        final_action_name = prepare_action_name(action_name, sub_action_name)

        appropiate_fields_per_action = fields_map.get(product_name, {})

        appropiate_fields = appropiate_fields_per_action.get(final_action_name, set())

        for field_name in createable_fields:
            field_value = main_record.get(field_name)
            if field_value not in (None, "", 0, False):
                appropiate_fields.add(field_name)

        appropiate_fields_per_action[final_action_name] = appropiate_fields
        fields_map[product_name] = appropiate_fields_per_action

    return fields_map


def prepare_action_name(action_name, subaction_name):
    if action_name is None:
        _action_name = ''
    else:
        _action_name = action_name

    if subaction_name is None:
        _subaction_name = ''
    else:
        _subaction_name = subaction_name

    return (_action_name + ' ' + _subaction_name).strip()


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
    parser.add_argument('--mode', dest='mode', default='product', help='Specify whether the retrieval should be based on product or action')
    parser.add_argument('--out', dest='out_file', default=None, help='Path to output Markdown file (.md). Defaults to autogenerated timestamped file.')
    args = parser.parse_args()

    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    default_name = f'editable_fields_{args.mode}_{timestamp}.md'
    out_path = args.out_file or default_name

    lines: List[str] = []

    if args.mode == 'product':
        lines.append('# Editable Fields Per Product')
        lines.append('')
        # QLI
        lines.append('## QuoteLineItem (Product2Id)')
        qli = get_editable_field_per_product('QuoteLineItem', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
        for product, fields in sorted(qli.items()):
            lines.append(f'### {product}')
            if fields:
                for f in sorted(fields):
                    lines.append(f'- {f}')
            else:
                lines.append('- (no editable fields detected)')
            lines.append('')
        # ORP
        lines.append('## OrderItem (Product2Id)')
        orp = get_editable_field_per_product('OrderItem', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
        for product, fields in sorted(orp.items()):
            lines.append(f'### {product}')
            if fields:
                for f in sorted(fields):
                    lines.append(f'- {f}')
            else:
                lines.append('- (no editable fields detected)')
            lines.append('')
        # Asset
        lines.append('## Asset (Product2Id)')
        asset = get_editable_field_per_product('Asset', 'Product2Id', ' WHERE isDeleted = false', args.org_alias, args.domain)
        for product, fields in sorted(asset.items()):
            lines.append(f'### {product}')
            if fields:
                for f in sorted(fields):
                    lines.append(f'- {f}')
            else:
                lines.append('- (no editable fields detected)')
            lines.append('')

    if args.mode == 'action':
        lines.append('# Editable Fields Per Product And Action')
        lines.append('')
        # QLI
        lines.append('## QuoteLineItem (Product2Id, by Action)')
        qli = get_editable_field_per_product_and_action('QuoteLineItem', 'Product2Id', ' WHERE isDeleted = false', 'vlocity_cmt__Action__c', 'vlocity_cmt__SubAction__c', args.org_alias, args.domain)
        for product, actions in sorted(qli.items()):
            lines.append(f'### {product}')
            for action, fields in sorted(actions.items()):
                lines.append(f'- {action or "(no action)"}')
                if fields:
                    for f in sorted(fields):
                        lines.append(f'  - {f}')
                else:
                    lines.append('  - (no editable fields detected)')
            lines.append('')
        # ORP
        lines.append('## OrderItem (Product2Id, by Action)')
        orp = get_editable_field_per_product_and_action('OrderItem', 'Product2Id', ' WHERE isDeleted = false', 'vlocity_cmt__Action__c', 'vlocity_cmt__SubAction__c', args.org_alias, args.domain)
        for product, actions in sorted(orp.items()):
            lines.append(f'### {product}')
            for action, fields in sorted(actions.items()):
                lines.append(f'- {action or "(no action)"}')
                if fields:
                    for f in sorted(fields):
                        lines.append(f'  - {f}')
                else:
                    lines.append('  - (no editable fields detected)')
            lines.append('')

    # Ensure directory exists and write file
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'Markdown report written to: {out_path}')
