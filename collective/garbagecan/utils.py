from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


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
