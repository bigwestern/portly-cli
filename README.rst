=========
Mr Portly
=========

This comand line tool let's copy portal items between environments.
It does not handle any dependencies between items nor republish
services.  The tool is base on a script published to the Esri help
pages.  All I have done is placed a CLI wrapper around it, as is my
want.

------------
Installation
------------

I haven't registered this package with any python package website so
you'll need to tell your python install manually like so::

    $ git clone thisrepo
    $ pip install thisrepo

---------------
Getting Started
---------------

First, you'll need a config file.  The following command will place a
portly.ini file in your home diectory::

    $ portly init
    
Second, edit the ini file and enter the credentials of the portal
environments you want to access.  Hint: give the name of the portal in
square brackets ('[]') something short and catchy because you'll use
this on the command line alot.  Here's an example::

  [agol]
  url = https://qgsp.maps.arcgis.com
  user = wheresjacky
  passwd = qwerty12

  [myportal]
  url = https://billabong.maps.arcgis.com
  user = banjop
  passwd = jollyjumbuck
  
Third, check the change to the config is holding up okay by running
the info command::

  $ portly info

Fourth, test that you can connect to the portal env using the list
command.  Note that if you do not specify a query the default will be
'owner:wheresjacky'.  This means the list command will list out all
portal items ownered by 'wheresjacky'.  you can override this default
with --query id:reallylongnumber if you want.

  $ portly list agol

We now should be setup to do something.  Try a copy of portal items
like so::

  $ portly copy agol myportal
