from ckan.logic.validators import resource_id_exists
from ckan.lib.navl.validators import not_empty, ignore_missing

from ckanext.resourceauthorizer.logic.validators import auth_type_validator
from ckanext.resourceauthorizer.logic.validators import permission_validator


def resource_acl_create_schema():
    schema = {
        'resource_id': [resource_id_exists],
        'auth_type': [auth_type_validator, unicode],
        'auth_id': [not_empty, unicode],
        'permission': [permission_validator, unicode],
    }
    return schema


def resource_acl_update_schema():
    schema = {
        'auth_type': [auth_type_validator, unicode],
        'auth_id': [not_empty, unicode],
        'permission': [permission_validator, unicode],
    }
    return schema


def resource_acl_patch_schema():
    schema = {
        'auth_type': [ignore_missing, auth_type_validator, unicode],
        'auth_id': [ignore_missing, not_empty, unicode],
        'permission': [ignore_missing, permission_validator, unicode],
    }
    return schema
