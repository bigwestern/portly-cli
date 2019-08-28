import argparse
import os
import sys

from portlycli.portal import generate_token
from portlycli.portal import search_portal, list_items
from portlycli.portal import get_items
from portlycli.config import loader, find_config
from portlycli.files import item_to_file, get_download_path

import portlycli.session as session

def info_command(args):
    print("Mr. Portly is taking direction from: '%s'" % (args.conf_path))
    print("He found the following portals configured:")
    for portal in session.config.portals():
        print("\t%s" % (portal))
        
def list_command(args):
    source_creds = session.config.creds[args.env]
    sourcePortal = generate_token(source_creds)
    items = list_items(sourcePortal, args.query)
    if args.csvfile:
        print("Writing queried items to file: '%s'" % (args.csvfile))
        to_csv(args.csvfile, ('name','title','type', 'id'), items)
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
        item_id, title, desc, data, thumbnail = item
        files = item_to_file(download_path, title, item)
        
    return portal_data


def copy_command(args):
    source_creds = session.config.creds[args.source]
    if source_creds:
        sourcePortal = generate_token(source_creds)
    else:
        return False
    
    destination_creds = session.config.creds[args.destination]    
    if destination_creds:
        destinationPortal = generate_token(destination_creds)
    else:
        return False

    # Get a list of the content matching the query.
    content = search_portal(sourcePortal, query=args.query)
    portalData = get_items(sourcePortal, content)
    upload(destinationPortal, portalData)

    return portalData

    
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-c','--config', dest='conf_path', default=None)
    
    subparsers = parser.add_subparsers()

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

    args = parser.parse_args()

    config = loader(args)
    if not config:
        sys.exit()
        
    session.init(args, config)
    
    args.func(args)

    print('Done.')
