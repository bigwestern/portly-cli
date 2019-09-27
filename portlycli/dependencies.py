import json
from jsonpath_ng import jsonpath, parse
import networkx as nx

import uuid
from functools import partial

def relabeller(remaps, data):
    if isinstance(data, (bytes, bytearray)):
        data = data.decode()

    for remap in remaps:
        portal_id, dep_id = remap
        data = data.replace(portal_id, dep_id)
        
    return data

def to_json(portal_data):
    try:
        jdict = json.loads(portal_data.data)
        return jdict
    except ValueError as e:
        print(e)
        print("Can't beautify json for item %s" % (portal_data.id))
        return dict()

def webapp_dependencies(portal_data):
    if not portal_data.data:
        print()
        print("Item %s references an externally hosted webapp at %s" %
              (portal_data.id,portal_data.desc['url']))
        print("\t  No JSON data available to check dependencies.")
        return []
        
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

    def generate_id(self):
        return str(uuid.uuid4())[:8]
    
    def find_node_by_portal_id(self, id):
        for n in self.graph.nodes(data=True):
            dep_id, data = n
            if 'id' in data:
                if data['id'] == id:
                    return dep_id
        return None

    def add_item(self, item):
        dep_id = self.find_node_by_portal_id(item.id)
        if dep_id:
            print("item '%s' with id %s already exists in graph." % (item.title, item.id))
        else:
            dep_id = self.generate_id()
            print("adding new item: %s" % (item.id))
            self.graph.add_node(dep_id,
                                dep_id=dep_id,
                                id=item.id,
                                type=item.type,
                                title=item.title,
                                portal_data=item)
            
        return self.graph.node[dep_id]
    
    def add_child(self, parent_item, child_item):
        parent_node = self.add_item(parent_item)
        child_node = self.add_item(child_item)
        self.graph.add_edge(parent_node['dep_id'],child_node['dep_id'])
        return self.graph
        
    def add_root(self, item):
        dep_id = self.generate_id()        
        self.graph.add_node(dep_id,
                            dep_id=dep_id,
                            id=item.id,
                            type=item.type,
                            title=item.title,
                            portal_data=item)


    def has_parents(self, dep_id):
        parents = self.graph.predecessors(dep_id)
        return len(list(parents)) > 0
        
    def parents(self, dep_id):
        parents = self.graph.predecessors(dep_id)
        return list(parents)
        
    def postorder(self):
        return [self.graph.node[id] for id in list(nx.dfs_postorder_nodes(self.graph))]
    
    def traversal(self):
        return [self.graph.node[id]['portal_data'] for id in list(nx.dfs_postorder_nodes(self.graph))]

    def create_remapping_list(self):
        remaps = []
        for dep_id in nx.dfs_postorder_nodes(self.graph):
            print("'%s' '%s'" % (self.graph.node[dep_id]['type'], self.graph.node[dep_id]['title']))
            if self.has_parents(dep_id):
                remaps.append((self.graph.node[dep_id]['id'],dep_id))
        return remaps
            
    def create_relabeller(self):
        remaps = self.create_remapping_list()
        print(remaps)
        return partial(relabeller, remaps)
