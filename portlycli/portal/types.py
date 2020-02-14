SERVICE_TYPES = ['Feature Service','Map Service','Vector Tile Service']
ITEM_TYPES = ['Web Map', 'Web Mapping Application']

def is_service(portal_type):
    return portal_type in SERVICE_TYPES

def is_not_service(portal_type):
    not is_service(portal_type)

def is_webapp(portal_type):
    return portal_type in ['Web Mapping Application']

def is_valid_item(portal_type):
    return True if portal_type in ITEM_TYPES else False
