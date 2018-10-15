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
