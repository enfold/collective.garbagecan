import unittest
from plone.testing.zope import login
from plone.app.testing import SITE_OWNER_NAME

from collective.garbagecan.testing import GARBAGECAN_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = GARBAGECAN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        login(self.app['acl_users'], SITE_OWNER_NAME)
