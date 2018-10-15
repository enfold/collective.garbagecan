# coding=utf-8
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2
from zope.configuration import xmlconfig

try:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
    BASE_FIXTURE = PLONE_APP_CONTENTTYPES_FIXTURE
except ImportError:
    from plone.app.testing import PLONE_FIXTURE
    BASE_FIXTURE = PLONE_FIXTURE


class Garbagecan(PloneSandboxLayer):
    defaultBases = (BASE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import collective.garbagecan
        xmlconfig.file('configure.zcml', collective.garbagecan,
                       context=configurationContext)
        z2.installProduct(app, 'collective.garbagecan')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'collective.garbagecan:default')
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))


GARBAGECAN_FIXTURE = Garbagecan()
GARBAGECAN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GARBAGECAN_FIXTURE,), name="Garbagecan:Integration")
GARBAGECAN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GARBAGECAN_FIXTURE,), name="Garbagecan:Functional")
