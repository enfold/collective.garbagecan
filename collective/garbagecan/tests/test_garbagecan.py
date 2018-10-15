from .base import BaseTestCase
from ..interfaces import IGarbageStorage
from ..garbagecan import GARBAGECAN_KEY


class TestStorage(BaseTestCase):

    def setUp(self):
        super(TestStorage, self).setUp()
        self.login_as_portal_owner()

    def test_dispose(self):
        self.portal.invokeFactory('Document', 'd1', title='Doc 1')
        self.portal.manage_delObjects(['d1'])
        storage = IGarbageStorage(self.portal)
        self.assertTrue('/plone/d1' in storage.annotations[GARBAGECAN_KEY])
