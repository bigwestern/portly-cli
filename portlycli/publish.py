from pathlib import Path
import os
import uuid
import json
from jsonmerge import merge

from portlycli.portal.requests import search_portal, get_item_description, update_item_request, generate_token
import portlycli.session as session
from portlycli.files import item_to_file, get_download_path

extensions = ['.webmap']

def getQuery(args):
    query = args.query if(args.query) else ""
    # read input json
    if(args.jsonfile):
        with open(args.jsonfile) as input_json:
            print("-q will be overwritten with user provided input")
            data = json.load(input_json)
            query = 'id:' + ' OR '.join([str(elem) for elem in data["IDs"]])
    
    return query

def validateInput(infile):

    itemType = ""
    itemConfig = {}
    publishId = ""

    ext = Path(infile).suffix
    
    if ext in extensions:
        itemType = "Web Map"
        with open(infile, "r") as itemConfigFile:
            itemConfig = json.load(itemConfigFile)
        
        # add publish id
        publishId = None
        publish_prop = itemConfig['_meta'] if '_meta' in itemConfig else {}
        if 'id' in publish_prop:
            publishId = publish_prop['id'] 
        else:
            publishId = str(uuid.uuid1())
            # add meta id to input
            publish_prop = {"_meta":{"id": str(publishId)}}
            itemConfig = merge(itemConfig, publish_prop)
            with open(infile, "w") as itemConfigFile:
                json.dump(itemConfig, itemConfigFile)
    
    return itemConfig, itemType, publishId

def add_publishId_to_source(dep, publishId):
    
    source_portal_id = None 
    source_portal = None
    for origin in dep['origins']:            
        if origin['originType'] == 'source':
            env = session.config.get_env_from_url(origin['portal']['url'])
            source_portal_id = origin['portal']['id']
            source_creds = session.config.creds[env]
            source_portal = generate_token(source_creds)

    add_publishId(source_portal, source_portal_id, publishId)

def add_publishId(portal, portal_id, publishId):
    #get item info
    portalUrl, token = portal
    item_desc = get_item_description(portal_id, portalUrl, token)
    item_desc_json = json.loads(item_desc)

    properties = item_desc_json['properties'] if item_desc_json['properties'] is not None else {}
    
    properties['publishId'] = publishId
    item_desc_json['properties'] = properties
    update_item_request(portal, portal_id, item_desc_json)

def check_publishId_exists(authenticatedPortal, publishId, username):
    portalUrl, token = authenticatedPortal

    # Get a list of the content matching the query.
    searchQuery = "owner:" + username
    content = search_portal(authenticatedPortal, query=searchQuery)

    for item in content:
        json_desc = get_item_description(item['id'], portalUrl, token)
        desc = json.loads(json_desc)
        prop = desc['properties'] if desc['properties'] is not None else {}
        if 'publishId' in prop:
            if prop['publishId'] == publishId:
                return desc['id']
                
    return None

def get_user_configs(dep, env):

    itemconfig = {}
    desc_file = os.path.basename(dep['files']['desc'])
    desc_filename = os.path.splitext(desc_file)[0]   
    desc_filename =  desc_filename + "." + env + ".json"    

    data_file = os.path.basename(dep['files']['data'])
    data_filename = os.path.splitext(data_file)[0]   
    data_filename =  data_filename + "." + env + ".json"  

    descpath = get_download_path(session.config.downloads) + "\\" + desc_filename
    datapath = get_download_path(session.config.downloads) + "\\" + data_filename
    with open(descpath, "r") as descfile:
        itemconfig['desc'] = json.load(descfile)
    with open(datapath, "r") as datafile:
        itemconfig['data'] = json.load(datafile)

    return itemconfig


