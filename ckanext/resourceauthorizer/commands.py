#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from ckan import model
from ckan.logic import get_action

from ckan.lib.cli import CkanCommand


class ResourceAuthorizerCommand(CkanCommand):
    '''Resource authorizer commands

    Usage:

      resourceauthorizer init-db
        - Create the resource_acl table in the database

      resourceauthorizer list-acl [{resource-id}]
        - lists resource acls

      resourceauthorizer show-acl {id}
        - shows information of the resource acl

      resourceauthorizer create-acl {resource-id} {auth-type} {auth-id} {permission}
        - creates a new resource acl

      resourceauthorizer delete-acl {id}
        - deletes the resource acl

      resourceauthorizer update-acl {id} {auth-type} {auth-id} {permission}
        - updates the resource acl
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 5
    min_args = 0

    def __init__(self, name):
        super(ResourceAuthorizerCommand, self).__init__(name)

    def command(self):
        self._load_config()

        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(0)

        context = {
            'model': model,
            'session': model.Session,
            'ignore_auth': True
        }
        self.admin_user = get_action('get_site_user')(context, {})

        print ''

        cmd = self.args[0]

        if cmd == 'initdb':
            self.setup_db()
        elif cmd == 'list-acl':
            self.list_acl()
        elif cmd == 'show-acl':
            self.show_acl()
        elif cmd == 'create-acl':
            self.create_acl()
        elif cmd == 'delete-acl':
            self.delete_acl()
        elif cmd == 'update-acl':
            self.update_acl()
        else:
            print 'command %s not recognized' % cmd

    def setup_db(self):
        from ckanext.resourceauthorizer.model import setup as db_setup
        db_setup()
        print 'resource_acl table created'
        print ''

    def list_acl(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': self.admin_user['name'],
            'ignore_auth': True,
        }
        data_dict = {}
        if 2 <= len(self.args):
            data_dict['resource_id'] = unicode(self.args[1])
        acls = get_action('resource_acl_list')(context, data_dict)
        for acl in acls:
            self.print_acl(acl)

    def show_acl(self):
        if len(self.args) != 2:
            print 'Please check arguments'
            sys.exit(1)
        context = {
            'model': model,
            'session': model.Session,
            'user': self.admin_user['name'],
            'ignore_auth': True,
        }
        data_dict = {}
        data_dict['id'] = unicode(self.args[1])
        acl = get_action('resource_acl_show')(context, data_dict)
        self.print_acl(acl)

    def create_acl(self):
        if len(self.args) != 5:
            print 'Please check arguments'
            sys.exit(1)
        context = {
            'model': model,
            'session': model.Session,
            'user': self.admin_user['name'],
            'ignore_auth': True,
        }
        data_dict = {}
        data_dict['resource_id'] = unicode(self.args[1])
        data_dict['auth_type'] = unicode(self.args[2])
        data_dict['auth_id'] = unicode(self.args[3])
        data_dict['permission'] = unicode(self.args[4])
        acl = get_action('resource_acl_create')(context, data_dict)
        self.print_acl(acl)

    def delete_acl(self):
        if len(self.args) != 2:
            print 'Please check arguments'
            sys.exit(1)
        context = {
            'model': model,
            'session': model.Session,
            'user': self.admin_user['name'],
            'ignore_auth': True,
        }
        data_dict = {}
        data_dict['id'] = unicode(self.args[1])
        get_action('resource_acl_delete')(context, data_dict)
        print 'acl <%s> was deleted.' % data_dict['id']
        print ''

    def update_acl(self):
        if len(self.args) != 5:
            print 'Please check arguments'
            sys.exit(1)
        context = {
            'model': model,
            'session': model.Session,
            'user': self.admin_user['name'],
            'ignore_auth': True,
        }
        data_dict = {}
        data_dict['id'] = unicode(self.args[1])
        data_dict['auth_type'] = unicode(self.args[2])
        data_dict['auth_id'] = unicode(self.args[3])
        data_dict['permission'] = unicode(self.args[4])
        acl = get_action('resource_acl_update')(context, data_dict)
        self.print_acl(acl)

    def print_acl(self, acl):
        print '              id: %s' % acl.get('id')
        print '     resource id: %s' % acl.get('resource_id')
        print '       auth type: %s' % acl.get('auth_type')
        print '         auth id: %s' % acl.get('auth_id')
        print '      permission: %s' % acl.get('permission')
        print '         created: %s' % acl.get('created')
        print '   last modified: %s' % acl.get('last_modified')
        print ' creator user id: %s' % acl.get('creator_user_id')
        print 'modifier user id: %s' % acl.get('modifier_user_id')
        print ''
