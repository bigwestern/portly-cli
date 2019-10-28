import argparse
import os
import sys
import re

from portlycli.portal.requests import generate_token
from portlycli.portal.requests import search_portal, list_items
from portlycli.portal.requests import get_items, upload_items, update_item
from portlycli.config import loader, find_config
from portlycli.files import item_to_file, get_download_path, to_csv, file_to_item
from portlycli.dependencies import find_dependencies, Graph, set_dependencies, create_setvars, relabeller, create_dep_id_var

from portlycli.project import Project

import portlycli.session as session
import portlycli.defaults as defaults

# FIXME: rmeove these deps to somewhere else
import json
from portlycli.models import PortalData

def template_command(args):
    print(defaults.CONFIG_FILE_TEMPLATE)

def init_command(args):

    project = Project()
    
    if project.has_project_file():
        print("A project file '%s' has already been configured here.  Delete it to use this command."
              % (project.project_path()))
    else:
        project_name = input('Project name:')
        project_author = input('Project author:')
        project_desc = input('Project description:')        
        project = Project(project_name, project_desc, project_author)
        project.create_project_file()
    
def info_command(args):
    print("Mr. Portly is taking direction from: '%s'" % (args.conf_path))
    print("He found the following portals configured:")
    for portal in session.config.portals():
        print("\t%s" % (portal))
        
def list_command(args):
    source_creds = session.config.creds[args.env]
    sourcePortal = generate_token(source_creds)
    items = list_items(sourcePortal, args.query)
    # only write out a subset of interesting columns from the listed items
    interesting = [t[:4] for t in items]
    if args.csvfile:
        print("Writing queried items to file: '%s'" % (args.csvfile))
        to_csv(args.csvfile, ('name','title','type','id'), interesting)
    return items

def download_command(args):
    source_creds = session.config.creds[args.env]
    source_portal = generate_token(source_creds)
    project = session.project
    
    # create directory
    #download_path = get_download_path(session.config.downloads, source_portal)
    download_path = get_download_path(session.config.downloads)
    print(download_path)
    os.makedirs(download_path, exist_ok=True)
    
    # Get a list of the content matching the query.
    content = search_portal(source_portal, query=args.query)

    # store all content locally
    portal_data = get_items(source_portal, content)
    
    # look for dependencies where I can
    if args.deps:
        print("you should look for dependencies")

        graph = retrieve_deps(source_portal, portal_data)
        relabeller = graph.create_relabeller()
        setvars = create_setvars(source_portal)
        
        for node in graph.postorder():
            item = node['portal_data']
            print(item.type)            
            files = item_to_file(download_path, item.title, item, relabeller, setvars)
            node['files'] = files
            
        # grab all the nodes in order of least amount of dependencies
        nodes = graph.postorder()

        # remember the ids used to remap the portal ids
        project.add_dependencies(nodes, source_portal, source_creds)

        # save the changes to the project
        project.create_project_file()
        
    else:
        print("Dont look for dependencies")        
        for item in portal_data:
            files = item_to_file(download_path, item.title, item)

    return portal_data


def copy_command(args):
    source_creds = session.config.creds[args.source]
    if source_creds:
        source_portal = generate_token(source_creds)
    else:
        return False
    
    destination_creds = session.config.creds[args.destination]    
    if destination_creds:
        destination_portal = generate_token(destination_creds)
    else:
        return False

    # Get a list of the content matching the query.
    content = search_portal(source_portal, query=args.query)
    portal_data = get_items(source_portal, content)

    upload_items(destination_portal, portal_data)

    return portal_data

def upload_command(args):
    destination_creds = session.config.creds[args.env]
    destination_portal = generate_token(destination_creds)

    project = session.project

    deps = project.derived_dependencies(destination_portal)

    remaps = project.service_remaps(destination_portal)

    for dep in deps:

        print(remaps)
        
        local_item = file_to_item(dep['files'])

        descripto = json.loads(local_item['desc_str'])
        title = descripto['title']
        thumbnail = descripto['thumbnail']
        
        portal_data = PortalData(descripto['name'],
                                 title,
                                 descripto['type'],
                                 descripto['id'],
                                 descripto,
                                 local_item['desc_str'],
                                 local_item['data_str'],
                                 local_item['thumbnail_str'])

        data_str = set_dependencies(destination_portal, portal_data, remaps)

        #FIXME: Need to find a way not to have to import relabeller
        #function in here.  set_dependencies function needs to take a
        #string and return a changed string
        desc_str = relabeller(remaps, portal_data.desc_str)
        
        dest_portal_data = PortalData(descripto['name'],
                                      title,
                                      descripto['type'],
                                      descripto['id'],
                                      descripto,
                                      desc_str,
                                      data_str,
                                      local_item['thumbnail_str'])
        
        wins, fails, length, portal_id = upload_items(destination_portal, [dest_portal_data])

        # add new portal_id to list of remaps
        if portal_id:
            remaps.append((create_dep_id_var(dep['depId']), portal_id))
        else:
            print("Error: upload to destination portal returned no id!")
            

def retrieve_deps(source_portal, portal_data, last_parent=None):

    graph = Graph()    
    
    for parent in portal_data:

        if last_parent is None:
            graph.add_root(parent)        
        else:
            graph.add_child(last_parent, parent)
                            
        deps = find_dependencies(parent)

        if deps is not None and len(deps) > 0:
            
            # create a query to get all the dependencies
            ids_query = " OR ".join(["id:{}".format(dep) for dep in deps])
        
            # Get a list of the content matching the query.
            deps_content = search_portal(source_portal, query=ids_query)

            # store all content locally
            children = get_items(source_portal, deps_content)
        
            print("item '%s' of type: '%s' has the following dependencies:" %
                  (parent.title, parent.type))
            
            for child in children:
                print("\tchild id:%s" % (child.title)) 
                graph.add_child(parent, child)

            if len(children) > 0:
                retrieve_deps(source_portal, children, parent)
                
        else:
            print("No dependencies for item '%s' of type: '%s'." % (parent.title, parent.type))    

    return graph
            

def deps_command(args):
    source_creds = session.config.creds[args.source]
    if source_creds:
        source_portal = generate_token(source_creds)
    else:
        return False
    
    # Get a list of the content matching the query.
    content = search_portal(source_portal, query=args.query)
    portal_data = get_items(source_portal, content)

    graph = retrieve_deps(source_portal, portal_data)    

    return graph

def origin_command(args):
    dest_creds = session.config.creds[args.env]
    dest_portal = generate_token(dest_creds)
    project = session.project

    if args.action == 'add':

        # add a destination origin
        project.add_origin(dest_portal, dest_creds)

        # save the changes
        project.create_project_file()

    if args.action == 'fetch':

        service_deps = project.all_dependencies(dest_portal)
        print(service_deps)

        dest_ids = []
        
        for dep in service_deps:
            dep_id, clauses = dep
            terms = ["{}:{}".format(k, v) for k, v in clauses.items()]
            query = " AND ".join(terms)
        
            # Get a list of the content matching the query.            
            content = search_portal(dest_portal, query=query)
            if len(content) == 1:
                dest_ids.append((dep_id, content[0]['id'], content[0]['url']))
            else:
                print("A UNIQUE match for '%s' could not be found in '%s'" % (query, dest_portal))

        # update the project file with the destination portal ids
        project.update_portal_ids(dest_portal, dest_ids)

        # save the changes
        project.create_project_file()

    if args.action == 'fix':
        
        webapp_origins = project.webapp_dependencies(dest_portal)
        for webapp_origin in webapp_origins:

            # make url
            if 'serviceUrl' in webapp_origin['portal']:
                m = re.match(r"(.*)(id=.*)", webapp_origin['portal']['serviceUrl'])            
                print(m.group(1))
                
                if m.group(1) and 'id' in webapp_origin['portal']:
                    item_url = "%sid=%s" % (m.group(1), webapp_origin['portal']['id']) 
                    
                    # update item
                    result = update_item(dest_portal,
                                         webapp_origin['portal']['id'],
                                         {'url': item_url, 'ownerFolder': ""})
                    
 
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-c','--config', dest='conf_path', default=None)
    
    subparsers = parser.add_subparsers()

    parser_template = subparsers.add_parser('template')
    parser_template.set_defaults(func=template_command,parser_name='template')
    
    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init_command,parser_name='init')
    
    parser_info = subparsers.add_parser('info')
    parser_info.set_defaults(func=info_command,parser_name='info')
    
    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('env')
    parser_list.add_argument('-q', '--query', dest='query', default=None)
    parser_list.add_argument('-o','--csvfile', nargs='?',
                        help='Write items out to csv file specified')    
    parser_list.set_defaults(func=list_command,parser_name='list')
    
    parser_download = subparsers.add_parser('download')
    parser_download.add_argument('env')
    parser_download.add_argument('-q', '--query', dest='query', default=None)
    parser_download.add_argument('-d', '--with-dependencies', dest='deps', action='store_true')    
    parser_download.set_defaults(func=download_command,parser_name='download')

    parser_copy = subparsers.add_parser('copy')
    parser_copy.add_argument('source')
    parser_copy.add_argument('destination')
    parser_copy.add_argument('-q', '--query', dest='query', default=None)
    parser_copy.set_defaults(func=copy_command,parser_name='copy')

    parser_deps = subparsers.add_parser('deps')
    parser_deps.add_argument('source')
    parser_deps.add_argument('-q', '--query', dest='query', default=None)
    parser_deps.set_defaults(func=deps_command,parser_name='deps')

    parser_origin = subparsers.add_parser('origin')
    parser_origin.add_argument('action')
    parser_origin.add_argument('env')    
    parser_origin.set_defaults(func=origin_command,parser_name='origin')

    parser_upload = subparsers.add_parser('upload')
    parser_upload.add_argument('env')    
    parser_upload.set_defaults(func=upload_command,parser_name='upload')

    args = parser.parse_args()

    # init parser shows the user an example config so don't bother
    # loading the config in this instance.
    if args.parser_name not in ['init', 'template']:
        config = loader(args)
        if not config:
            sys.exit()
            
        session.init(args, config)

        project = Project()
        
        if project.has_project_file():
            session.project = project
        else:
            # download feature needs a project file
            if args.parser_name in ['download', 'origin']:
                print("No project file found. Try 'portly init' first.")
                sys.exit()        

    args.func(args)

