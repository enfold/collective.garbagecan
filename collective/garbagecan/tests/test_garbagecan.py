from .base import BaseTestCase
from ..interfaces import IGarbageStorage
from ..garbagecan import GARBAGECAN_KEY


class TestStorage(BaseTestCase):

    def setUp(self):
        super(TestStorage, self).setUp()
        self.login_as_portal_owner()

    def test_dispose(self):
        self.portal.invokeFactory('Document', 'd1', title='Doc 1')
        item = self.portal['d1']
        storage = IGarbageStorage(self.portal)
        key = storage.get_key(item)
        self.portal.manage_delObjects(['d1'])
        self.assertTrue(key in storage.annotations[GARBAGECAN_KEY])
