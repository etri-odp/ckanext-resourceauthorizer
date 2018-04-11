import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.resourceauthorizer.helpers as resourceauthorizer_helpers
import ckan.authz as authz
from ckan.plugins.toolkit import get_action
from ckan.lib.plugins import DefaultPermissionLabels
from ckanext.resourceauthorizer.logic import action
from ckanext.resourceauthorizer.logic import auth


class ResourceAuthorizerPlugin(plugins.SingletonPlugin,
                               DefaultPermissionLabels):

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IPermissionLabels)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'resourceauthorizer')

    def get_helpers(self):
        '''Register the linked_organization() function above as a template
        helper function.
        '''
        return {
            'linked_organization':
            resourceauthorizer_helpers.linked_organization
        }

    # IActions

    def get_actions(self):
        return {
            'resource_list_for_user': action.resource_list_for_user,
            'resource_acl_list': action.resource_acl_list,
            'resource_acl_show': action.resource_acl_show,
            'resource_acl_create': action.resource_acl_create,
            'resource_acl_delete': action.resource_acl_delete,
            'resource_acl_update': action.resource_acl_update,
            'resource_acl_patch': action.resource_acl_patch,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'resource_list_for_user': auth.resource_list_for_user,
            'resource_acl_list': auth.resource_acl_list,
            'resource_acl_show': auth.resource_acl_show,
            'resource_acl_create': auth.resource_acl_create,
            'resource_acl_delete': auth.resource_acl_delete,
            'resource_acl_update': auth.resource_acl_update,
            'resource_acl_patch': auth.resource_acl_patch,
            'resource_show': auth.resource_show,
            'resource_view_show': auth.resource_view_show,
            'resource_view_list': auth.resource_view_list
        }

    # IRoutes

    def before_map(self, m):
        m.connect(
            'resource_acl',
            '/dataset/{dataset_id}/resource/{resource_id}/acl',
            controller=
            'ckanext.resourceauthorizer.controller:ResourceAuthorizerController',
            action='resource_acl',
            ckan_icon='users')
        m.connect(
            'resource_acl_new',
            '/dataset/{dataset_id}/resource/{resource_id}/acl_new',
            controller=
            'ckanext.resourceauthorizer.controller:ResourceAuthorizerController',
            action='resource_acl_new')
        m.connect(
            'resource_acl_delete',
            '/dataset/{dataset_id}/resource/{resource_id}/acl/{id}',
            controller=
            'ckanext.resourceauthorizer.controller:ResourceAuthorizerController',
            action='resource_acl_delete')
        return m

    # IPackageController

    def after_show(item, context, data_dict):
        resources = []
        for resource_dict in data_dict['resources']:
            logic_authorization = authz.is_authorized('resource_show', context,
                                                      resource_dict)
            if logic_authorization['success']:
                resources.append(resource_dict)
        data_dict['resources'] = resources
        return

    # IPermissionLabels

    def get_dataset_labels(self, dataset_obj):
        labels = super(ResourceAuthorizerPlugin,
                       self).get_dataset_labels(dataset_obj)
        labels.extend(u'acl-%s' % o.id for o in dataset_obj.resources)
        return labels

    def get_user_dataset_labels(self, user_obj):
        labels = super(ResourceAuthorizerPlugin,
                       self).get_user_dataset_labels(user_obj)
        if user_obj:
            resources = get_action(u'resource_list_for_user')()
            labels.extend(u'acl-%s' % o[u'resource_id'] for o in resources)
        return labels
