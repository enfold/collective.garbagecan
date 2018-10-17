Introduction
============

The package creates a "garbage can" for deleted objects inside of a Plone
site, where these objects are stored until they are undeleted or expunged.


Installation
============

Download the package from GitHub and extract into your src directory.
Add 'collective.garbagecan' to your eggs and zcml slugs in buildout.
Include the location (src/collective.garbagecan) in development slugs too.
Run buildout

In Site Setup -> Add-ons, activate Garbage Can.
Once it is installed you will see "Garbage Can" under Add-on Configuration.
This is where you can see and manage deleted objects.

Expunging old objects from a cron job
=====================================

The package includes a script for expunging files older than a specified
number of days. From the buildout directory run:

$ bin/expunge parts/client1/etc/zope.conf Plone 45

The first parameter is the configuration file of one of the installed
clients, the second parameter is the site name, and the last parameter is
the number of days.
