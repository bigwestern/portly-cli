import os
import json
import portlycli.defaults as defaults

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
        
        dep['source'] = dict()
        dep['source']['url'] = source_portal.url
        dep['source']['portalId'] = node['id']
        
        dep['matchStrategy'] = dict()
        dep['matchStrategy']['owner'] = source_creds.user
        dep['matchStrategy']['title'] = portal_data.title
        dep['matchStrategy']['type'] = portal_data.type
        
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
        
