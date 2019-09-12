import json
from jsonpath_ng import jsonpath, parse

def to_json(portal_data):
    try:
        jdict = json.loads(portal_data.data)
    except ValueError as e:
        print(e)
        print("Can't beautify json for item %s" % (portal_data.id))
    return jdict

def webapp_dependencies(portal_data):
    webapp = to_json(portal_data)
    expression = parse('map.itemId')
    return [match.value for match in expression.find(webapp)]
    

def webmap_dependencies(portal_data):
    webapp = to_json(portal_data)
    operational_expression = parse('operationalLayers[*].itemId')
    operational_ids = [match.value for match in operational_expression.find(webapp)]
    basemap_expression = parse('baseMap.baseMapLayers[*].itemId')
    basemap_ids = [match.value for match in basemap_expression.find(webapp)]
    return operational_ids + basemap_ids

def unknown_dependencies(portal_data):
    print("Mr. Portly knows nothing about the dependencies of type:'%s'" % (portal_data.type))
    return []

def find_dependencies(portal_data):
    task = {
        'Web Mapping Application': webapp_dependencies,
        'Web Map': webmap_dependencies
    }
    try:
        return task[portal_data.type](portal_data)
    except KeyError:
        unknown_dependencies(portal_data)    
