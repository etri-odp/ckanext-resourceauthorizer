# -*- coding: utf-8 -*-

from webhelpers.html import tags
import ckan.lib.helpers as helpers
from routes import url_for


def linked_organization(org):
    organization = helpers.get_organization(org)
    if organization:
        return tags.literal(u'{icon} {link}'.format(
            icon=helpers.icon_html(
                organization['image_display_url'], alt='', inline=False),
            link=tags.link_to(organization['title'],
                              url_for(
                                  controller='organization',
                                  action='read',
                                  id=organization['name']))))
    return 'Not Existed'
