import argparse
import os
import sys

from portlycli.portal import generate_token
from portlycli.portal import search_portal, list_items
from portlycli.portal import get_items, upload_items
from portlycli.config import loader, find_config
from portlycli.files import item_to_file, get_download_path, to_csv
from portlycli.dependencies import find_dependencies, Graph

from portlycli.project import Project

import portlycli.session as session
import portlycli.defaults as defaults

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
        
        for item in graph.traversal():
            print(item.type)
            files = item_to_file(download_path, item.title, item, relabeller)

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
                print("\tid:%s" % (child.title)) 
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
            print("No project file found. Try 'portly init' first.")
            sys.exit()        

    args.func(args)

