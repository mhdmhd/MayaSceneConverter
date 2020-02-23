# Copyright 2020 by Mahmoud El-Ashry. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.
"""
Drag and drop for Maya 2018+
"""
import os
import sys

try:
    import maya.mel
    import maya.cmds

    isMaya = True
except ImportError:
    isMaya = False


def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""

    srcPath = os.path.dirname(__file__)
    iconPath = os.path.join(srcPath, 'icon.png')

    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)

    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)

    for path in sys.path:
        if os.path.exists(path + '/MayaSceneConverter/__init__.py'):
            maya.cmds.warning('Maya Scene Converter is already installed at ' + path)

    command = '''
# -----------------------------------
# Maya Scene Converter
# -----------------------------------

import os
import sys
    
if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')
    
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')
    
import ConverterUI
ConverterUI.ConverterUI()
'''.format(path=srcPath)

    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)
    maya.cmds.shelfButton(
        command=command,
        annotation='Maya Scene Converter',
        sourceType='Python',
        image=iconPath,
        image1=iconPath,
        parent=parent
    )

    # print("\n// Maya Scene Converter has been added to current shelf.")


if isMaya:
    _onMayaDropped()
