import datetime

from ckan.logic import side_effect_free, check_access, get_or_bust
from ckan.logic import NotFound, ValidationError

from ckan.lib.navl.dictization_functions import validate

from ckanext.resourceauthorizer.logic.schema import resource_acl_create_schema
from ckanext.resourceauthorizer.logic.schema import resource_acl_update_schema
from ckanext.resourceauthorizer.logic.schema import resource_acl_patch_schema

from ckanext.resourceauthorizer.model import ResourceAcl


@side_effect_free
def resource_acl_list(context, data_dict):
    '''Return the list of acls for a particular resource

    :param resource_id: the id of the resource
    :param limit: the number of returning results
    :param offset: the offset to start returning results from
    '''
    check_access('resource_acl_list', context, data_dict)

    resource_id = data_dict.get('resource_id')
    limit = data_dict.get('limit')
    offset = data_dict.get('offset')
    session = context['session']
    query = session.query(ResourceAcl)

    if resource_id:
        query = query.filter(ResourceAcl.resource_id == resource_id)
    if limit:
        query = query.limit(int(limit))
    if offset:
        query = query.offset(int(offset))

    acls = query.all()

    return [acl.as_dict() for acl in acls]


@side_effect_free
def resource_list_for_user(context, data_dict):
    '''Return the resources that the user has a given permission for based on resource acl.

    :param user_id: the id of the resource
    '''
    check_access('resource_list_for_user', context, data_dict)

    user = context['user']
    model = context['model']
    userobj = model.User.get(user)

    if userobj:
        user_id = userobj.id
        user_acls = model.Session.query(ResourceAcl).filter(
            ResourceAcl.auth_id == user_id).all()
        user_acl = [acl.as_dict() for acl in user_acls]

        org_ids = userobj.get_group_ids('organization')
        org_acls = model.Session.query(ResourceAcl).filter(
            ResourceAcl.auth_id.in_(org_ids),
            ResourceAcl.permission != 'none').all()

        resources = []
        none_resources = []
        for user_acl in user_acls:
            if user_acl.permission != 'none':
                resources.append(user_acl)
            else:
                none_resources.append(user_acl.resource_id)

        for org_acl in org_acls:
            if org_acl.resource_id not in none_resources:
                resources.append(org_acl)

        return [acl.as_dict() for acl in resources]

    return []


@side_effect_free
def resource_acl_show(context, data_dict):
    '''Return the information of the resource acl

    :param id: the id of the resource acl
    '''
    reference = get_or_bust(data_dict, 'id')
    acl = ResourceAcl.get(reference)

    if not acl: raise NotFound('acl <{id}> was not found.'.format(id=reference))

    data_dict['resource_id'] = acl.resource_id
    check_access('resource_acl_show', context, data_dict)

    return acl.as_dict()


def resource_acl_create(context, data_dict):
    '''Append a new resource acl to the list of resource acls

    :param resource_id: the id of the resource
    :param auth_type: user, org
    :param auth_id: the id of user or organization
    :param permission: none, read
    '''
    check_access('resource_acl_create', context, data_dict)

    data, errors = validate(data_dict, resource_acl_create_schema(), context)

    if errors:
        raise ValidationError(errors)

    acl = ResourceAcl(
        resource_id=data.get('resource_id'),
        auth_type=data.get('auth_type'),
        auth_id=data.get('auth_id'),
        permission=data.get('permission'),
        creator_user_id=context.get('user'))

    acl.save()

    return acl.as_dict()


def resource_acl_delete(context, data_dict):
    '''Delete the resource acl from the list of resource acls

    :param id: the id of the resource acl
    '''
    reference = get_or_bust(data_dict, 'id')
    acl = ResourceAcl.get(reference)

    if not acl: raise NotFound('acl <{id}> was not found.'.format(id=reference))

    data_dict['resource_id'] = acl.resource_id

    check_access('resource_acl_delete', context, data_dict)

    acl.delete()
    acl.commit()


def resource_acl_update(context, data_dict):
    '''Update the resource acl

    :param id: the id of the resource acl
    :param auth_type: user, org
    :param auth_id: the id of user or organization
    :param permission: none, read
    '''
    reference = get_or_bust(data_dict, 'id')
    acl = ResourceAcl.get(reference)

    if not acl: raise NotFound('acl <{id}> was not found.'.format(id=reference))

    data_dict['resource_id'] = acl.resource_id

    check_access('resource_acl_update', context, data_dict)

    data, errors = validate(data_dict, resource_acl_update_schema(), context)

    if errors:
        raise ValidationError(errors)

    acl.auth_type = data.get('auth_type')
    acl.auth_id = data.get('auth_id')
    acl.permission = data.get('permission')
    acl.last_modified = datetime.datetime.utcnow()
    acl.modifier_user_id = context.get('user')

    acl.commit()

    return acl.as_dict()


def resource_acl_patch(context, data_dict):
    '''Patch the resource acl

    :param id: the id of the resource acl
    :param auth_type: user, org
    :param auth_id: the id of user or organization
    :param permission: none, read
    '''
    reference = get_or_bust(data_dict, 'id')
    acl = ResourceAcl.get(reference)

    if not acl: raise NotFound('acl <{id}> was not found.'.format(id=reference))

    data_dict['resource_id'] = acl.resource_id

    check_access('resource_acl_patch', context, data_dict)

    data, errors = validate(data_dict, resource_acl_patch_schema(), context)

    if errors:
        raise ValidationError(errors)

    acl.auth_type = data.get('auth_type', acl.auth_type)
    acl.auth_id = data.get('auth_id', acl.auth_id)
    acl.permission = data.get('permission', acl.permission)
    acl.last_modified = datetime.datetime.utcnow()
    acl.modifier_user_id = context.get('user')

    acl.commit()

    return acl.as_dict()
