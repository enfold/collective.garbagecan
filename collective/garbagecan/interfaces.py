from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface.declarations import implementer
from zope.interface.interface import Attribute


_ = MessageFactory('collective.garbagecan')


class IGarbageStorage(Interface):
    """A persistent storage for the garbage can."""


class IGarbageDeletedEvent(Interface):
    """An event signaling that an object was deleted (added to the garbage can)."""
    object = Attribute("The deleted object.")


class IGarbageRestoredEvent(Interface):
    """An event signaling that an object was restored to its original place."""
    object = Attribute("The restored object.")
