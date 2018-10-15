from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface.declarations import implementer
from zope.interface.interface import Attribute


_ = MessageFactory('collective.garbagecan')


class IGarbageStorage(Interface):
    """A persistent storage for the garbage can."""
