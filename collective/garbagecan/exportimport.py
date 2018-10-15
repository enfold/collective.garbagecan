from zope.annotation.interfaces import IAnnotations

from collective.garbagecan.garbagecan import GARBAGECAN_KEY


def uninstall(context):
    if not context.readDataFile('collective.garbagecan.uninstall.txt'):
        return

    portal = context.getSite()
    annotations = IAnnotations(portal)
    if GARBAGECAN_KEY not in annotations:
        return
    del annotations[GARBAGECAN_KEY]
