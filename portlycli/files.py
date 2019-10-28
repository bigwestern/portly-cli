import os
import json
import portlycli.defaults as defaults

def to_json_file(file_path, data, is_dict_already=False):
    validjson = False
    try:

        if is_dict_already:
            jdict = data
        else:
            jdict = json.loads(data)
            
        nicejson = json.dumps(jdict, indent=2)
        validjson = True
    except ValueError as e:
        print(e)
        print("Can't beautify json for file %s" % (file_path))
        
    if validjson:
        file = open(file_path,"w")        
        file.write(nicejson)
    else:
        file = open(file_path,"wb")                
        file.write(data)
        
    file.close()
    return file_path

def to_thumbnail_file(file_path, data):
    file = open(file_path,"w")                
    file.write(data)
    file.close()
    return file_path

def url_to_dir(url):
    return url.lstrip('htps:/.')

def get_download_path(content_path, authenticated_portal=None):
    cwd = os.getcwd()
    return os.path.join(
        cwd,
        content_path)
#        url_to_dir(authenticated_portal.url))

def item_to_file(directory, title, data, relabeller=lambda x: x, setvars=lambda x: x):
    item_files = {'desc': None, 'data': None, 'thumbnail_url': None}

    if data.desc:
        item_files['desc'] = to_json_file(
                os.path.join(directory, ".".join([data.title, data.type, 'desc', 'json'])),
                setvars(data.desc_str))
        
    if data.data:
        item_files['data'] = to_json_file(
                os.path.join(directory, ".".join([data.title, data.type, 'data', 'json'])),
                relabeller(data.data))

    if data.thumbnail_url:
        item_files['thumbnail_url'] = to_thumbnail_file(
                os.path.join(directory, ".".join([data.title, data.type, 'thumbnail', 'txt'])),
                relabeller(data.thumbnail_url))

    return item_files


def from_json_file(file_path):
    with open(file_path) as data:
        s = data.read()
        data.close()
        return s
    
def from_thumbnail_file(file_path):
    with open(file_path) as data:
        s = data.read()
        data.close()
        return s
        
def file_to_item(files):
    
    item = {'desc_str': None, 'data_str': None, 'thumbnail_str': None}
    
    if files['desc']:
        item['desc_str'] = from_json_file(files['desc'])
        
    if files['data']:
        item['data_str'] = from_json_file(files['data'])

    if files['thumbnail_url']:
        item['thumbnail_str'] = from_thumbnail_file(files['thumbnail_url'])

    return item
    
def to_csv(csv_path, header, rows):
    file = open(csv_path, "w")                
    file.write(','.join(str(c) for c in header) + '\n')
    for row in rows:
        file.write(','.join(str(i) for i in row) + '\n')
    file.close()
    return csv_path

