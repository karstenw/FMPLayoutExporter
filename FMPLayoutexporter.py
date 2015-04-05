
# -*- coding: utf-8 -*-

import sys, os
import thread

import re

import pdb
kwdbg = False

import pprint
pp = pprint.pprint

import objc

import Foundation
import AppKit
NSWindowController = AppKit.NSWindowController

import PyObjCTools
import PyObjCTools.AppHelper

import OutlineModelDelegate
OutlineModel = OutlineModelDelegate.OutlineModel

import appscript
import fmpa10


# class defined in OutlineWindow.nib
class OutlineWindowController(NSWindowController):
    # the actual base class is NSWindowController

    cbPDF = objc.IBOutlet()
    cbXML = objc.IBOutlet()
    outlineView = objc.IBOutlet()

    def __new__(cls, obj):
        return cls.alloc().initWithObject_(obj)

    def initWithObject_(self, obj):
        self = self.initWithWindowNibName_("OutlineWindow")

        self.setWindowTitleForObject_(None)

        self.model = OutlineModel.alloc().initWithObject_(obj)

        self.outlineView.setDataSource_(self.model)
        self.outlineView.setDelegate_(self.model)
        self.outlineView.setTarget_(self)
        # self.outlineView.setDoubleAction_("doubleClick:")

        self.window().makeFirstResponder_(self.outlineView)
        self.cbPDF.setState_(True)
        self.cbXML.setState_(True)
        self.showWindow_(self)
        self.retain()
        return self

    def windowWillClose_(self, notification):
        # see comment in self.initWithObject_()
        self.autorelease()

    def setWindowTitleForObject_(self, obj):
        self.window().setTitle_( u"FMP-Layout-Exporter" )

    def setObject_(self, obj):
        self.setWindowTitleForObject_(obj)
        self.model.setObject_(obj)
        self.outlineView.reloadData()

    @objc.IBAction
    def export_(self, sender):
        createPDF = self.cbPDF.state()
        createXML = self.cbXML.state()
        m = self.model
        ov = self.outlineView

        # pdb.set_trace()
        sel = ov.selectedRowIndexes()
        selectedItems = []
        n = 0
        if sel:
            n = sel.count()
        next = sel.firstIndex()
        selectedItems.append( ov.itemAtRow_(next) )

        for i in range(1, n):
            next = sel.indexGreaterThanIndex_(next)
            selectedItems.append( ov.itemAtRow_(next) )

        data = {}
        for item in selectedItems:
            n,d,w,p = item.name, item.dbref,item.winref,item.parent
            if not w:
                continue
            if d not in data:
                data[d] = []
            data[d].append( (n,w) )
        
        fld = getFolderDialog()

        if fld:
            fld = fld[0]
            thread.start_new_thread(doExport, (data,
                                               fld,
                                               createPDF,
                                               createXML) )

def doExport(d, fld, createPDF, createXML ):
    pool = Foundation.NSAutoreleasePool.alloc().init()
    fpa = get_fmp( True )
    for k,v in d.iteritems():
        # get winref
        doc = fpa.documents[ k ]
        win = doc.windows[1]
        if os.path.exists( fld ):
            if v:
                iter_layouts( k, win, v, fld, createPDF, createXML )
    del pool


class PythonBrowserAppDelegate(Foundation.NSObject):

    def applicationDidFinishLaunching_(self, notification):
        self.newBrowser_(self)

    @objc.IBAction
    def newBrowser_(self, sender):
        fpa = get_fmp( True )
        if not fpa:
            return 
        data = getFMPData( fpa )
        #pdb.set_trace()
        OutlineWindowController( data )

    def outlineViewSelectionDidChange_(self, sender):
        pass

def getFolderDialog():
    panel = AppKit.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(False)
    panel.setCanChooseDirectories_(True)
    panel.setAllowsMultipleSelection_(False)
    rval = panel.runModalForTypes_([])
    if rval != 0:
        return [unicode(t) for t in panel.filenames()]
    else:
        return False

##################################
#
# FileMaker Section START
#
##################################

def get_fmp(bringtofront=True):
    """Create and return an application object for the default filemaker.

    If bringtofront it will be activated
    """
    e = appscript.app("System Events.app")
    if not e.isrunning():
        e.activate()
    pl = e.processes[ appscript.its.creator_type=='FMP7' ].properties()
    fpa = None
    pl.sort()
    pl.reverse()
    if pl:
        for p in pl:
            f = p.get(appscript.k.file, False)
            if not f:
                continue
            fpa = appscript.app(f.path, terms=fmpa10)
            if fpa.isrunning():
                break
    if fpa and bringtofront:
        fpa.activate()
    return fpa

def get_fmp_docs():
    """Get open databases as documentrefs from filemaker.

    If db return databaserefs.
    """
    fpa = get_fmp( True )
    if not fpa:
        return []
    return fpa.documents()

def getFMPData( fpa ):
    """Get open databases as documentrefs from filemaker.

    If db return databaserefs.
    """
    d = {}
    docs = fpa.documents()

    if docs:
        fpa.windows.visible.set(False)
        for doc in docs:
            doc.show()
            dname = doc.name()
            win = fpa.windows[ 1 ].name()
            if win.endswith( ')' ):
                winregex = re.compile("^(.+) \([-a-zA-Z0-9_%\.]+\)")
                m = winregex.match( win )
                if m:
                    win = m.groups()[0]
            winref = fpa.windows[ win ]
            w = doc.windows[1]()
            winref.visible.set(True)
            winref.show()
            winref.go_to()
            # name = unicode( doc.name() )
            name = unicode( win )

            do_menu_STDMENUS()

            # this MUST be True
            ok = do_menu_LAYOUTMODE()
            if ok:
                lnames = winref.layouts.name()
                lids = winref.layouts.ID_()
                d[dname] = []
                for l in zip(lids,lnames):
                    d[dname].append( (l[0],l[1]) )
            winref.visible.set(False)
    return d

def do_menu_STDMENUS():
    """Try to set Filemakere standard menus for frontmost document.
    This is needed to enter layout mode.

    return True on success
    """
    fpa = get_fmp()
    ok = False
    try:
        fpa.menus[ u'Tools' ].menus[ u'Custom Menus' ].menu_items[ u'[Standard FileMaker Menus]' ].do_menu()
        ok = True
    except appscript.reference.CommandError, v:
        try:
            fpa.menus[ u'Werkzeuge' ].menus[ u'Angepasste Men\xfcs' ].menu_items[ u'[Standard-FileMaker-Men\xfcs]' ].do_menu()
            ok = True
        except appscript.reference.CommandError, w:
            pass
            # print "ERROR:", v
    return ok

def do_menu_SELECTALL():
    fpa = get_fmp()
    ok = False
    try:
        fpa.menus[ u'Edit' ].menu_items[ u'Select All' ].do_menu(timeout=300)
        ok = True
    except appscript.reference.CommandError, v:
        try:
            fpa.menus[ u'Bearbeiten' ].menu_items[ u'Alles ausw\xe4hlen' ].do_menu(timeout=300)
            ok = True
        except appscript.reference.CommandError, w:
            # print "ERROR:", v
            pass
    return ok

def do_menu_COPY():
    fpa = get_fmp()
    ok = False
    try:
        fpa.menus[ u'Edit' ].menu_items[  u'Copy' ].do_menu(timeout=600)
        ok = True
    except appscript.reference.CommandError, v:
        try:
            fpa.menus[ u'Bearbeiten' ].menu_items[  u'Kopieren' ].do_menu(timeout=600)
            ok = True
        except appscript.reference.CommandError, w:
            # print "ERROR:", v
            pass
    return ok

def do_menu_LAYOUTMODE():
    fpa = get_fmp()
    ok = False
    try:
        fpa.menus[ u'View' ].menu_items[ u'Layout mode' ].do_menu(timeout=300)
        ok = True
    except appscript.reference.CommandError, v:
        try:
            fpa.menus[ u'Ansicht' ].menu_items[ u'Layoutmodus' ].do_menu(timeout=300)
            ok = True
        except appscript.reference.CommandError, w:
            # print "ERROR:", v
            pass
    return ok

def do_menu_BROWSEMODE():
    fpa = get_fmp()
    ok = False
    try:
        fpa.menus[ u'View' ].menu_items[ u'Browse mode' ].do_menu()
        ok = True
    except appscript.reference.CommandError, v:
        try:
            fpa.menus[ u'Ansicht' ].menu_items[ u'Bl\xe4tternmodus' ].do_menu()
            ok = True
        except appscript.reference.CommandError, w:
            # print "ERROR:", v
            pass
    return ok

def iter_layouts( docname, winref, layolist, outfolder, doPDF, doXML ):
    fpa = get_fmp( True )
    if not fpa:
        return False

    # we should be in Layout mode now
    # docname = winref.name()
    
    if docname.endswith( ')' ):
        winregex = re.compile("^(.+) \([-a-zA-Z0-9_%\.]+\)")
        m = winregex.match( docname )
        if m:
            docname = m.groups()[0]

    allLayoutnames = winref.layouts.name()

    winref.visible.set(True)
    winref.show()
    winref.go_to()

    # pdb.set_trace()
    idx = 0
    for layo in layolist:
        idx += 1
        
        name, id_ = layo
        
        layIndex = -1
        try:
            layIndex = allLayoutnames.index( name )
            # fmp layouts are 1-based
            layIndex += 1
        except Exception, err:
            print
            print "ERROR"
            print err
        
        sid = str(id_).rjust(7,"0")
        s = u"Layout id=%s    %i/%i  -  '%s'  -  '%s'" % (sid, layIndex, len(allLayoutnames), docname, name)
        print s.encode("utf-8")

        winref.layouts[ appscript.its.ID_==id_ ].go_to( timeout=600 )

        # select all
        ok = do_menu_SELECTALL()

        if ok:
            ok = do_menu_COPY()

            if ok:
                pboard = AppKit.NSPasteboard.generalPasteboard()
                if pboard:
                    pbtypes = pboard.types()

                    # make it "filenameable"
                    fname = docname.replace(".", "_")
                    fname = fname.replace("/", "_")
                    lidx = "0000" + str(layIndex)
                    lidx = lidx[-5:]
                    ln = name.replace(".", "_")
                    ln = ln.replace("/", "_")
                    ln = ln.replace(":", "_")

                    fname = fname + "_" + lidx + "_" + ln

                    fname = os.path.join(outfolder, fname)

                    for t in pbtypes:
                        data = str(pboard.dataForType_( t ) )
                        if type(ln) == str:
                            ln = unicode(ln, "utf-8")
                        try:
                            ln = ln.encode("utf-8")
                            t = t.encode("utf-8")
                        except Exception,v:
                            print; print "ERROR"
                            print v
                        if t == u'CorePasteboardFlavorType 0x584D4C4F':
                            if doXML:
                                f = open ( fname + ".xml", 'wb')
                                f.write( data )
                                f.close()
                        elif t == u'Apple PDF pasteboard type':
                            if doPDF:
                                f = open ( fname + ".pdf", 'wb')
                                f.write( data )
                                f.close()
    winref.visible.set(False)

def iterwindows():
    dbs = get_fmp_docs()
    outpath = os.path.abspath("./")

    for db in dbs:
        db.show()
        w = db.windows[1]()
        w.show()
        w.go_to()
        name = w.name()

        # print "Database: '%s'" % name.encode("utf-8")

        # pdb.set_trace()

        # this one cannot be checked since we could be running under
        # std filemaker, which doesn't have this item
        ok = do_menu_STDMENUS()

        # this MUST be True
        ok = do_menu_LAYOUTMODE()

        layolist = w.layouts()
        # print "layouts:", pp(layolist)

        if ok:
            iter_layouts( w, layolist, outpath )

##################################
#
# FileMaker Section END
#
##################################



if __name__ == "__main__":
    PyObjCTools.AppHelper.runEventLoop()
