from ckan.plugins.toolkit import auth_allow_anonymous_access
import ckan.plugins as p
import ckan.authz as authz
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.logic.auth import (get_package_object, get_group_object,
                             get_resource_object)
from ckanext.resourceauthorizer.model import ResourceAcl
from ckan.logic.auth.get import package_show as ckan_package_show
from ckan.logic.auth.get import resource_show as ckan_resource_show
from ckan.logic.auth.update import resource_update as ckan_resource_update


def has_user_record_for_resource(resource_id, user):
    userobj = model.User.get(user)

    if not userobj: return False
    
    user_id = userobj.id
    org_ids = userobj.get_group_ids('organization')
    acls = model.Session.query(ResourceAcl).filter(
        ResourceAcl.resource_id == resource_id).all()

    for acl in acls:
        if acl.auth_id == user_id and acl.auth_type == 'user':
            return True
        if acl.auth_id in org_ids and acl.auth_type == 'org':
            return True

    return False


def has_user_permission_for_resource(resource_id, user, permission):
    userobj = model.User.get(user)
    
    if not userobj: return False
    
    user_id = userobj.id
    org_ids = userobj.get_group_ids('organization')
    permissions = ['read']
    permissions = permissions[permissions.index(permission):]
    acls = model.Session.query(ResourceAcl).filter(
        ResourceAcl.resource_id == resource_id).all()

    for acl in acls:
        if acl.auth_id == user_id and acl.auth_type == 'user' and acl.permission in permissions:
            return True
        if acl.auth_id in org_ids and acl.auth_type == 'org' and acl.permission in permissions:
            return True

    return False


def resource_acl_create(context, data_dict):
    '''Authorization check for creating a acl for a resource
    '''
    resource_id = data_dict.get('resource_id')
    return ckan_resource_update(context, {'id': resource_id})


def resource_acl_list(context, data_dict):
    '''Authorization check for getting a list of acls for a resource
    '''
    return resource_acl_create(context, data_dict)


def resource_list_for_user(context, data_dict):
    '''Authorization check for getting a list of resources for a user
    '''
    return {'success': True}


def resource_acl_show(context, data_dict):
    '''Authorization check for getting the information of the resource acl
    '''
    return resource_acl_create(context, data_dict)


def resource_acl_delete(context, data_dict):
    '''Authorization check for deleting a acl for a resource
    '''
    return resource_acl_create(context, data_dict)


def resource_acl_update(context, data_dict):
    '''Authorization check for updating a acl for a resource
    '''
    return resource_acl_create(context, data_dict)


def resource_acl_patch(context, data_dict):
    '''Authorization check for updating a acl for a resource
    '''
    return resource_acl_create(context, data_dict)


@p.toolkit.auth_allow_anonymous_access
def resource_show(context, data_dict):
    '''Override ckan's auth function
    '''
    resource_id = data_dict.get('id')
    user = context.get('user')

    if has_user_record_for_resource(resource_id, user):
        if has_user_permission_for_resource(resource_id, user, 'read'):
            return {'success': True}
        return {'success': False}

    resourceObj = get_resource_object(context, data_dict)
    packageObj = get_package_object(context, {'id': resourceObj.package_id})
    if packageObj.private:
        userobj = model.User.get(user)
        if userobj:
            org_ids = userobj.get_group_ids('organization')
            if packageObj.owner_org in org_ids:
                return {'success': True}
            return {'success': False}

    return ckan_package_show(context, {'id': resourceObj.package_id})

@p.toolkit.auth_allow_anonymous_access
def resource_view_show(context, data_dict):
    resourceObj = get_resource_object(context, data_dict)
    return resource_show(context, {'id': resourceObj.id})


@p.toolkit.auth_allow_anonymous_access
def resource_view_list(context, data_dict):
    resourceObj = model.Resource.get(data_dict['id'])
    return ckan_package_show(context, {'id': resourceObj.package_id})
