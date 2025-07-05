# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os

import struct

import unicodedata

import functools
cmp_to_key = functools.cmp_to_key

import pdb
import pprint
pp = pprint.pprint

# py3 stuff

py3 = False
try:
    unicode('')
    punicode = unicode
    pstr = str
    punichr = unichr
except NameError:
    punicode = str
    pstr = bytes
    py3 = True
    punichr = chr


__all__ = [
    "cmp_to_key", "sortlist", "dotprinter", "makeunicode", "makeunicodelist"
]


def sortlist(thelist, thecompare):
    if py3:
        sortkeyfunction = cmp_to_key( thecompare )
        thelist.sort( key=sortkeyfunction )
    else:
        thelist.sort( thecompare )


def dotprinter( count, scale=1000 ):
    dot = scale
    line = scale*100
    block = line * 5
    if count % dot == 0:
        sys.stdout.write(".")
        if count % line == 0:
            sys.stdout.write( "  " + str(count) )
            sys.stdout.write("\n")
            if count % block == 0:
                sys.stdout.write("\n")
        sys.stdout.flush()


def makeunicode(s, srcencoding="utf-8", normalizer="NFC"):
    if type(s) not in (punicode, pstr):
        s = str( s )
    if type(s) != punicode:
        s = punicode(s, srcencoding)
    s = unicodedata.normalize(normalizer, s)
    return s


def makeunicodelist(l, srcencoding="utf-8", normalizer="NFC"):
    result = []
    for item in l:
        s = makeunicode( item, srcencoding=srcencoding,  normalizer=normalizer)
        result.append( s )
    return result


