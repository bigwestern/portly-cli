SERVICE_TYPES = ['Feature Service']

def is_service(portal_type):
    return portal_type in SERVICE_TYPES

def is_not_service(portal_type):
    not is_service(portal_type)

def is_webapp(portal_type):
    return portal_type in ['Web Mapping Application']
