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

import os

import maya.cmds as cmds
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance

import Converter as Conv
reload(Conv)

script_dir = os.path.dirname(__file__)

from Qt import QtWidgets, QtCore, QtGui


class ConverterUI(QtWidgets.QWidget):

    def __init__(self):
        self.ui_name = 'Scene Converter'
        parent = getDock(QtWidgets.QWidget, self.ui_name + 'Dock', self.ui_name)
        super(ConverterUI, self).__init__(parent)

        self.Converter = Conv.ConverterClass()

        self.build_ui()
        self.populate_ui()
        self.parent().layout().addWidget(self)

    def build_ui(self):
        self.resize(400, 120)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.selection_layout = QtWidgets.QHBoxLayout()
        self.rules_box = QtWidgets.QComboBox(self)
        self.selection_layout.addWidget(self.rules_box)
        self.refresh_button = QtWidgets.QPushButton(self)
        self.refresh_button.clicked.connect(self.populate_ui)
        self.refresh_button.setMaximumSize(QtCore.QSize(50, 16777215))
        self.selection_layout.addWidget(self.refresh_button)
        self.verticalLayout.addLayout(self.selection_layout)

        self.checks_layout = QtWidgets.QHBoxLayout()
        self.lights_check = QtWidgets.QCheckBox(self)
        self.lights_check.setChecked(True)
        self.checks_layout.addWidget(self.lights_check)
        self.material_check = QtWidgets.QCheckBox(self)
        self.material_check.setChecked(True)
        self.checks_layout.addWidget(self.material_check)
        self.selected_check = QtWidgets.QCheckBox(self)
        self.checks_layout.addWidget(self.selected_check)
        self.verticalLayout.addLayout(self.checks_layout)

        self.in_render_check = QtWidgets.QCheckBox(self)
        self.in_render_check.setChecked(True)
        self.verticalLayout.addWidget(self.in_render_check)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.convert_button = QtWidgets.QPushButton(self)
        self.convert_button.clicked.connect(self.convert)
        self.convert_button.setMinimumSize(QtCore.QSize(0, 40))
        self.buttons_layout.addWidget(self.convert_button)
        self.editor_button = QtWidgets.QPushButton(self)
        self.editor_button.clicked.connect(self.editor)
        self.editor_button.setMinimumSize(QtCore.QSize(0, 40))
        self.buttons_layout.addWidget(self.editor_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.web_link = QtWidgets.QLabel(self)
        url_link1 = "<a href=\"https://www.linkedin.com/in/mahmoud-el-ashry-29324020/\" style=\"color: grey;\">'Linkedin'</a>"
        url_link2 = "<a href=\"https://www.artstation.com/mhdmhd\" style=\"color: grey;\">'Artsation'</a>"
        self.web_link.setText(url_link1 + '\t\t' + url_link2)
        self.web_link.setOpenExternalLinks(True)
        self.web_link.setAlignment(QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.web_link)

        self.refresh_button.setText("Refresh")
        self.lights_check.setText("Lights")
        self.material_check.setText("Materials")
        self.selected_check.setText("Selected Only")
        self.in_render_check.setText("Selected Render Engine Only")
        self.convert_button.setText("Convert")
        self.editor_button.setText("Editor")

    def populate_ui(self):
        self.rules_box.clear()
        file_names = self.Converter.get_filenames(script_dir + '/Rules')
        self.rules_box.addItems(file_names)

    def editor(self):
        editor = EditorUI(self)
        editor.show_ui()

    def convert(self):
        lights = self.lights_check.isChecked()
        materials = self.material_check.isChecked()
        selected = self.selected_check.isChecked()
        in_render = self.in_render_check.isChecked()
        file_name = self.rules_box.currentText()
        self.Converter.convert_scene(file_name, lights=lights, materials=materials,
                                     selected=selected, in_render=in_render)


class EditorUI(QtWidgets.QWidget):

    def __init__(self, parent):

        self.ui_name = 'Editor'

        super(EditorUI, self).__init__(parent)
        self.newWindow = QtWidgets.QDialog(parent=parent)

        self.Converter = parent.Converter

        self.build_ui()
        self.populate_ui()

        # ---------------------------

    def show_ui(self):
        self.newWindow.show()  # exec_() > modal

    def build_ui(self):
        self.newWindow.resize(1400, 800)
        self.newWindow.setWindowTitle(self.ui_name)
        self.all_layout = QtWidgets.QVBoxLayout(self.newWindow)
        self.main_widget = QtWidgets.QWidget(self.newWindow)
        self.main_Layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.main_Layout.setContentsMargins(0, 0, 0, 0)

        self.render_in_Layout = QtWidgets.QVBoxLayout()
        self.render_in_box = QtWidgets.QComboBox(self.main_widget)
        self.render_in_box.currentIndexChanged.connect(self.populate_render_in)
        self.render_in_Layout.addWidget(self.render_in_box)

        self.checks_layout_in = QtWidgets.QHBoxLayout()

        self.inherited_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.inherited_check_in.setText("Inherited")
        self.inherited_check_in.setChecked(True)
        self.inherited_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.inherited_check_in)

        self.maps_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.maps_check_in.setText("Float3")
        self.maps_check_in.setChecked(True)
        self.maps_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.maps_check_in)

        self.float_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.float_check_in.setText("Float")
        self.float_check_in.setChecked(True)
        self.float_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.float_check_in)

        self.integer_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.integer_check_in.setText("Integer")
        self.integer_check_in.setChecked(True)
        self.integer_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.integer_check_in)

        self.bool_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.bool_check_in.setText("Bool")
        self.bool_check_in.setChecked(True)
        self.bool_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.bool_check_in)

        self.other_check_in = QtWidgets.QCheckBox(self.main_widget)
        self.other_check_in.setText("Other")
        self.other_check_in.setChecked(True)
        self.other_check_in.stateChanged.connect(self.populate_render_in)
        self.checks_layout_in.addWidget(self.other_check_in)

        self.expand_button_in = QtWidgets.QPushButton(self.main_widget)
        self.expand_button_in.setText("+")
        self.expand_button_in.setMaximumSize(25, 25)
        self.checks_layout_in.addWidget(self.expand_button_in)

        self.collapse_button_in = QtWidgets.QPushButton(self.main_widget)
        self.collapse_button_in.setText("-")
        self.collapse_button_in.setMaximumSize(25, 25)
        self.checks_layout_in.addWidget(self.collapse_button_in)

        self.render_in_Layout.addLayout(self.checks_layout_in)

        self.render_in_tree = QtWidgets.QTreeWidget(self.main_widget)
        self.render_in_tree.setAutoFillBackground(True)
        self.render_in_tree.setAlternatingRowColors(True)
        self.render_in_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.render_in_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.render_in_tree.setColumnCount(3)
        self.render_in_tree.setHeaderHidden(True)

        self.render_in_Layout.addWidget(self.render_in_tree)

        self.main_Layout.addLayout(self.render_in_Layout)

        self.render_out_Layout = QtWidgets.QVBoxLayout()
        self.render_out_box = QtWidgets.QComboBox(self.main_widget)
        self.render_out_box.currentIndexChanged.connect(self.populate_render_out)
        self.render_out_Layout.addWidget(self.render_out_box)

        self.checks_layout_out = QtWidgets.QHBoxLayout()

        self.inherited_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.inherited_check_out.setText("Inherited")
        self.inherited_check_out.setChecked(True)
        self.inherited_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.inherited_check_out)

        self.maps_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.maps_check_out.setText("Float3")
        self.maps_check_out.setChecked(True)
        self.maps_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.maps_check_out)

        self.float_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.float_check_out.setText("Float")
        self.float_check_out.setChecked(True)
        self.float_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.float_check_out)

        self.integer_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.integer_check_out.setText("Integer")
        self.integer_check_out.setChecked(True)
        self.integer_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.integer_check_out)

        self.bool_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.bool_check_out.setText("Bool")
        self.bool_check_out.setChecked(True)
        self.bool_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.bool_check_out)

        self.other_check_out = QtWidgets.QCheckBox(self.main_widget)
        self.other_check_out.setText("Other")
        self.other_check_out.setChecked(True)
        self.other_check_out.stateChanged.connect(self.populate_render_out)
        self.checks_layout_out.addWidget(self.other_check_out)

        self.expand_button_out = QtWidgets.QPushButton(self.main_widget)
        self.expand_button_out.setText("+")
        self.expand_button_out.setMaximumSize(25, 25)
        self.checks_layout_out.addWidget(self.expand_button_out)

        self.collapse_button_out = QtWidgets.QPushButton(self.main_widget)
        self.collapse_button_out.setText("-")
        self.collapse_button_out.setMaximumSize(25, 25)
        self.checks_layout_out.addWidget(self.collapse_button_out)

        self.render_out_Layout.addLayout(self.checks_layout_out)

        self.render_out_tree = QtWidgets.QTreeWidget(self.main_widget)
        self.render_out_tree.setAutoFillBackground(True)
        self.render_out_tree.setAlternatingRowColors(True)
        self.render_out_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.render_out_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.render_out_tree.setColumnCount(3)
        self.render_out_tree.setHeaderHidden(True)
        self.render_out_Layout.addWidget(self.render_out_tree)
        self.main_Layout.addLayout(self.render_out_Layout)

        self.match_widget = QtWidgets.QWidget(self.main_widget)
        self.match_layout = QtWidgets.QVBoxLayout(self.match_widget)

        self.match_button = QtWidgets.QPushButton(self.main_widget)
        self.match_button.setMinimumSize(15, 600)
        self.match_button.setMaximumSize(25, 700)
        self.match_button.clicked.connect(self.match_selection)
        self.match_layout.addWidget(self.match_button)

        self.main_Layout.addWidget(self.match_widget)

        self.render_tree = QtWidgets.QTreeWidget(self.main_widget)
        self.render_tree.setAutoFillBackground(True)
        self.render_tree.setAlternatingRowColors(True)
        self.render_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.render_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.render_tree.setColumnCount(4)
        self.render_tree.setHeaderLabels(['In', 'Out', 'Type', 'Factor'])
        self.render_tree.itemClicked.connect(self.select_source)
        self.main_Layout.addWidget(self.render_tree)

        self.all_layout.addWidget(self.main_widget)

        self.buttons_widget = QtWidgets.QWidget(self.main_widget)
        self.buttons_layout = QtWidgets.QVBoxLayout(self.buttons_widget)

        self.delete_button = QtWidgets.QPushButton(self.buttons_widget)
        self.delete_button.clicked.connect(self.remove_selected)
        self.buttons_layout.addWidget(self.delete_button)
        self.clear_button = QtWidgets.QPushButton(self.buttons_widget)
        self.clear_button.clicked.connect(self.clear_all)
        self.buttons_layout.addWidget(self.clear_button)

        self.inverse_button = QtWidgets.QPushButton(self.buttons_widget)
        self.inverse_button.clicked.connect(self.add_inverse)
        self.buttons_layout.addWidget(self.inverse_button)

        self.override_button = QtWidgets.QPushButton(self.buttons_widget)
        self.override_button.clicked.connect(self.add_override)
        self.buttons_layout.addWidget(self.override_button)

        self.remove_button = QtWidgets.QPushButton(self.buttons_widget)
        self.remove_button.clicked.connect(self.remove_override)
        self.buttons_layout.addWidget(self.remove_button)

        spacerItemB = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addItem(spacerItemB)

        self.save_button = QtWidgets.QPushButton(self.buttons_widget)
        self.save_button.clicked.connect(self.save_file)
        self.buttons_layout.addWidget(self.save_button)
        self.load_button = QtWidgets.QPushButton(self.buttons_widget)
        self.load_button.clicked.connect(self.load_file)
        self.buttons_layout.addWidget(self.load_button)

        spacerItemC = QtWidgets.QSpacerItem(20, 500, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addItem(spacerItemC)

        self.main_Layout.addWidget(self.buttons_widget)

        self.expand_button_in.clicked.connect(self.render_in_tree.expandAll)
        self.collapse_button_in.clicked.connect(self.render_in_tree.collapseAll)
        self.expand_button_out.clicked.connect(self.render_out_tree.expandAll)
        self.collapse_button_out.clicked.connect(self.render_out_tree.collapseAll)

        self.match_button.setText(">")
        self.delete_button.setText("Delete selected")
        self.clear_button.setText("Clear All")
        self.save_button.setText("Save")
        self.load_button.setText("Load")
        self.inverse_button.setText("Inverse Value")
        self.override_button.setText("Override Value")
        self.remove_button.setText("Remove Value")

    def populate_ui(self):

        render_engines = self.Converter.render_engines
        self.render_in_box.addItems(render_engines)
        self.render_out_box.addItems(render_engines)
        current_renderer = self.Converter.current_engine
        self.render_in_box.setCurrentText(current_renderer)

        self.populate_render_in()
        self.populate_render_out()

    def populate_render_in(self):
        inherited = self.inherited_check_in.isChecked()
        others = self.other_check_in.isChecked()

        checks_dic = {'float3': self.maps_check_in.isChecked(), 'float': self.float_check_in.isChecked(),
                      'long': self.integer_check_in.isChecked(),
                      'bool': self.bool_check_in.isChecked()}

        render_in = self.render_in_box.currentText()
        render_dic = self.get_nodes_types(render_in)

        excluded_types = []
        for key, value in checks_dic.items():
            if not value:
                excluded_types.append(key)
        if render_in != '':
            self.populate_render_trees(self.render_in_tree, render_dic, inherited, others, excluded_types)

    def populate_render_out(self):
        inherited = self.inherited_check_out.isChecked()
        others = self.other_check_out.isChecked()

        checks_dic = {'float3': self.maps_check_out.isChecked(), 'float': self.float_check_out.isChecked(),
                      'long': self.integer_check_out.isChecked(),
                      'bool': self.bool_check_out.isChecked()}

        render_out = self.render_out_box.currentText()
        render_dic = self.get_nodes_types(render_out)

        excluded_types = []
        for key, value in checks_dic.items():
            if not value:
                excluded_types.append(key)
        if render_out != '':
            self.populate_render_trees(self.render_out_tree, render_dic, inherited, others, excluded_types)

    def get_nodes_types(self, render_engine):

        node_types = ['shader', 'light', 'texture', 'utility']
        render_in_dic = {}
        for node_type in node_types:
            render_in_nodes = self.Converter.get_type_nodes(render_engine, node_type)
            render_in_dic[node_type] = render_in_nodes
        return render_in_dic

    def resize_trees(self, tree_widget):

        tree_widget.expandAll()
        count = tree_widget.columnCount()
        for i in range(0, count):
            tree_widget.resizeColumnToContents(i)
        tree_widget.sortItems(0, QtCore.Qt.AscendingOrder)
        # tree_widget.collapseAll()

    def select_source(self):
        in_item = self.render_tree.currentItem().text(0)
        out_item = self.render_tree.currentItem().text(1)

        in_item_parent = self.render_tree.currentItem().parent()
        out_item_parent = self.render_tree.currentItem().parent()

        in_items = self.render_in_tree.findItems(in_item, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if in_items:
            for item in in_items:
                if in_item_parent is not None:
                    if item.parent().text(0) == in_item_parent.text(0):
                        self.render_in_tree.setCurrentItem(item)
                else:
                    self.render_in_tree.setCurrentItem(item)

        out_items = self.render_out_tree.findItems(out_item, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if out_items:
            for item in out_items:
                if out_item_parent is not None:
                    if item.parent().text(0) == out_item_parent.text(1):
                        self.render_out_tree.setCurrentItem(item)
                else:
                    self.render_out_tree.setCurrentItem(item)

    def populate_render_trees(self, tree_widget, render_nodes, inherited, others, excluded_types):
        tree_widget.clear()

        for node_type, nodes in render_nodes.items():
            parent_item = QtWidgets.QTreeWidgetItem([node_type])
            tree_widget.addTopLevelItem(parent_item)
            for node in nodes:
                child_item = QtWidgets.QTreeWidgetItem([node])
                for c in range(0, child_item.columnCount()):
                    child_item.setForeground(c, QtGui.QBrush(QtGui.QColor(250, 180, 120)))
                parent_item.addChild(child_item)
                node_attributes = self.Converter.get_type_attributes(node, inherited, others, excluded_types)
                for node_attribute, node_info in node_attributes.items():
                    item = QtWidgets.QTreeWidgetItem([node_attribute, node_info])
                    child_item.addChild(item)
                    if node_info == 'float3':
                        item.setForeground(0, QtGui.QBrush(QtGui.QColor(250, 120, 120)))
                        attibute_children = self.Converter.get_attribute_children(node_attribute, node)
                        if attibute_children:
                            for child_attribute in attibute_children:
                                child_attribute_item = QtWidgets.QTreeWidgetItem([child_attribute, 'float'])
                                item.addChild(child_attribute_item)
                                child_attribute_item.setHidden(True)

        self.resize_trees(tree_widget)

    def get_parent_item(self, in_attribute, out_attribute):
        # Search for existing parent nodes if not then create new one.
        items = self.render_tree.findItems(in_attribute.text(0), QtCore.Qt.MatchExactly, 0)
        if items:
            parent_item = items[0]
        else:
            parent_item = QtWidgets.QTreeWidgetItem([in_attribute.text(0), out_attribute.text(0)])
        return parent_item

    def get_child_item(self, parent_item, in_attribute, out_attribute):
        # Search for existing child attributes but only in the same parent.
        items = self.render_tree.findItems(in_attribute.text(0), QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        item_exists = False
        if items:
            for i in items:
                if parent_item.text(0) == i.parent().text(0):  # Make sure the attribute has the same parent
                    item_exists = True
                    break  # exit the loop because if there is an existing parent there will be no other.
                else:
                    item_exists = False

        if not item_exists:
            item = QtWidgets.QTreeWidgetItem([in_attribute.text(0), out_attribute.text(0), in_attribute.text(1)])
            return item
        else:
            return

    def get_item_children(self, item):
        item_dic = {}
        in_child_count = item.childCount()
        for i in range(in_child_count):
            attr_item = item.child(i)
            item_dic[attr_item.text(0)] = attr_item
        return item_dic

    def count_item_visible_children(self, item):
        visible_child_items = []
        child_count = item.childCount()
        if child_count > 0:
            for i in range(0, child_count):
                child_item = item.child(i)
                if not child_item.isHidden():
                    visible_child_items.append(child_item)
        return len(visible_child_items)

    def match_selection(self):

        in_item = self.render_in_tree.currentItem()
        out_item = self.render_out_tree.currentItem()
        parent_item = None
        if in_item is not None and out_item is not None:
            # Make sure both selections are the same type.
            if in_item.text(1) == out_item.text(1):

                in_item_child_count = self.count_item_visible_children(in_item)
                out_item_child_count = self.count_item_visible_children(out_item)

                # Check if both selections are attributes by comparing the number of visible children.
                if in_item_child_count == 0 and out_item_child_count == 0:

                    attr_in_parent = self.render_in_tree.currentItem().parent()
                    attr_out_parent = self.render_out_tree.currentItem().parent()
                    parent_item = self.get_parent_item(attr_in_parent, attr_out_parent)
                    self.render_tree.addTopLevelItem(parent_item)

                    child_item = self.get_child_item(parent_item, in_item, out_item)
                    if child_item is not None:
                        parent_item.addChild(child_item)

                        in_child_item_count = in_item.childCount()
                        out_child_item_count = out_item.childCount()
                        if in_child_item_count == out_child_item_count > 0:
                            for i in range(0, in_child_item_count):
                                in_child_item = in_item.child(i)
                                out_child_item = out_item.child(i)

                                sub_child_item = self.get_child_item(parent_item, in_child_item, out_child_item)
                                if sub_child_item is not None:
                                    parent_item.addChild(sub_child_item)

                # If both selections are parent nodes.
                elif in_item.parent() is not None and out_item.parent() is not None:

                    parent_item = self.get_parent_item(in_item, out_item)
                    self.render_tree.addTopLevelItem(parent_item)

                    #  match same attributes
                    in_attrs_items = self.get_item_children(in_item)
                    out_attrs_items = self.get_item_children(out_item)

                    for attr, item in in_attrs_items.items():
                        if attr in out_attrs_items.keys():
                            child_item = self.get_child_item(parent_item, item, item)
                            if child_item is not None:
                                parent_item.addChild(child_item)
                                for i in range(0, child_item.columnCount()):
                                    child_item.setForeground(i, QtGui.QBrush(QtGui.QColor(100, 100, 100)))

                                in_child_item_count = item.childCount()
                                if in_child_item_count > 0:
                                    for i in range(0, in_child_item_count):
                                        in_child_item = item.child(i)
                                        sub_child_item = self.get_child_item(parent_item, in_child_item, in_child_item)
                                        if sub_child_item is not None:
                                            parent_item.addChild(sub_child_item)
                else:
                    cmds.inViewMessage(amg='In-view message <hl>Wrong Selection</hl>.', pos='topCenter', fade=True)

            else:
                cmds.inViewMessage(amg='In-view message <hl>Incompatible Type</hl>.', pos='topCenter', fade=True)

            self.resize_trees(self.render_tree)
            self.render_tree.expandAll()
            self.set_item_colors()

            self.render_tree.setCurrentItem(parent_item)

    def set_item_colors(self):
        root = self.render_tree.invisibleRootItem()
        node_count = root.childCount()

        for i in range(node_count):
            node_item = root.child(i)
            for c in range(0, node_item.columnCount()):
                node_item.setForeground(c, QtGui.QBrush(QtGui.QColor(250, 180, 120)))
            attr_count = node_item.childCount()
            for a in range(attr_count):
                item = node_item.child(a)
                if item.text(0) == item.text(1):
                    for c in range(0, item.columnCount()):
                        item.setForeground(c, QtGui.QBrush(QtGui.QColor(100, 100, 100)))
                if item.text(2) == 'float3':
                    for c in range(0, item.columnCount()):
                        item.setForeground(c, QtGui.QBrush(QtGui.QColor(250, 120, 120)))

    def save_file(self):
        render_in = self.render_in_box.currentText()
        render_out = self.render_out_box.currentText()
        result_data = {'Engines': [render_in, render_out]}

        root = self.render_tree.invisibleRootItem()
        node_count = root.childCount()

        for i in range(node_count):
            node_item = root.child(i)
            attrs = {node_item.text(0): node_item.text(1)}
            attr_count = node_item.childCount()
            for a in range(attr_count):
                attr_item = node_item.child(a)
                attrs[attr_item.text(0)] = [attr_item.text(1), attr_item.text(2), attr_item.text(3)]
            result_data[node_item.text(0)] = attrs

        file_name = render_in + '_To_' + render_out
        file_path = cmds.fileDialog2(caption='Save File', fileFilter='*.json', fileMode=0,
                                     dir=script_dir + '/Rules/' + file_name + '.json')
        if file_path:
            self.Converter.save_json_file(file_path[0], result_data)

    def load_file(self):
        self.render_tree.clear()
        file_path = cmds.fileDialog2(caption='Load File', fileFilter='*.json', fileMode=1, dir=script_dir + '/Rules/')
        if file_path:
            data = self.Converter.load_json_file(file_path[0])
            for node_name, attr_list in data.items():
                if node_name == 'Engines':
                    self.render_in_box.setCurrentText(attr_list[0])
                    self.render_out_box.setCurrentText(attr_list[1])
                else:
                    parent_item = QtWidgets.QTreeWidgetItem([node_name, attr_list[node_name]])
                    self.render_tree.addTopLevelItem(parent_item)
                    for attr_in, attrs_out in attr_list.items():
                        if attr_in != node_name:
                            attr_out = attrs_out[0]
                            attr_type = attrs_out[1]
                            inverse = attrs_out[2]
                            child_item = QtWidgets.QTreeWidgetItem([attr_in, attr_out, attr_type, inverse])
                            parent_item.addChild(child_item)

            self.resize_trees(self.render_tree)
            self.render_tree.expandAll()
            self.set_item_colors()

    def add_inverse(self):
        for item in self.render_tree.selectedItems():
            if item.text(2) in ['float3', 'float']:
                item.setText(3, 'Inverse')

    def add_override(self):
        value, ok_pressed = QtWidgets.QInputDialog.getDouble(self, "Enter Value", "Override:", 0, 0, 100, 2)
        if ok_pressed:
            for item in self.render_tree.selectedItems():
                item.setText(3, str(value))

    def remove_override(self):
        for item in self.render_tree.selectedItems():
            item.setText(3, '')

    def clear_all(self):
        self.render_tree.clear()

    def remove_selected(self):
        root = self.render_tree.invisibleRootItem()
        for item in self.render_tree.selectedItems():
            (item.parent() or root).removeChild(item)


def getDock(wrap, name, label):
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)
    ctrl = cmds.workspaceControl(name, r=True, rs=True, floating=True, label=label)
    # tabToControl=('ChannelBoxLayerEditor', 1)
    # dockToMainWindow=("right", True)
    qtCtrl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(long(qtCtrl), wrap)
    return ptr
