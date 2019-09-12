import os
import json

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

def get_download_path(content_path, authenticated_portal):
    return os.path.join(
        content_path,
        url_to_dir(authenticated_portal.url))

def item_to_file(directory, title, data):
    item_files = []
    if data.desc:
        item_files.append(
            to_json_file(
                os.path.join(directory, ".".join([data.title, 'desc', 'json'])),
                data.desc,
                True))
        
    if data.data:
        item_files.append(
            to_json_file(
                os.path.join(directory, ".".join([data.title, 'data', 'json'])), data.data))

    if data.thumbnail_url:
        item_files.append(
            to_thumbnail_file(
                os.path.join(directory, ".".join([data.title, 'thumbnail', 'txt'])), data.thumbnail_url))

    return item_files

def to_csv(csv_path, header, rows):
    file = open(csv_path, "w")                
    file.write(','.join(str(c) for c in header) + '\n')
    for row in rows:
        file.write(','.join(str(i) for i in row) + '\n')
    file.close()
    return csv_path
