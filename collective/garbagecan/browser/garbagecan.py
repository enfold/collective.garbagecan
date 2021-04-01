from z3c.form import field
from z3c.form import form
from z3c.form import interfaces
from zope import schema
from zope.event import notify
from zope.interface import Interface
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.api import portal
from plone.api import user
from plone.i18n.normalizer import idnormalizer

from ..interfaces import _
from ..interfaces import IGarbageStorage
from ..utils import getUser


try:
    from collective.auditlog.interfaces import AuditableActionPerformedEvent
    AUDIT = True
except ImportError:
    AUDIT = False


class SiteGarbagecanView(BrowserView):

    RESTRICTED = False

    def list_contents(self):
        site = portal.get()
        storage = IGarbageStorage(site)
        contents = [i for i in storage.garbagecan_contents()]
        return sorted(contents,
                      key=lambda n: n[1].garbagecan_date,
                      reverse=True)

    def folder_contents(self, folderish):
        contents = list()
        for item in folderish.objectValues():
            title = item.title

            if not title:
                title = item.id
            contents.append('{} ({})'.format(title, item.portal_type))
        return contents

    def user_display_name(self, username):
        display = None
        obj = user.get(userid=username)
        if obj is not None:
            display = obj.getProperty('fullname')
        if not display:
            display = username
        return display

    def expunge(self):
        selected = self.request.get('selected', None)
        site = portal.get()
        if selected is not None:
            if not isinstance(selected, list):
                selected = [selected]
            paths = list()
            storage = IGarbageStorage(site)
            for key in selected:
                storage.expunge(key)
                path = key.split(':')[0]
                paths.append(path)
                if AUDIT:
                    notify(AuditableActionPerformedEvent(self.context,
                                                         self.request,
                                                         'Expunge',
                                                         path))
            IStatusMessage(self.request).add(
                _(u'Expunged: ${selected}.',
                    mapping={u'selected': ','.join(paths)}))

    def restore(self, oldselected=None):
        selected = self.request.get('selected', oldselected)
        problems = {'container_gone': [],
                    'existing_id': [],
                    'unrestorable': [],
                    }
        restore = True
        if selected is not None:
            if not isinstance(selected, list):
                selected = [selected]
            self.selected = selected
            site = portal.get()
            storage = IGarbageStorage(site)
            idxid = 0
            idxcon = 0
            fixed = 0
            for key in selected:
                restorability = storage.restorability(key)
                if restorability == 'container_gone':
                    problems[restorability].append(key)
                    restore = False
                    if self.newcontainers:
                        fixrest = storage.restorability(key,
                            newcontainer=self.newcontainers[idxcon])
                        if fixrest == 'restorable':
                            fixed += 1
                    idxcon += 1
                if restorability == 'existing_id':
                    problems[restorability].append(key)
                    restore = False
                    if self.newids:
                        fixrest = storage.restorability(key,
                            newid=self.newids[idxid])
                        if fixrest == 'restorable':
                            fixed += 1
                    idxid += 1
                if fixed == idxid + idxcon:
                    restore = True
            if restore:
                paths = list()
                idxid = 0
                idxcon = 0
                for key in selected:
                    if self.newids and key in problems['existing_id']:
                        storage.restore(key,
                                        newid=self.newids[idxid],
                                        restricted=self.RESTRICTED)
                        idxid += 1
                    elif self.newcontainers and key in problems['container_gone']:
                        storage.restore(key,
                                newcontainer=self.newcontainers[idxcon],
                                restricted=self.RESTRICTED)
                        idxcon += 1
                    else:
                        storage.restore(key, restricted=self.RESTRICTED)
                    path = key.split(':')[0]
                    paths.append(path)
                    if AUDIT:
                        notify(AuditableActionPerformedEvent(self.context,
                                                             self.request,
                                                             'Restore',
                                                             path))
                IStatusMessage(self.request).add(
                    _(u'Restored: ${selected}.',
                      mapping={u'selected': ', '.join(paths)}))
            else:
                self.problems = problems

                problem_form = GarbagecanRestoreForm(self.context,
                                                     self.request,
                                                     selected,
                                                     problems)
                problem_form.update()
                self.problem_form = problem_form

    def continue_restore(self):
        self.newcontainers = [self.request[k] for k in self.request.keys()
                              if k.startswith('widgets.container_gone_')]
        newids = [self.request[k] for k in self.request.keys()
                  if k.startswith('widgets.existing_id_')]
        self.newids = list(map(idnormalizer.normalize, newids))
        oldselected = self.request.get('widgets.selected', None)
        oldselected = oldselected.split()
        self.restore(oldselected=oldselected)

    def __call__(self):
        self.selected = []
        self.problems = None
        self.newids = []
        self.newcontainers = []
        if self.request.get('expunge', None) is not None:
            self.expunge()
        if self.request.get('restore', None) is not None:
            self.restore()
        if self.request.get('widgets.selected', None) is not None:
            self.continue_restore()
        return super(SiteGarbagecanView, self).__call__()


class MyGarbagecanView(SiteGarbagecanView):

    RESTRICTED = True

    def list_contents(self):
        site = portal.get()
        storage = IGarbageStorage(site)
        contents = [i for i in storage.garbagecan_contents()
                    if i[1].garbagecan_deleted_by == getUser()]
        return sorted(contents,
                      key=lambda n: n[1].garbagecan_date,
                      reverse=True)


class IGarbagecanBaseField(Interface):
    """No initial fields"""


class GarbagecanRestoreForm(form.Form):

    prefix = ''

    fields = field.Fields(IGarbagecanBaseField)

    ignoreContext = True

    def __init__(self, context, request, selected=None, problems=None):
        super(GarbagecanRestoreForm, self).__init__(context, request)
        fields = self.fields
        self.selected = selected
        self.problems = problems
        if selected is not None and problems is not None:
            hidden = schema.List(
                    __name__='selected',
                    readonly=True,
                    value_type=schema.TextLine(),
                    default=selected)
            fields += field.Fields(hidden)
            fields['selected'].mode = interfaces.HIDDEN_MODE
            fields['selected'].widget = interfaces.HIDDEN_MODE
            for num, problem in enumerate(problems['container_gone']):
                cfield = schema.TextLine(
                    __name__='container_gone_' + str(num),
                    title=u'Container for ' + problem.split(':')[0],
                    description=u'Container moved or deleted. Pick new container. Use relative path from site.',
                    required=True,
                )
                fields += field.Fields(cfield)
            for num, problem in enumerate(problems['existing_id']):
                cfield = schema.TextLine(
                    __name__='existing_id_' + str(num),
                    title=u'Id for ' + problem.split(':')[0],
                    description=u'Id in use in this container. Pick new id',
                    required=True,
                )
                fields += field.Fields(cfield)
        self.fields = fields
