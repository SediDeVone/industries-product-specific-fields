class AuthorizationObject(object):
    name = ""
    username = ""
    password = ""
    security_token = ""
    host = ""
    consumer_key = ""
    consumer_secret = ""
    is_sandbox = False

    def __init__(self, name, username, password, security_token, host, consumer_key, consumer_secret, is_sandbox):
        self.name = name
        self.username = username
        self.password = password
        self.security_token = security_token
        self.host = host
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.is_sandbox = is_sandbox
        # print('Creating Authorization object: ', str(self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


class SFDCObject(object):
    name = ""
    variants = []
    matching_api_name = ""
    dependencies = []
    record_type_mapping = []
    default_retrieve_query = ""

    def __init__(self, name, variants, matching_api_name, dependencies, record_type_mapping, default_retrieve_query):
        self.name = name
        self.variants = variants
        self.matching_api_name = matching_api_name
        self.dependencies = dependencies
        self.record_type_mapping = record_type_mapping
        self.default_retrieve_query = default_retrieve_query
        # print('Creating Salesforce object: ', str(self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__


class Variant(object):
    name = ""
    soql_query = ""

    def __init__(self, name, soql_query):
        self.name = name
        self.soql_query = soql_query
        # print('Creating variant for Salesforce object:', str(self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
