from datetime import datetime

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
        key = item.absolute_url_path()
        item.garbagecan_date = datetime.now()
        item.relatedItems = []
        user = getUser()
        item.garbagecan_deleted_by = user
        self.annotations[GARBAGECAN_KEY][key] = item

    def expunge(self, path):
        self.check_initialized()
        if path in self.annotations[GARBAGECAN_KEY]:
            del self.annotations[GARBAGECAN_KEY][path]

    def restore(self, path):
        self.check_initialized()
        item = self.annotations[GARBAGECAN_KEY].get(path, None)
        if item is not None:
            site = getSite()
            parent_path, item_id = path.rsplit('/', 1)
            path_from_site = parent_path[2+len(site.id):]
            try:
                parent = site.restrictedTraverse(path_from_site)
            except KeyError:
                message = "One or more containers in path {} do not exist"
                raise ContainerGone(message.format(parent_path))
            if item_id in parent.objectIds():
                message = "Container at {} already has an item with id {}."
                raise ExistingId(message.format(parent_path, item_id))
            del item.garbagecan_date
            del item.garbagecan_deleted_by
            parent._setObject(item_id, item)
            del self.annotations[GARBAGECAN_KEY][path]


def handle_deletion(event):
    if not isInstalled():
        return
    site = getSite()
    storage = IGarbageStorage(site)
    storage.dispose(event.object)
