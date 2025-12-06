"""
Script for building the application.

Usage:
    python setup.py py2app -gx -O2
"""
import os

from distutils.core import setup
import py2app

appname = "FileMaker Layout Eporter"
appnameshort = "FMPLayoutexporter"
version = "V0.3.1"

copyright = u"Copyright 2009-2025 Karsten Wolf"

infostr = appname + u' ' + version + u' ' + copyright



setup(
    app=[{
        'script': "FMPLayoutexporter.py",

        'plist':{
            'CFBundleGetInfoString': infostr,
            'CFBundleIdentifier': 'org.kw.Layoutexporter',
            'CFBundleShortVersionString': version,
            'CFBundleDisplayName': appnameshort,
            'CFBundleName': appnameshort,
            'CFBundleSignature': 'KWLe',
            'LSHasLocalizedDisplayName': False,
            'NSAppleScriptEnabled': False,
            'NSHumanReadableCopyright': copyright}}],

    data_files=["English.lproj/MainMenu.nib",
                "English.lproj/OutlineWindow.nib",
                "Icon.icns"],
    options={
        'py2app':{
            'iconfile': "Icon.icns",
            "excludes": [
                'TkInter', 'tkinter', 'tk', 'wx', 'sphinx',
                'pyqt5', 'qt5', 'PyQt5', 
                
                'setuptools', 'numba', 
                
                # 'certifi', 'pytz', 
                'notebook', 'nbformat', 'jedi', 'testpath', 'docutils',
                'ipykernel', 'parso', 'Cython', 'sphinx_rtd_theme', 'alabaster',
                'tornado', 'IPython', 'numpydoc', 'nbconvert', 
                'scipy', 'matplotlib', 
                'pandas', 'cv2', 'dlib', 'skimage', 'sklearn', 'mpl_toolkits', 
            ],
        },
    },
)
