# FileMaker-Layout-Exporter
OSX app to export FileMaker Layouts as PDF &amp; XML.

Tested on OSX 10.6. May work on higher versions but I don't expect ot to run on OSX 10.10.

Tested with FileMaker Pro Advanced Versions 9-11. Higher versions may or may not work.

If the database files do not use custom menus and the "Layout mode" menu item is present,
it may work with "FileMaker Pro".

The application is flaky. The layout selection does not work right. Start, expand all, select all, export & quit. **Don't play around**.

I've observed 5%-20% damaged pdf files. The app just does a copy of all layout elements and writes the clipboard contents into a file.

The source code is in a horrible state and the outline code is buggy. Usually I need this app once per project, so the incentive for a more polished app is near zero. YMMV.


## Download (goes to dropbox)
http://goo.gl/AZVMVj


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

## What is it good for?

The important part 