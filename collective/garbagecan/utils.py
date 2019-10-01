from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

GARBAGECAN_INSTALLED_KEY = 'collective.garbagecan.isinstalled'


def getUser():
    site = getSite()
    try:
        portal_membership = getToolByName(site, 'portal_membership')
        user = portal_membership.getAuthenticatedMember()
        username = user.getUsername()
    except AttributeError:
        request = getRequest()
        user = request.other.get('AUTHENTICATED_USER')
        if user is not None:
            username = user.getUserName()
        else:
            username = 'unknown'
    return username


def isInstalled(site=None):
    if site is None:
        site = getSite()
    annotations = IAnnotations(site)
    return annotations.get(GARBAGECAN_INSTALLED_KEY, False)
