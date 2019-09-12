from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.request import Request
import json

from portlycli.models import AuthenticatedPortal, PortalItem, PortalData
import portlycli.session as session

def generate_token(creds):
    '''Retrieves a token to be used with API requests.'''

    portalUrl, username, password = creds

    parameters = urlencode({'username' : username,
                            'password' : password,
                            'client' : 'referer',
                            'referer': portalUrl,
                            'expiration': 60,
                            'f' : 'json'}).encode()

    req =  Request(portalUrl + '/sharing/rest/generateToken', data=parameters)
    response = urlopen(req).read()
    
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return AuthenticatedPortal(portalUrl, jsonResponse['token'])
        elif 'error' in jsonResponse:
            print("Error generating a token at '%s': '%s'" % (portalUrl, jsonResponse['error']['message']))
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError:
        print('An unspecified error occurred.')


def get_item_description(itemId, portalUrl, token):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urlencode({'token' : token,
                                   'f' : 'json'})
    response = urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "?" + parameters).read()
    return response


def __search__(portal, query=None, numResults=100, sortField='numviews',
               sortOrder='desc', start=0, token=None):
    '''Retrieve a single page of search results.'''
    params = {
        'q': query,
        'num': numResults,
        'sortField': sortField,
        'sortOrder': sortOrder,
        'f': 'json',
        'start': start
    }
    if token:
        # Adding a token provides an authenticated search.
        params['token'] = token
    request = portal + '/sharing/rest/search?' + urlencode(params)
    results = json.loads(urlopen(request).read())
    return results


def search_portal(authentcatedPortal, query=None, totalResults=None, sortField='numviews',
                 sortOrder='desc'):
    '''
    Search the portal using the specified query and search parameters.
    Optionally provide a token to return results visible to that user.
    '''

    portal, token = authentcatedPortal
    
    # Default results are returned by highest
    # number of views in descending order.
    allResults = []
    if not totalResults or totalResults > 100:
        numResults = 100
    else:
        numResults = totalResults
        
    results = __search__(portal, query, numResults, sortField, sortOrder, 0,
                         token)

    if not 'error' in results.keys():
        if not totalResults:
            totalResults = results['total'] # Return all of the results.
        allResults.extend(results['results'])
        while (results['nextStart'] > 0 and
               results['nextStart'] < totalResults):
            # Do some math to ensure it only
            # returns the total results requested.
            numResults = min(totalResults - results['nextStart'] + 1, 100)
            results = __search__(portal=portal, query=query,
                                 numResults=numResults, sortField=sortField,
                                 sortOrder=sortOrder, token=token,
                                 start=results['nextStart'])
            allResults.extend(results['results'])
        return allResults
    else:
        print(results['error']['message'])
        return results


def list_items(authenticatedPortal, searchQuery):
    portalUrl, token = authenticatedPortal

    # Get a list of the content matching the query.
    content = search_portal(authenticatedPortal, query=searchQuery)

    items = []
    
    for item in content:
        json_desc = get_item_description(item['id'], portalUrl, token)
        desc = json.loads(json_desc)
        of_interest = PortalItem(desc['name'], desc['title'], desc['type'], item['id'], desc, json_desc)
        print("name: '%s'; title: '%s'; type: '%s'; id: %s" % of_interest[:4])
        items.append(of_interest)
        
    return items

def get_item_description(itemId, portalUrl, token):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urlencode({'token' : token,
                                   'f' : 'json'})
    response = urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "?" + parameters).read()
    return response

def get_item_data(itemId, portalUrl, token):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urlencode({'token' : token,
                                   'f' : 'json'})
    response = urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "/data?" + parameters).read()
    return response


def get_item(itemId, authenticatedPortal):
    sourcePortal, sourceToken = authenticatedPortal
    
    desc = get_item_description(itemId, sourcePortal, sourceToken)
    data = get_item_data(itemId, sourcePortal, sourceToken)
    descripto = json.loads(desc)
    title = descripto['title']
    thumbnail = descripto['thumbnail']
    
    if thumbnail:
        thumbnail_url = (sourcePortal + '/sharing/rest/content/items/' +
                        itemId + '/info/' + thumbnail +
                        '?token=' + sourceToken)
    else:
        thumbnail_url = ''

    return PortalData(descripto['name'], title, descripto['type'],
                      itemId, descripto, desc, data, thumbnail_url)


def get_items(authenticatedPortal, content):
    items = []    
    for item in content:
        data = get_item(item['id'], authenticatedPortal)
        items.append(data)        
    return items


def get_user_content(username, portalUrl, token):
    ''''''
    parameters = urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/content/users/' + username +
               '?' + parameters)
    content = json.loads(urlopen(request).read())
    return content


def get_owner(authenticatedPortal):
    portalUrl, token = authenticatedPortal
    matches = [cred.user for cred in session.config.creds.values() if cred.url == portalUrl]
    if len(matches) > 0:
        return matches[0]
    else:
        False

        
def get_destination_folder(authenticatedPortal):
    portalUrl, token = authenticatedPortal    
    folderId = ''
    owner = get_owner(authenticatedPortal)    
    destUser = get_user_content(owner, portalUrl, token)

    for folder in destUser['folders']:
        if folder['title'] == folder:
            folderId = folder['id']
    return folderId

def no_nones(d):
    for key, value in d.items():
        if value is None:
            d[key] = ''
    return d
        
def add_item(username, folder, description, data, portalUrl, token, thumbnailUrl=''):
    '''Creates a new item in a user's content.'''

    desc = json.loads(description)
            
    print("title: '%s'; description: '%s'" % (desc['title'], desc['description']))

    # merge
    add_item_params = {
        'item': desc['title'],
        'text': data,
        'overwrite': 'false',
        'thumbnailurl': thumbnailUrl,
        'token' : token,
        'f' : 'json'
    }

    # mixin
    post_params = {**desc, **add_item_params}

    # None values need to be empty strings before posting to portal
    no_nones(post_params)
    
    parameters = urlencode(post_params).encode()

    url_parts = [portalUrl, 'sharing/rest/content/users', username]

    if folder:
        url_parts.append(folder)

    url_parts.append('addItem?')
    addItemUrl = "/".join(url_parts)

    print("Posting content to url: '%s'" % (addItemUrl))
    
    req = Request(addItemUrl, data=parameters)
    response = urlopen(req).read()
    return response


def upload_items(authenticated_portal, portal_data):
    portalUrl, token = authenticated_portal

    owner = get_owner(authenticated_portal)
    folder = get_destination_folder(authenticated_portal)
    
    print("Copying %d item(s) to portal: '%s' in folder: '%s' as user: '%s'" %
          (len(portal_data), portalUrl, folder, owner))
    wins = 0
    fails = 0    
    for d in portal_data:
        try:
            status = add_item(owner, folder,
                              d.desc_str, d.data,
                              portalUrl, token, d.thumbnail_url)
            result = json.loads(status)
            if 'success' in result:
                wins += 1                
                print('successfully copied "%s": "%s"' % (d.type, d.title))
            elif 'error' in result:
                fails += 1                
                print('error in add item response for type %s: %s' % (d.type,d.title))
                print('error message: "%s"' % (result['error']['message']))
                for detail in result['error']['details']:
                    print(detail)
            else:
                fails += 1                
                print('error copying %s: %s' % (d.type, d.title))
        except Exception as e:
            fails += 1
            print('Exception posting item %s: %s' % (d.type, d.title))
            print(e.message)

        return (wins, fails, len(portal_data))
