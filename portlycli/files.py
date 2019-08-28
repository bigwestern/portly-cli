import os

def to_json_file(file_path, data):
    validjson = False
    try:
        nicejson = json.dumps(json.loads(data), indent=2)
        validjson = True
    except:
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

def get_download_path(content_path, authenticated_portal):
    return os.path.join(
        content_path,
        url_to_dir(authenticated_portal.url))

def item_to_file(directory, title, data):
    item_files = []
    item_id, item_title, desc, data, thumbnail = data
    if desc:
        item_files.append(
            to_json_file(os.path.join(directory, ".".join([title, 'desc', 'json'])), desc))
        
    if data:
        item_files.append(
            to_json_file(os.path.join(directory, ".".join([title, 'data', 'json'])), data))

    if thumbnail:
        item_files.append(
            to_thumbnail_file(os.path.join(directory, ".".join([title, 'thumbnail', 'txt'])), thumbnail))

    return item_files
