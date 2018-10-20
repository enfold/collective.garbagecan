import datetime
import os
import sys

import transaction
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.event import notify
import Zope2
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser

from collective.garbagecan.interfaces import IGarbageStorage
from collective.garbagecan.utils import isInstalled

try:
    from collective.auditlog.interfaces import AuditableActionPerformedEvent
    AUDIT = True
except ImportError:
    AUDIT = False


def spoofRequest(app):
    user = app.acl_users.getUserById("admin")
    if not user:
        user = OmnipotentUser().__of__(app.acl_users)
    _policy = PermissiveSecurityPolicy()
    setSecurityPolicy(_policy)
    newSecurityManager(None, user)
    return makerequest(app, environ=os.environ)


def main(argv=sys.argv):
    if len(sys.argv) != 4:
        raise Exception("Must specify configuration path, site name and days")

    site_name = sys.argv[2]
    days = int(sys.argv[3])
    now = datetime.datetime.now()
    argv = argv

    filepath = sys.argv[1]
    os.environ['ZOPE_CONFIG'] = filepath
    sys.argv = ['']
    from Zope2.Startup.run import configure
    configure(os.environ['ZOPE_CONFIG'])
    app = spoofRequest(Zope2.app())
    request = app.REQUEST
    site = app.unrestrictedTraverse(site_name)
    setSite(site)
    storage = IGarbageStorage(site)
    if storage and isInstalled(site=site):
        expunge = []
        for key, item in storage.garbagecan_contents():
            delta = now - item.garbagecan_date
            if delta.days > days:
                expunge.append(key)
        for key in expunge:
            storage.expunge(key)
            if AUDIT:
                notify(AuditableActionPerformedEvent(site,
                                                     request,
                                                     'Restore (script)',
                                                     ', '.join(expunge)))
            transaction.commit()
