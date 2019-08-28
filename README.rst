
*********
Mr Portly
*********

Mr Portly is a simple command line that move `ArcGIS for Portal
<https://enterprise.arcgis.com/en/portal/latest/use/what-is-portal-for-arcgis-.htm>`_
content items between instances.  To use this tool you'll need access
to one or more ArcGIS for Portal instances.  If you don't what any of
that is then best walk away now.

Mr Porty does not handle any dependencies between items, nor republish
services and remap those services within the destination instance.
This tool is based on a `sample script
<https://enterprise.arcgis.com/en/portal/latest/administer/linux/example-copy-content.htm>`_
published to the Esri's help pages.  All I have done here is wrap the
script in a CLI, as is my bias.


Installation
============

You'll need to use ``pip`` to directly install Mr Portly from github::

    $ pip install -e https://github.com/bigwestern/portly-cli.git

    
Getting Started
===============

Follow these steps after you have successfully installed the package
into your python environment.  The assumption made in the following
commands is that your python environment has been activated and is
available at the command line.

1. Create a config file
-----------------------

The following command will place a ``.portly.ini`` file in your home
diectory::

    $ portly init > .portly.ini

2.  Add your portal creds to the config file
--------------------------------------------
    
Edit the ``.portly.ini`` file and enter the credentials of the portal
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
``info`` command::

  $ portly info
  

3.  Check you can connect to your portal
----------------------------------------
  
Test that you can connect to the portal env using the ``list`` command::

  $ portly list agol

4.  Copy some items between environments
----------------------------------------

We now should be setup to do something.  Try a copy of portal items
like so::

  $ portly copy agol myportal
