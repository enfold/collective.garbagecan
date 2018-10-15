from Products.Five.browser import BrowserView

from plone.api import portal
from plone.api import user

from ..interfaces import IGarbageStorage


class SiteGarbagecanView(BrowserView):

    def list_contents(self):
        site = portal.get()
        storage = IGarbageStorage(site)
        contents = [i for i in storage.garbagecan_contents()]
        return sorted(contents,
                      key=lambda n: n[1].garbagecan_date,
                      reverse=True)

    def folder_contents(self, folderish):
        return ['{} ({})'.format(i.title, i.portal_type)
                for i in folderish.objectValues()]

    def user_display_name(self, username):
        obj = user.get(userid=username)
        display = obj.getProperty('fullname')
        if not display:
            display = username
        return display

    def __call__(self):
        selected = self.request.get('selected', None)
        if selected is not None:
            if not isinstance(selected, list):
                selected = [selected]
            site = portal.get()
            storage = IGarbageStorage(site)
            expunge = self.request.get('expunge', None)
            if expunge is not None:
                for path in selected:
                    storage.expunge(path)
            restore = self.request.get('restore', None)
            if restore is not None:
                for path in selected:
                    storage.restore(path)
        return super(SiteGarbagecanView, self).__call__()
