from ckan.plugins.toolkit import Invalid


def auth_type_validator(value):
    if not value in ['user', 'org']:
        raise Invalid('Invalid auth_type %s' % (value))
    return value


def permission_validator(value):
    if not value in ['none', 'read']:
        raise Invalid('Invalid permission %s' % (value))
    return value
