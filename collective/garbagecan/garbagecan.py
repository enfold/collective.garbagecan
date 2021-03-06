from datetime import datetime

from Acquisition import aq_base
from BTrees.OOBTree import OOBTree

from zope.interface import implements
from zope.component import adapts
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations

from plone.app.layout.navigation.interfaces import INavigationRoot

from .interfaces import IGarbageStorage
from .utils import getUser
from .utils import isInstalled


GARBAGECAN_KEY = 'collective.garbagecan'


class ContainerGone(Exception):
    """Raised when a container for an undeleted object has been removed"""


class ExistingId(Exception):
    """Raised when there is already an item with same id as undeleted one"""


class GarbageStorage(object):

    adapts(INavigationRoot)
    implements(IGarbageStorage)

    def __init__(self, context):
        self.annotations = IAnnotations(context)

    def check_initialized(self):
        if GARBAGECAN_KEY not in self.annotations:
            self.annotations[GARBAGECAN_KEY] = OOBTree()

    def garbagecan_contents(self):
        self.check_initialized()
        return self.annotations[GARBAGECAN_KEY].iteritems()

    def dispose(self, item):
        self.check_initialized()
        key = self.get_key(item)
        item.garbagecan_date = datetime.now()
        item.relatedItems = []
        user = getUser()
        item.garbagecan_deleted_by = user
        self.annotations[GARBAGECAN_KEY][key] = item

    def get_key(self, item):
        return '{}:{}'.format('/'.join(item.getPhysicalPath()),
                              item.creation_date.millis())

    def expunge(self, key):
        self.check_initialized()
        if key in self.annotations[GARBAGECAN_KEY]:
            del self.annotations[GARBAGECAN_KEY][key]

    def restorability(self, key, newid=None, newcontainer=None):
        state = 'restorable'
        self.check_initialized()
        item = self.annotations[GARBAGECAN_KEY].get(key, None)
        if item is not None:
            path = key.split(':')[0]
            site = getSite()
            parent_path, item_id = path.rsplit('/', 1)
            if newid is not None:
                item_id = newid
            if newcontainer is not None:
                parent_path = newcontainer
            try:
                parent = site.unrestrictedTraverse(parent_path)
            except KeyError:
                state = 'container_gone'
                parent = None
            if parent and item_id in parent.objectIds():
                state = 'existing_id'
        else:
            state = 'unrestorable'
        return state

    def restore(self, key, newid=None, newcontainer=None, restricted=False):
        self.check_initialized()
        item = self.annotations[GARBAGECAN_KEY].get(key, None)
        if item is not None:
            path = key.split(':')[0]
            site = getSite()
            traverse = site.unrestrictedTraverse
            if restricted:
                traverse = site.restrictedTraverse
            parent_path, item_id = path.rsplit('/', 1)
            if newid is not None:
                item_id = newid
            if newcontainer is not None:
                parent_path = newcontainer
            try:
                parent = traverse(parent_path)
            except KeyError:
                message = "One or more containers in path {} do not exist"
                raise ContainerGone(message.format(parent_path))
            if item_id in parent.objectIds():
                message = "Container at {} already has an item with id {}."
                raise ExistingId(message.format(parent_path, item_id))
            del item.garbagecan_date
            del item.garbagecan_deleted_by
            item.id = item_id
            parent._setObject(item_id, aq_base(item))
            del self.annotations[GARBAGECAN_KEY][key]


def handle_deletion(obj, event):
    if not isInstalled():
        return
    site = getSite()
    storage = IGarbageStorage(site)
    storage.dispose(obj)
