# -*- coding: utf-8 -*-


def upgrade_to_1001(portal_setup):
    portal_setup.runImportStepFromProfile(
        'profile-collective.garbagecan:default',
        'collective.garbagecan.install',
        run_dependencies=False)
