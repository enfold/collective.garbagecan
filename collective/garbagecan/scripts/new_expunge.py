
import argparse
import datetime
import logging
import os
import sys
import traceback
import transaction

from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import newSecurityManager
from collective.garbagecan.interfaces import IGarbageStorage
from collective.garbagecan.utils import isInstalled
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.event import notify
from zope.globalrequest import setRequest

try:
    from collective.auditlog.interfaces import AuditableActionPerformedEvent
    AUDIT = True
except ImportError:
    AUDIT = False

logger = logging.getLogger("collective.garbagecan.scripts.new_expunge")


def entrypoint(app, args):
    # Logging configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file")
    parser.add_argument("portal_path")
    parser.add_argument("days")
    args = parser.parse_args(args[2:])
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(args.log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    app = makerequest(app)

    roles = ('manage', 'Manager', 'Site Administrator',)
    manager = UnrestrictedUser('System Processes', '', roles, [])
    newSecurityManager(None, manager)

    # Set site
    try:
        site = app.restrictedTraverse(args.portal_path)
    except Exception:
        raise ValueError(
            "Wrong portal_path parameter; Please specify an existing "
            "site's path."
        )

    setSite(site=site)
    site.REQUEST["PARENTS"] = [site]
    site.REQUEST.setVirtualRoot("/")

    if os.getenv("SERVER_NAME"):
        site.REQUEST["SERVER_NAME"] = os.getenv("SERVER_NAME")
    if os.getenv("SERVER_URL"):
        site.REQUEST["SERVER_URL"] = os.getenv("SERVER_URL")

    setRequest(site.REQUEST)

    logger.info("Running garbage expunge script")

    days = int(args.days)
    now = datetime.datetime.now()

    try:
        transaction.begin()

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
                                                        site.REQUEST,
                                                        'Expunge (script)',
                                                        key.split(':')[0]))
                transaction.savepoint()

        # commit transaction
        transaction.commit()
        app._p_jar.sync()
    except Exception as e:
        logger.error("Running the garbage expunge script failed")
        exc_info = sys.exc_info()
        tb = traceback.format_exception(*exc_info)
        logger.error(''.join(tb))
        sys.exit(1)

    logger.info("Finished garbage expunge script")


if __name__ == "__main__":
    app = globals()["app"]  # for pep8
    entrypoint(app, sys.argv[1:])
