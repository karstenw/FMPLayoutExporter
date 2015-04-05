"""PythonBrowserModel.py -- module implementing the data model for PythonBrowser."""



import pdb
import pprint
pp = pprint.pprint
kwdbg = False
kwlog = True


import Foundation
NSObject = Foundation.NSObject

NSMutableArray = Foundation.NSMutableArray

NSNotFound = Foundation.NSNotFound
NSIndexSet = Foundation.NSIndexSet

NSNumber = Foundation.NSNumber


import AppKit
NSString = AppKit.NSString
NSMutableString = AppKit.NSMutableString


class PythonBrowserModel(Foundation.NSObject):
    """This is a delegate as well as a data source for NSOutlineViews."""

    def initWithObject_(self, obj):
        self = self.init()
        # pdb.set_trace()
        self.setObject_( None )
        for db in obj:
            # (name, db, win, parent, rootNode)
            dbnode = OutlineNode(db, db, "window", self.root, self.root)
            self.root.addChild_( dbnode )
            for layitem in obj[db]:
                id_,layname = layitem
                cnode = OutlineNode(layname, db, id_, dbnode, self.root)
                dbnode.addChild_( cnode )
        return self

    def setObject_(self, obj):
        self.root = OutlineNode("root", "", "", None, None)

    # NSOutlineViewDataSource  methods
    def outlineView_numberOfChildrenOfItem_(self, view, item):
        if item is None:
            item = self.root
        return item.noOfChildren()

    def outlineView_child_ofItem_(self, view, child, item):
        if not item:
            item = self.root
        return item.childAtIndex_( child )

    def outlineView_isItemExpandable_(self, view, item):
        if item is None:
            item = self.root
        return item.isExpandable()

    def outlineView_objectValueForTableColumn_byItem_(self, view, col, item):
        c = col.identifier()
        # TODO: COLUMNWORK
        if not item:
            item = self.root
        return item.name

    def outlineView_setObjectValue_forTableColumn_byItem_(self, view, value, col, item):
        if not item:
            return
        if value != item.name:
            item.setName_(value)

    def outlineView_shouldEditTableColumn_item_(self, view, col, item):
        """Can item be edited?"""
        return False

    def outlineView_shouldSelectTableColumn_(self, view, col):
        return False

    def outlineView_shouldSelectItem_(self, view, item):
        return True

    def getSelectionItems(self):
        if kwlog:
            print "getSelectionItems"
        """The actual nodes of the current selection are returned."""
        sel = self.selectedRowIndexes()
        result = []
        n = 0
        if sel:
            n = sel.count()
            if not n:
                return result
        next = sel.firstIndex()
        result.append( self.itemAtRow_(next) )

        for i in range(1, n):
            next = sel.indexGreaterThanIndex_(next)
            result.append( self.itemAtRow_(next) )
        return result


class OutlineNode(NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to OutlineNode instances
    # without retaining them. If we don't make sure they don't get
    # garbage collected, the app will crash. For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    # attributes of OutlineNode:
    # name
    # value
    # comment
    # type
    # parent
    # children
    #
    # displayValue
    #

    #
    # to be added
    #
    # nodeAttributes

    # that's the deal
    def __new__(cls, *args, **kwargs):
        return cls.alloc().init()

    def __init__(self, name, db, win, parent, rootNode):

        # this is outlinetype, not valueType
        self.name = name
        self.dbref = db
        self.winref = win
        self.parent = parent

        # these must exists before any name/value is set
        self.children = NSMutableArray.arrayWithCapacity_( 200 )

        # leave this here or bad things will happen
        self.retain()

    def __repr__(self):
        return "<OutlineNode(name='%s')" % (self.name,)

    def dealloc(self):
        print "OutlineNode.dealloc()"
        # pp(self.__dict__)
        self.children.release()

        # 2013-05-15
        # currently crashes during dict dealloc.
        # seems like I'm on the right way to deallocation...
        psolved = False
        if psolved:
            super(OutlineNode, self).dealloc()

    def noOfChildren(self):
        return self.children.count()

    def addChild_(self, child):
        if kwlog and 0:
            print "OutlineNode.addChild_", child
        # retain: child+1
        if isinstance(child, OutlineNode):
            if child.parent != self:
                child.parent = self
            self.children.addObject_( child )
            # child.release()

    def addChild_atIndex_(self, child, index):
        if kwdbg:
            print "addChild_atIndex_setParent", child
        self.children.insertObject_atIndex_( child, index)
        child.parent = self

    def childAtIndex_( self, index ):
        # delegeate child getter
        if index <= self.children.count():
            return self.children.objectAtIndex_( index )
        return None

    def isExpandable(self):
        return self.children.count() > 0

    def isRoot(self):
        return self.parent == None
