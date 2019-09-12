from collections import namedtuple

Credentials = namedtuple('Credentials', 'url user passwd')
AuthenticatedPortal = namedtuple('AuthenticatedPortal', 'url token')

PortalItem = namedtuple('PortalItem', 'name title type id desc desc_str')
PortalData = namedtuple('PortalData', 'name title type id desc desc_str data thumbnail_url')
