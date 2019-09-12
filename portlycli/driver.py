import argparse
import os
import sys

from portlycli.portal import generate_token
from portlycli.portal import search_portal, list_items
from portlycli.portal import get_items, upload_items
from portlycli.config import loader, find_config
from portlycli.files import item_to_file, get_download_path, to_csv
from portlycli.dependencies import find_dependencies

import portlycli.session as session
import portlycli.defaults as defaults

def init_command(args):
    print(defaults.CONFIG_FILE_TEMPLATE)

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
    
    # create directory
    download_path = get_download_path(session.config.downloads, source_portal)
    os.makedirs(download_path, exist_ok=True)
    
    # Get a list of the content matching the query.
    content = search_portal(source_portal, query=args.query)

    # store all content locally
    portal_data = get_items(source_portal, content)  
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


def deps_command(args):
    source_creds = session.config.creds[args.source]
    if source_creds:
        source_portal = generate_token(source_creds)
    else:
        return False
    
    # Get a list of the content matching the query.
    content = search_portal(source_portal, query=args.query)
    portal_data = get_items(source_portal, content)
    for pd in portal_data:
        deps = find_dependencies(pd)
        print("item '%s' of type: '%s' has the following dependencies:" % (pd.title, pd.type))
        for dep in deps:
            print("\tid:%s" % (dep)) 

    return portal_data

    
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-c','--config', dest='conf_path', default=None)
    
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init_command)
    
    parser_info = subparsers.add_parser('info')
    parser_info.set_defaults(func=info_command)
    
    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('env')
    parser_list.add_argument('-q', '--query', dest='query', default=None)
    parser_list.add_argument('-o','--csvfile', nargs='?',
                        help='Write items out to csv file specified')    
    parser_list.set_defaults(func=list_command)
    
    parser_download = subparsers.add_parser('download')
    parser_download.add_argument('env')
    parser_download.add_argument('-q', '--query', dest='query', default=None)
    parser_download.set_defaults(func=download_command)

    parser_copy = subparsers.add_parser('copy')
    parser_copy.add_argument('source')
    parser_copy.add_argument('destination')
    parser_copy.add_argument('-q', '--query', dest='query', default=None)
    parser_copy.set_defaults(func=copy_command)

    parser_deps = subparsers.add_parser('deps')
    parser_deps.add_argument('source')
    parser_deps.add_argument('-q', '--query', dest='query', default=None)
    parser_deps.set_defaults(func=deps_command)
    
    args = parser.parse_args()

    config = loader(args)
    if not config:
        sys.exit()
        
    session.init(args, config)
    
    args.func(args)

