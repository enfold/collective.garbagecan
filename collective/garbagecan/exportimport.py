from zope.annotation.interfaces import IAnnotations

from collective.garbagecan.garbagecan import GARBAGECAN_KEY
from collective.garbagecan.utils import GARBAGECAN_INSTALLED_KEY


def uninstall(context):
    if not context.readDataFile('collective.garbagecan.uninstall.txt'):
        return

    portal = context.getSite()
    annotations = IAnnotations(portal)
    if GARBAGECAN_KEY in annotations:
        del annotations[GARBAGECAN_KEY]
    if GARBAGECAN_INSTALLED_KEY in annotations:
        del annotations[GARBAGECAN_INSTALLED_KEY]


def install(context):
    if not context.readDataFile('collective.garbagecan.txt'):
        return
    portal = context.getSite()
    annotations = IAnnotations(portal)
    annotations[GARBAGECAN_INSTALLED_KEY] = True
