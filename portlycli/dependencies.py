import json
from jsonpath_ng import jsonpath, parse
import networkx as nx

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
    print("Mr. Portly does not know how to find the dependencies of type:'%s'" % (portal_data.type))
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


class Graph(object):
    
    graph = nx.DiGraph()

    def add_item(self, item):
        exists = self.graph[item.id]
        if not exists:
            self.graph.add_node(item.id)
        else:
            print("item '%s' with id %s already exists in graph." % (item.title, item.id))
        return self.graph[item.id]
    
    def add_child(self, parent_item, child_item):
        parent_node_id = self.add_item(parent_item)
        child_node_id = self.add_item(child_item)
        self.graph.add_edge(parent_node_id,child_node_id)
        return self.graph
        
    def add_root(self, portal_item):
        self.graph.add_node(portal_item.id)

