"""PythonBrowserModel.py -- module implementing the data model for PythonBrowser."""

import sys
import pdb
import pprint
pp = pprint.pprint
kwdbg = False

import Foundation
import AppKit

from operator import getitem, setitem


class DBDict(object):
    def __init__(self, parent):
        self.d = dict()
        self.k = list()
        self.parent = parent

    def __repr__(self):
        """

        Arguments:
        - `self`:
        """
        s = self.d.__repr__()
        return ", ".join( (str(self.parent), str(s)) )

    def set_key_value(self, k, v):
        if k in self.k:
            self.k.remove(k)

        self.d[k] = v
        self.k.append(k)

    def get_value_for_key(self, key):
        if key in self.k:
            return self.d[key]
        else:
            raise KeyError

    def keys(self):
        return self.k[:]

class PythonBrowserModel(Foundation.NSObject):
    """This is a delegate as well as a data source for NSOutlineViews."""

    def initWithObject_(self, obj):
        self = self.init()
        self.setObject_(obj)
        return self

    def setObject_(self, obj):
        self.root = PythonItem("<root>", obj, None, None)

    # NSOutlineViewDataSource  methods
    def outlineView_numberOfChildrenOfItem_(self, view, item):
        if item is None:
            item = self.root
        return len(item)

    def outlineView_child_ofItem_(self, view, child, item):
        if item is None:
            item = self.root
        return item.getChild(child)

    def outlineView_isItemExpandable_(self, view, item):
        if item is None:
            item = self.root
        return item.isExpandable()

    def outlineView_objectValueForTableColumn_byItem_(self, view, col, item):
        """Get data for column, item"""
        if item is None:
            item = self.root
        val = getattr(item, col.identifier())
        return val

    def outlineView_setObjectValue_forTableColumn_byItem_(self, view, value, col, item):
        """User set data for column, item"""
        assert col.identifier() == "value"
        if item.value == value:
            return
        try:
            obj = eval(value, {})
        except:
            AppKit.NSBeep()
            print "XXX Error:", sys.exc_info()
            print "XXX      :", repr(value)
        else:
            item.setValue(obj)

    # delegate method
    def outlineView_shouldEditTableColumn_item_(self, view, col, item):
        """Can item be edited?"""
        return item.isEditable()

    # kw for fmphelper
    def outlineView_shouldSelectTableColumn_(self, view, col):
        return False

    def outlineView_shouldSelectItem_(self, view, item):
        # print "Item select:", item.name.encode("utf-8"), item.type.encode("utf-8")
        item.selection = True # not item.selection
        return True # not item.type == 'dict'

    def getSelection(self):
        pass

# objects of these types are not eligable for expansion in the outline view
SIMPLE_TYPES = (str, unicode, int, long, float, complex, type(None), bool)

def getInstanceVarNames(obj):
    """Return a list the names of all (potential) instance variables."""
    # Recipe from Guido
    slots = {}
    if hasattr(obj, "__dict__"):
        slots.update(obj.__dict__)
    if hasattr(obj, "__class__"):
        slots["__class__"] = 1
    cls = getattr(obj, "__class__", type(obj))
    if hasattr(cls, "__mro__"):
        for base in cls.__mro__:
            for name, value in base.__dict__.items():
                # XXX using callable() is a heuristic which isn't 100%
                # foolproof.
                if hasattr(value, "__get__") and not callable(value) and \
                        hasattr(obj, name):
                    slots[name] = 1
    if "__dict__" in slots:
        del slots["__dict__"]
    slots = slots.keys()
    slots.sort()
    return slots

class NiceError:
    """Wrapper for an exception so we can display it nicely in the browser."""

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def __repr__(self):
        from traceback import format_exception_only
        lines = format_exception_only(*self.exc_info[:2])
        assert len(lines) == 1
        error = lines[0].strip()
        return "*** error *** %s" %error

class PythonItem(Foundation.NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to PythonItem instances
    # without retaining them. If we don't make sure they don't get
    # garbage collected, the app will crash. For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    def __new__(cls, *args, **kwargs):
        # "Pythonic" constructor
        return cls.alloc().init()

    def __init__(self, name, obj, parent, setvalue):
        self.realName = name
        self.name = unicode(name) #.encode("utf-8")
        self.parent = parent
        # kwchange for selection
        self.selection = False
        self._setValue = setvalue
        self.type = type(obj).__name__
        try:
            # XXX [:256] makes it quite a bit faster for long reprs.
            self.value = repr(obj)[:256]
            assert isinstance(self.value, str)
        except:
            self.value = repr(NiceError(sys.exc_info()))
        self.object = obj
        self.childrenEditable = 0

        if isinstance(obj, dict):
            self.children = obj.keys()
            self.children.sort()
            self._getChild = getitem
            self._setChild = setitem
            self.childrenEditable = 1

        elif obj is None or isinstance(obj, SIMPLE_TYPES):
            self._getChild = None
            self._setChild = None

        elif isinstance(obj, (list, tuple)):
            self.children = range(len(obj))
            self._getChild = getitem
            self._setChild = None
            #if isinstance(obj, list):
            #    self.childrenEditable = 1

        elif isinstance(obj, DBDict):
            self.children = obj.keys()
            self._getChild = DBDict.get_value_for_key
            self._setChild = None

            # XXX we don't know that...
            self.childrenEditable = 1


        else:
            self.children = getInstanceVarNames(obj)
            self._getChild = getattr
            self._setChild = setattr

            # XXX we don't know that...
            self.childrenEditable = 1

        self._childRefs = {}


    def setValue(self, value):
        self._setValue(self.parent, self.realName, value)
        self.__init__(self.realName, value, self.parent, self._setValue)

    def isEditable(self):
        return self._setValue is not None

    def isExpandable(self):
        return self._getChild is not None

    def getChild(self, child):
        if self._childRefs.has_key(child):
            return self._childRefs[child]

        name = self.children[child]
        try:
            obj = self._getChild(self.object, name)
        except:
            obj = NiceError(sys.exc_info())

        if self.childrenEditable:
            childObj = PythonItem(name, obj, self.object, self._setChild)
        else:
            childObj = PythonItem(name, obj, None, None)

        self._childRefs[child] = childObj
        return childObj

    def __len__(self):
        return len(self.children)
