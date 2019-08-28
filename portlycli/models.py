from collections import namedtuple

Credentials = namedtuple('Credentials', 'url user passwd')
AuthenticatedPortal = namedtuple('AuthenticatedPortal', 'url token')
