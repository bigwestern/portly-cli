
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

You have two options with installing this package.

Option 1: You don't want to edit the source code
------------------------------------------------

If you don't want to change the tool in anyway then install the
package straight into your python environment.  Make sure you've done
your virtualenv setup beforehand::

    $ pip install git+https://github.com/bigwestern/portly-cli
  
Option 2: You want to install the package and also edit the source code
-----------------------------------------------------------------------

If you want to make changes to the source code then you will need to
clone the repo first and then advise the python packaging environment
to reference the cloned repo.  Here's how to go about that::

    $ git clone https://github.com/bigwestern/portly-cli.git
    $ cd portly-cli
    $ pip install -e .


Getting Started
===============

Follow these steps after you have successfully installed the package
into your python environment.  The assumption made in the following
commands is that your python environment has been activated and is
available at the command line.

1. Create a config file
-----------------------

The following command will place a ``.portly.ini`` file in your current
directory (You might wsnt to place the file in your home directory)::

    $ portly template > .portly.ini

2.  Add your portal creds to the config file
--------------------------------------------
    
Edit the ``.portly.ini`` file and enter the credentials of the portal
environments you want to access.  Here's an example::

  [jack@agol]
  url = https://www.arcgis.com
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

  $ portly list jack@agol

4.  Copy some items between environments
----------------------------------------

We now should be setup to do something.  Try a copy of portal items
like so::

  $ portly copy jack@agol myportal
