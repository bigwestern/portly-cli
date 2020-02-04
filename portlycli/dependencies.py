import json
from jsonpath_ng import jsonpath, parse
import networkx as nx

import uuid
from functools import partial

from portlycli.portal.types import is_service

def relabeller(remaps, data):
    if isinstance(data, (bytes, bytearray)):
        data = data.decode()

    for remap in remaps:
        old_id, new_id = remap
        data = data.replace(old_id, new_id)
        
    return data

def create_setvars(source_portal):
    base_url = source_portal.url.rstrip('/')
    return partial(relabeller, [(base_url,'{%baseUrl%}')])
    
def create_dep_id_var(dep_id):
    return '{{%{0}.id%}}'.format(dep_id)

def create_url_var(dep_id):
    return '{{%{0}.url%}}'.format(dep_id)

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
        return unknown_dependencies(portal_data)    


def set_webapp_dependencies(dest_portal, portal_data, remaps):
    webapp = to_json(portal_data)
    expression = parse('map.itemId')
    dep_ids = [match.value for match in expression.find(webapp)]

    if dep_ids:
       portal_ids = [portal_id for dep_id, portal_id in remaps if dep_ids[0] == dep_id]
       if portal_ids:
           webapp['map']['itemId'] = portal_ids[0]
           webapp['map']['appProxy']['mapItemId'] = portal_ids[0]
       else:
           print("No dep id matches that in the local webapp json.")
    else:
        print("No map.itemId in this webapp.  Has the schema changed for webapp json?")

    webapp['portalUrl'] = dest_portal.url
    webapp['httpProxy']['url'] = '/'.join([dest_portal.url.rstrip('/'), 'sharing/proxy'])
    webapp['map']['portalUrl'] = dest_portal.url
    webapp['appItemId'] = ""
    
    s = json.dumps(webapp, indent=2)
    print(s)
    return json.dumps(webapp)
        
def set_webmap_dependencies(dest_portal, portal_data, remaps):
    return relabeller(remaps, portal_data.data)
        
def unknown_set_dependencies(portal_data):
    print("No known way to set dependencies of type:'%s'" % (portal_data.type))
    return portal_data

def set_dependencies(dest_portal, portal_data, remaps):
    task = {
        'Web Mapping Application': set_webapp_dependencies,
        'Web Map': set_webmap_dependencies
    }
    try:
        return task[portal_data.type](dest_portal, portal_data, remaps)
    except KeyError:
        unknown_set_dependencies(portal_data)    

        
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
            print("item '%s' (dep id: '%s') with id %s already exists in graph." % (item.title, dep_id, item.id))
        else:
            dep_id = self.generate_id()
            print("adding new item: %s" % (item.id))
            self.graph.add_node(dep_id,
                                dep_id=dep_id,
                                files={'desc': None,'data': None,'thumbnail_url': None},
                                id=item.id,
                                item_type=item.type,
                                title=item.title,
                                portal_data=item)

        print(self.graph.node)
        return self.graph.node[dep_id]
    
    def add_child(self, parent_item, child_item):
        print("parent:")
        parent_node = self.add_item(parent_item)
        print("child:")        
        child_node = self.add_item(child_item)
        self.graph.add_edge(parent_node['dep_id'],child_node['dep_id'])
        return self.graph
        
    def add_root(self, item):
        dep_id = self.generate_id()
        print("add root '%s'" % (dep_id))
        self.graph.add_node(dep_id,
                            dep_id=dep_id,
                            files={'desc': None,'data': None,'thumbnail_url': None},                            
                            id=item.id,
                            item_type=item.type,
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
            print("'%s' '%s'" % (self.graph.node[dep_id]['item_type'], self.graph.node[dep_id]['title']))

            # only change files where the item has parents.  ie. other
            # items that depend on this item.
            if self.has_parents(dep_id):
                remaps.append((self.graph.node[dep_id]['id'], create_dep_id_var(dep_id)))

                # service urls will also have to change in some items
                # so revise the file in a way that this can be done.
                if is_service(self.graph.node[dep_id]['item_type']):
                    old_url = self.graph.node[dep_id]['portal_data'].desc['url']
                    new_url = create_url_var(dep_id)
                    remaps.append((old_url, new_url))
                    
        return remaps
            
    def create_relabeller(self):
        remaps = self.create_remapping_list()
        return partial(relabeller, remaps)
