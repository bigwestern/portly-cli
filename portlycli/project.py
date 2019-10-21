import os
import json
import portlycli.defaults as defaults
import copy

def create_deps_list(nodes, source_portal, source_creds):
    deps = []

    for node in nodes:

        # {
        #    matchStrategy: { owner: value, type: value, title: value }
        #    depId: value
        #    source: {
        #      url: value,
        #      portalId: value
        # }

        portal_data = node['portal_data']

        dep = dict()
        dep['depId'] = node['dep_id']

        dep['origins'] = []

        origin = dict()

        origin['type'] = 'source'
        origin['portal'] = dict()
        origin['portal']['url'] = source_portal.url
        origin['portal']['id'] = node['id']
        
        origin['matchStrategy'] = dict()
        origin['matchStrategy']['owner'] = source_creds.user
        origin['matchStrategy']['title'] = portal_data.title
        origin['matchStrategy']['type'] = portal_data.type

        dep['origins'].append(origin)
        
        deps.append(dep)
        
    return deps
    

class Project(object):
    name = None
    description = None
    author = None
    dependencies = []
    
    def __init__(self, name=None, desc=None, author=None):
        self.dependencies = []
        
        if self.has_project_file():
            self.load_project_file()
        else:    
            self.name = name
            self.description = desc
            self.author = author
            
    def project_path(self):
        cwd = os.getcwd()
        return os.path.abspath(os.path.join(cwd, defaults.PROJECT_FILE_NAME))

    def has_project_file(self):
        project_path = self.project_path()
        return os.path.isfile(project_path) 

    def load_project_file(self):
        project_path = self.project_path()
        print("Loading project config file: '%s'" % (project_path))        
        with open(project_path) as json_data:
            d = json.load(json_data)
            json_data.close()
            self.__dict__ = d
            return d
    
    def create_project_file(self):
        project_path = self.project_path()
        # print(jsonpickle.encode(self, unpicklable=False))
        print("create_project_file")
        with open(project_path, 'w', encoding='utf-8') as f:

            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)
            f.close()
            print("Created a project config file: '%s'" % (project_path))
        
        return project_path

    def add_dependencies(self, nodes, source_portal, source_creds):
        self.dependencies = create_deps_list(nodes, source_portal, source_creds)
        print(self.dependencies)
        
    def add_origin(self, dest_portal, dest_creds):

        for dep in self.dependencies:
            source_origins = [o for o in dep['origins'] if o['type'] == 'source']
            if len(source_origins) > 0:
                source_origin = source_origins.pop(0)
                dest_origin = copy.deepcopy(source_origin)
                dest_origin['type'] = 'destination'
                dest_origin['portal']['url'] = dest_portal.url
                dest_origin['portal']['id'] = None
                dest_origin['matchStrategy']['owner'] = dest_creds.user
                dep['origins'].append(dest_origin)
            else:
                print("No source origins for dependency.  Have you downloaded anything yet?")

        print(self.dependencies)
        

    def service_dependencies(self, dest_portal):
        service_deps = []
        for dep in self.dependencies:
            dest_origins = [o for o in dep['origins'] if o['portal']['url'] == dest_portal.url]
            for dest_origin in dest_origins:
                if dest_origin['matchStrategy']['type'] in ['Feature Service']:
                    service_dep = (dep['depId'], dest_origin['matchStrategy'])
                    service_deps.append(service_dep)
                    
        return service_deps
                
                
