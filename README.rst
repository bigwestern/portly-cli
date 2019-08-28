
*********
Mr Portly
*********

This comand line tool let's copy portal items between environments.
It does not handle any dependencies between items nor republish
services.  The tool is base on a script published to the Esri help
pages.  All I have done is placed a CLI wrapper around it, as is my
want.


Installation
============

I haven't registered this package with any python package website so
you'll need to tell your python install manually like so::

    $ git clone thisrepo
    $ pip install thisrepo

    
Getting Started
===============

Follow these steps after you have successfully installed the package
into your python environment.  The assumption made in the following
commands is that your python environment has been activated and is
available at the command line.

1. Create a config file
-----------------------

The following command will place a `.portly.ini` file in your home
diectory::

    $ portly init > .portly.ini

2.  Add your portal creds to the config file
--------------------------------------------
    
Edit the `.portly.ini` file and enter the credentials of the portal
environments you want to access.  Here's an example::

  [agol]
  url = https://qgsp.maps.arcgis.com
  user = wheresjacky
  passwd = qwerty12

  [myportal]
  url = https://billabong.maps.arcgis.com
  user = banjop
  passwd = jollyjumbuck
  

3.  Check the config is valid
-----------------------------

Third, check the change to the config is holding up OK by running the
`info` command::

  $ portly info
  

3.  Check you can connect to your portal
----------------------------------------
  
Test that you can connect to the portal env using the `list` command::

  $ portly list agol

4.  Copy some items between environments
----------------------------------------

We now should be setup to do something.  Try a copy of portal items
like so::

  $ portly copy agol myportal

  
