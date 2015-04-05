# FileMaker-Layout-Exporter

OSX app to export FileMaker Layouts as PDF &amp; XML.

Tested on OSX 10.6. May work on higher versions but I don't expect ot to run on OSX 10.10.

Tested with FileMaker Pro Advanced Versions 9-11. Higher versions may or may not work.

If the database files do not use custom menus and the "Layout mode" menu item is present,
it may work with "FileMaker Pro".

The application is flaky. Start, expand all, select all, export & quit. **Don't play around**.

I've observed 5%-20% damaged pdf files. The app just does a copy of all layout elements and writes the clipboard contents into a file.

The source code is in a horrible state and the outline code is buggy. Usually I need this app once per project, so the incentive for a more polished app is near zero. YMMV.


## Download
dropbox: http://goo.gl/AZVMVj


## Usage

+ Make sure that you use "FileMaker Pro Advanced". If you can open all files and put them into layout mode, it should work with "FileMaker Pro".

+ Make sure you have a backup of the databases.

+ Start your FileMaker database with **[Full Access]** and make sure all files are open.

+ Start FMPLayoutExporter

+ The app will iterate through all the database files and switch them to layout mode.

+ A window will open with an outline of all the database files.

+ press cmd-a (select all), right arrow (expand outline nodes), cmd-a

+ click "Export"

+ A dialog opens. Select an empty folder where the export should go. Click "Export".

+ **WARNING:** If the folder is not empty, identical filenames will be overwritten without asking.

+ For each layout selected in the outline, 2 files will be created:
DBNAME_LAYOUTINDEX_LAYOUTNAME.pdf and
DBNAME_LAYOUTINDEX_LAYOUTNAME.xml

+ Quit the application.

## How does it work?

The app is written in Python with py2app & PyObjc. It controls FileMaker via AppleEvents.

On launch, the app detects a running FileMaker, gets it's documents, tries to go to layout mode for each document and finally opens it's own window with with an outline of the files & layouts to select.

At export it goes to each layout of each document, does a "select all" & copy, extracts the PDF and XML data from the pasteboard and writes them into files.

A note: when copying items in FileMaker layouts, FileMaker places several data formats on the pasteboard (which was called clipboard in it's former incarnation). It used to XML, PDF & PICT (the classic Mac image format). With FileMaker 11 this has been reduced to XML & PDF; PICT has been deprecated for many years. FMPLayoutExporter tells FileMaker to select all layout items and copy them and looks at what FileMaker has put on the pasteboard. If it finds the types for XML and/or PDF, they will be written into files.

For this to work, the Filemaker application needs to be set to the english or german language. FMPLayoutExporter literally tells Filemaker to "select menu item "Copy" of menu "Edit". So all those necessary menus must be present and selectable. 

FMPLayoutExporter can be made to work with other languages as long as the exact wording for "Edit", "Select All", "Copy", "View", Layout Mode", "Tools", "Custom Menus" and "[Standard FileMaker Menus]" are known.


## Compiling

Install

+ Python 2.7 (2.7.9 is current) <https://www.python.org/downloads/>

+ py2app <https://pythonhosted.org/py2app/install.html>

+ PyObjC <http://pythonhosted.org/pyobjc/install.html>

+ In Terminal do```
python setup.py py2app
``` in the source folder.

## Changes

+ v0.1.0 2015-04-04 - OSX 10.6, pyobjc 3.1 update of a 8 year old beginners project 

+ v0.2.0 2015-04-05 - Completely replaced the outline internals. Selection now works.
