from collective.garbagecan.interfaces import IGarbageDeletedEvent
from collective.garbagecan.interfaces import IGarbageRestoredEvent
from zope.interface import implementer


@implementer(IGarbageDeletedEvent)
class GarbageDeletedEvent(object):

    def __init__(self, object):
        self.object = object


@implementer(IGarbageRestoredEvent)
class GarbageRestoredEvent(object):

    def __init__(self, object):
        self.object = object
