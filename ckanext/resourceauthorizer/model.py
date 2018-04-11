import datetime
import uuid

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types

import ckan.model as model

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper
from ckan.model.types import make_uuid


class ResourceAcl(DomainObject):

    @classmethod
    def get(cls, reference):
        return model.Session.query(cls).filter(cls.id == reference).first()

    @classmethod
    def has(cls, resource_id):
        return model.Session.query(cls).filter(
            cls.resource_id == resource_id).count()


resource_acl_table = Table(
    'resource_acl',
    metadata,
    Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
    Column('resource_id', types.UnicodeText),
    Column('auth_type', types.UnicodeText),
    Column('auth_id', types.UnicodeText),
    Column('permission', types.UnicodeText),
    Column('created', types.DateTime, default=datetime.datetime.utcnow),
    Column('last_modified', types.DateTime, default=datetime.datetime.utcnow),
    Column('creator_user_id', types.UnicodeText, default=u''),
    Column('modifier_user_id', types.UnicodeText, default=u''),
)

mapper(ResourceAcl, resource_acl_table)


def setup():
    resource_acl_table.create(checkfirst=True)
