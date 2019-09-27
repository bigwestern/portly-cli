
*******************
Guide to Portly CLI
*******************

The tool was created because:

* A local copy of an app or webmap was needed in the event of a fatal
  crash where a portal instance had to be completely rebuilt.
  
* Apps and webmaps need to be copied between portal instances such
  that the project owner can release new versions to UAT and
  production instances.
  
* Portal instances do not share unique identifiers between them.  This
  means a way needs to be found to consistently find portal items
  between portal instances.


Approach
========

Finding a solution to this problem has meant:

*  Finding the dependencies of portal items;
*  Modelling those dependencies in a data structure.

Finding dependencies
--------------------

The ArcGIS for Python has added a routine to find the dependencies of
portal items. However, this routine is not supported in ArcGIS Online
and only works with Portal Enterprise instances.  Users will want copy
items from ArcGIS Online to their own Enterprise portals.

So the approach taken here has been a simple one. First define where
the dependencies are in JSON.  Only those types with defined
dependencies will be added to the dependency graph.  For this proof of
concept only these two types have been defined::

        'Web Mapping Application': webapp_dependencies,
        'Web Map': webmap_dependencies

Next, the JSON is searched using `jsonpath_ng` like so::

    operational_expression = parse('operationalLayers[*].itemId')

and like so::

    basemap_expression = parse('baseMap.baseMapLayers[*].itemId')

Once the relevant item ids have been found then the portal is queried
again to find those items.

Modelling dependencies
----------------------

The tool then downloads the items and uses the relationship between
the items to load them into a dependency graph.  An item with no
children has no dependencies.  The dependency graph makes it easy to
order the items from least dependent to most dependent as well as
providing routines to define the parent items that depend on a child
item.  The `networkx` DiGraph object has used to achieve this.

Consistent identifiers
----------------------

The approach taken here has been to:

*  Assign a new eight character long id (`dep_id`) to portal items
   that are a dependency for other items
*  Only alter the JSON of a portal item that contain dependencies such
   that they use the new `dep_id`
*  Write the all the portal items to disk
*  Save the information about the dependencies to the `project.json`.


Risks
=====

1.  The portal types are too vast for their dependencies to be
    defined.
    
2.  A suitable matching strategy cannot be found between source and
    destination portals.




   
