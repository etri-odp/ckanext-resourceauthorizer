from ckan.plugins.toolkit import (request, BaseController, abort, render, c, h,
                                  _)
from ckan.logic import (ValidationError, NotAuthorized, NotFound, check_access,
                        get_action, clean_dict, tuplize_dict, parse_params)
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model as model


class ResourceAuthorizerController(BaseController):

    def _redirect_to_this_controller(self, *args, **kw):
        kw['controller'] = request.environ['pylons.routes_dict']['controller']
        return h.redirect_to(*args, **kw)

    def resource_acl(self, dataset_id, resource_id):
        try:
            c.pkg_dict = get_action('package_show')(None, {'id': dataset_id})
            c.resource = get_action('resource_show')(None, {'id': resource_id})
            rec = get_action('resource_acl_list')(None, {
                'resource_id': resource_id,
                'limit': 0
            })
        except NotAuthorized:
            abort(403)
        except NotFound:
            abort(404)
        return render(
            'resource-authorizer/acl.html',
            extra_vars={
                'acls': rec,
                'dataset_id': dataset_id,
                'resource_id': resource_id
            })

    def resource_acl_new(self, dataset_id, resource_id):
        context = {'model': model, 'session': model.Session, 'user': c.user}
        try:
            check_access('resource_acl_create', context, {
                'resource_id': resource_id
            })
        except NotAuthorized:
            abort(403, _('Unauthorized to create resource acl %s') % '')
        try:
            c.pkg_dict = get_action('package_show')(None, {'id': dataset_id})
            c.resource = get_action('resource_show')(None, {'id': resource_id})
            c.permissions = [{
                'text': u'None',
                'value': 'none'
            }, {
                'text': u'Read',
                'value': 'read'
            }]
            if request.method == 'POST':
                data_dict = clean_dict(
                    dict_fns.unflatten(
                        tuplize_dict(parse_params(request.params))))
                acl = data_dict.get('id')
                if acl is None:
                    data = {
                        'resource_id': resource_id,
                        'permission': data_dict['permission']
                    }
                    if data_dict['organization']:
                        group = model.Group.get(data_dict['organization'])
                        if not group:
                            message = _(u'Organization {org} does not exist.').format(
                                org=data_dict['organization'])
                            raise ValidationError(
                                {
                                    'message': message
                                }, error_summary=message)
                        data['auth_type'] = 'org'
                        data['auth_id'] = group.id
                    elif data_dict['username']:
                        user = model.User.get(data_dict['username'])
                        if not user:
                            message = _(u'User {username} does not exist.').format(
                                username=data_dict['username'])
                            raise ValidationError(
                                {
                                    'message': message
                                }, error_summary=message)
                        data['auth_type'] = 'user'
                        data['auth_id'] = user.id
                    get_action('resource_acl_create')(None, data)
                else:
                    data = {'id': acl, 'permission': data_dict['permission']}
                    get_action('resource_acl_patch')(None, data)
                self._redirect_to_this_controller(
                    action='resource_acl',
                    dataset_id=dataset_id,
                    resource_id=resource_id)
            else:
                acl = request.params.get('id')
                if acl:
                    c.acl_dict = get_action('resource_acl_show')(context, {
                        'id': acl
                    })
                    if c.acl_dict['auth_type'] == 'user':
                        c.auth = get_action('user_show')(
                            context, {
                                'id': c.acl_dict['auth_id']
                            })
                    else:
                        c.auth = get_action('organization_show')(
                            context, {
                                'id': c.acl_dict['auth_id']
                            })
                    c.acl_permission = c.acl_dict['permission']
                else:
                    c.acl_permission = 'None'
        except NotAuthorized:
            abort(403)
        except NotFound:
            abort(404)
        except ValidationError, e:
            h.flash_error(e.error_summary)
        return render(
            'resource-authorizer/acl_new.html',
            extra_vars={
                'dataset_id': dataset_id,
                'resource_id': resource_id
            })

    def resource_acl_delete(self, id, dataset_id, resource_id):
        context = {'model': model, 'session': model.Session, 'user': c.user}
        try:
            if request.method == 'POST':
                get_action('resource_acl_delete')(context, {'id': id})
                h.flash_notice(_('Resource ACL has been deleted.'))
                self._redirect_to_this_controller(
                    action='resource_acl',
                    dataset_id=dataset_id,
                    resource_id=resource_id)
        except NotAuthorized:
            abort(403)
        except NotFound:
            abort(404)
