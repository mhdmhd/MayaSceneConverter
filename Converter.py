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

import json
import os
import traceback

import maya.cmds as cmds

# the name of  render engines differs from their plugins, so this needs to be edited if adding new renderer
render_engines_dic = {'arnold': 'mtoa', 'vray': 'vrayformaya', 'renderman': 'RenderMan_for_Maya',
                      'redshift': 'redshift4maya'}

other_types_list = ['enum', 'double', 'typed', 'compound', 'short',
                   'time', 'double3', 'float2', 'byte', 'fltMatrix', 'char', 'doubleAngle', 'floatLinear',
                   'double2', 'long2', 'doubleLinear', 'matrix', 'double4', 'generic']

mayaLightTypes = ["ambientLight", "pointLight", "spotLight", "areaLight", "directionalLight", "volumeLight"]
ignore_attributes = ['message', 'caching', 'frozen', 'isHistoricallyInteresting', 'nodeState', 'binMembership',
                     'lightData', 'iconName']
ignore_types = ['message', 'compound', 'byte', 'fltMatrix', 'char', 'matrix', 'generic']
script_dir = os.path.dirname(__file__)


class ConverterClass(object):

    def __init__(self):
        self.render_engines = self.get_render_engines()
        self.current_engine = self.get_current_render()
        self.all_plugins_nodes = self.get_all_engines_nodes()

    def get_render_engines(self):
        renders = []
        plugins = cmds.renderer(query=True, namesOfAvailableRenderers=True)
        for plugin in plugins:
            if plugin not in ['mayaHardware2', 'mayaVector', 'turtle']:
                renders.append(plugin)
        return renders

    def is_plugin_loaded(self, plugin):
        loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True)
        if plugin in loaded_plugins:
            return True
        else:
            return False

    def get_current_render(self):
        current_render = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        if current_render not in ['mayaHardware2', 'mayaVector', 'turtle']:
            return current_render
        else:
            return

    def get_engine_nodes(self, engine):
        if engine != 'mayaSoftware':
            render_plugin = render_engines_dic[engine]
            nodes = cmds.pluginInfo(render_plugin, dn=1, query=True)
        else:
            nodes = []
        return nodes

    def get_all_engines_nodes(self):
        all_engines_node = []
        for render_plugin in render_engines_dic.values():
            if self.is_plugin_loaded(render_plugin):
                nodes = cmds.pluginInfo(render_plugin, dn=1, query=True)
                all_engines_node.extend(nodes)
        return all_engines_node

    def get_type_nodes(self, engine, node_type):
        engine_nodes = []
        plugin_nodes = self.get_engine_nodes(engine)
        type_nodes = cmds.listNodeTypes(node_type)
        for node in type_nodes:
            if engine != 'mayaSoftware':
                if node in plugin_nodes:
                    engine_nodes.append(node)
            else:
                if node not in self.all_plugins_nodes:
                    engine_nodes.append(node)
        return engine_nodes

    def get_type_attributes(self, node_type, inherited, others, excluded_types):
        result_attrs = {}
        if inherited:
            type_attrs = cmds.attributeInfo(leaf=False, type=node_type)
        else:
            type_attrs = cmds.attributeInfo(inherited=False, leaf=False, logicalAnd=True, type=node_type)

        if type_attrs is not None:
            for attribute in type_attrs:
                if attribute not in ignore_attributes:
                    attr_type = cmds.attributeQuery(attribute, type=node_type, attributeType=True)
                    if attr_type not in ignore_types and attr_type not in excluded_types:
                        if others:
                            result_attrs[attribute] = attr_type
                        else:
                            if attr_type not in other_types_list:
                                result_attrs[attribute] = attr_type
        return result_attrs

    def get_attribute_children(self, attribute, node_type):
        attr_children = cmds.attributeQuery(attribute, type=node_type, listChildren=True)
        return attr_children

    def get_attribute_list(self, attribute, node_type):
        attr_enum = cmds.attributeQuery(attribute, type=node_type, listEnum=True)
        return attr_enum

    def save_json_file(self, file_path, data):
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    def load_json_file(self, file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data

    def is_target_engine_loaded(self, file_data):
        target_engine = file_data['Engines'][1]
        if target_engine != 'mayaSoftware':
            target_plugin = render_engines_dic[target_engine]
            return self.is_plugin_loaded(target_plugin)
        else:
            return True

    def fetch_attributes(self, file_data, node):
        node_type = cmds.nodeType(node)
        in_node_dic = {}
        out_node_dic = {}
        attributes_dic = {}
        if node_type in file_data.keys():
            attributes = file_data[node_type]
            for attribute in attributes:
                if attribute not in ignore_attributes and attribute != node_type:
                    if not cmds.attributeQuery(attribute, type=node_type, message=True):
                        node_attr = node + '.' + attribute
                        if cmds.connectionInfo(node_attr, isExactDestination=True):
                            source = cmds.connectionInfo(node_attr, sourceFromDestination=True)
                            in_node_dic[attribute] = source
                        elif cmds.connectionInfo(node_attr, isExactSource=True):
                            destinations = cmds.connectionInfo(node_attr, destinationFromSource=True)
                            for destination in destinations:
                                out_node_dic[attribute] = destination
                        attr_value = cmds.getAttr(node_attr)
                        attributes_dic[attribute] = attr_value
        return attributes_dic, in_node_dic, out_node_dic

    def convert_node(self, file_data, in_node):
        if in_node in file_data.keys():
            node_attributes = file_data[in_node]
            out_node = node_attributes[in_node]
            return out_node
        else:
            return

    def convert_attributes(self, file_data, in_node, in_attribute):
        node_attributes = file_data[in_node]
        if in_attribute in node_attributes.keys():
            return node_attributes[in_attribute]
        else:
            return

    def replace_node(self, file_data, in_node, category):
        unconverted_attributes = []
        node_type = cmds.nodeType(in_node)
        out_node_type = self.convert_node(file_data, node_type)
        if out_node_type is not None:
            if category == 'light':
                new_node = cmds.shadingNode(out_node_type, asLight=True)
            elif category == 'texture':
                new_node = cmds.shadingNode(out_node_type, asTexture=True)
            elif category == 'material':
                new_node = cmds.shadingNode(out_node_type, asShader=True)
            elif category == 'utility':
                new_node = cmds.shadingNode(out_node_type, asUtility=True)
            else:
                new_node = cmds.createNode(out_node_type, ss=True)

            if cmds.nodeType(new_node) != 'unknown':

                #  static values ##################################
                in_value_attributes = self.fetch_attributes(file_data, in_node)[0].items()
                for in_attribute, in_value in in_value_attributes:
                    out_attribute_list = self.convert_attributes(file_data, node_type, in_attribute)
                    if out_attribute_list is not None and in_value is not None:
                        out_attribute = out_attribute_list[0]
                        out_attribute_type = out_attribute_list[1]
                        out_attribute_factor = out_attribute_list[2]

                        if isinstance(in_value, (list, dict, tuple)):
                            if len(in_value) == 3:
                                if out_attribute_factor == 'Inverse':
                                    value_a = abs(1 - in_value[0][0])
                                    value_b = abs(1 - in_value[0][1])
                                    value_c = abs(1 - in_value[0][2])
                                elif isfloat(out_attribute_factor):
                                    value_a = float(out_attribute_factor)
                                    value_b = float(out_attribute_factor)
                                    value_c = float(out_attribute_factor)
                                else:
                                    value_a = in_value[0][0]
                                    value_b = in_value[0][1]
                                    value_c = in_value[0][2]

                                print(in_node + '.' + out_attribute + ' is setting to value(list): ',
                                      value_a, value_b, value_c)
                                try:
                                    cmds.setAttr(new_node + '.' + out_attribute, value_a, value_b, value_c,
                                                 type=out_attribute_type)
                                    print('\tValue set successfully \n')
                                except Exception:
                                    print('\tFailed to set value \n')
                                    unconverted_attributes.append(in_node + '.' + out_attribute)
                                    traceback.print_exc()
                        else:
                            if out_attribute_factor == 'Inverse' and isinstance(in_value, float):
                                in_value = abs(1 - in_value)
                            elif isfloat(out_attribute_factor):
                                in_value = float(out_attribute_factor)
                            print(in_node + '.' + out_attribute + ' is setting to value: ', in_value)
                            try:
                                cmds.setAttr(new_node + '.' + out_attribute, in_value)
                                print('\tValue set  successfully \n')
                            except Exception:
                                print('\tFailed to set value \n')
                                unconverted_attributes.append(new_node + '.' + out_attribute)
                                traceback.print_exc()

                #  input connections ###################################
                in_connection_inputs = self.fetch_attributes(file_data, in_node)[1].items()
                for in_attribute_input, in_connection_input in in_connection_inputs:
                    out_attribute_list = self.convert_attributes(file_data, node_type, in_attribute_input)
                    if out_attribute_list is not None:
                        out_attribute_input = out_attribute_list[0]
                        out_attribute_factor = out_attribute_list[2]
                        print(in_connection_input + ' is connecting to ' + in_node + '.' + out_attribute_input)
                        try:
                            if out_attribute_factor == 'Inverse':
                                inverse_node = cmds.shadingNode('reverse', asUtility=True)
                                cmds.connectAttr(in_connection_input, inverse_node + '.input', f=True)
                                cmds.connectAttr(inverse_node + '.output', new_node + '.' + out_attribute_input, f=True)
                                print('\tConnected inversely successfully \n')
                            else:
                                cmds.connectAttr(in_connection_input, new_node + '.' + out_attribute_input, f=True)
                                print('\tConnected successfully \n')
                        except Exception:
                            print('\tFailed to connect \n')
                            unconverted_attributes.append(new_node + '.' + out_attribute_input)
                            traceback.print_exc()

                #  output connections ###################################
                in_connection_outputs = self.fetch_attributes(file_data, in_node)[2].items()
                for in_attribute_output, in_connection_output in in_connection_outputs:
                    out_attribute_list = self.convert_attributes(file_data, node_type, in_attribute_output)
                    if out_attribute_list is not None:
                        out_attribute_output = out_attribute_list[0]
                        print(in_node + '.' + out_attribute_output + ' is connecting to ' + in_connection_output)
                        try:
                            cmds.connectAttr(new_node + '.' + out_attribute_output, in_connection_output, f=True)
                            print('\tConnected successfully \n')
                        except Exception:
                            print('\tFailed to connect \n')
                            unconverted_attributes.append(new_node + '.' + in_connection_output)
                            traceback.print_exc()

                if category == 'light':
                    in_transform = cmds.listRelatives(in_node, parent=True, shapes=True, fullPath=True)
                    cmds.matchTransform(new_node, in_transform)
                    in_parent = cmds.listRelatives(in_transform, parent=True, fullPath=True)
                    if in_parent:
                        cmds.parent(new_node, in_parent)
                    cmds.delete(in_transform)
                    in_name = in_transform[0].split('|')[-1]
                    cmds.rename(new_node, in_name)
                else:
                    cmds.delete(in_node)
                    cmds.rename(new_node, in_node)
            else:
                cmds.delete(new_node)
                print('Failed to create a new node of type: ' + out_node_type + '\n')

            return None, unconverted_attributes
        else:
            return (node_type + ' : ' + in_node), unconverted_attributes

    def get_shapes_from_objects(self, objects):
        objects_shapes = []
        if objects:
            for o in objects:
                shape = cmds.listRelatives(o, shapes=True, fullPath=True) or []
                objects_shapes.extend(shape)
        return objects_shapes

    def mat_and_tex_from_objects(self):
        selection = cmds.ls(sl=True)
        selection_shapes = self.get_shapes_from_objects(selection)
        selection_shapes = list(set(selection_shapes))
        shading_engine = cmds.listConnections(selection_shapes, type='shadingEngine')
        materials_connections = cmds.listConnections(shading_engine)
        materials = list(set(cmds.ls(materials_connections, materials=True)))
        textures = []
        for material in materials:
            textures_connections = cmds.listConnections(material)
            textures.extend(cmds.ls(textures_connections, textures=True))
        textures = list(set(textures))
        return materials, textures

    def list_materials(self, engine, selected=True, in_render=True):
        if in_render:
            material_types = self.get_type_nodes(engine, 'shader')
            engine_materials = cmds.ls(type=material_types)
            texture_types = self.get_type_nodes(engine, 'texture')
            engine_textures = cmds.ls(type=texture_types)

            if selected:
                selected_materials, selected_textures = self.mat_and_tex_from_objects()

                materials = []
                for material in selected_materials:
                    if material in engine_materials:
                        materials.append(material)

                textures = []
                for texture in selected_textures:
                    if texture in engine_textures:
                        textures.append(texture)
            else:
                materials = cmds.ls(engine_materials, mat=True)
                textures = cmds.ls(engine_textures, tex=True)
        else:
            if selected:
                materials, textures = self.mat_and_tex_from_objects()
            else:
                materials = cmds.ls(mat=True)
                textures = cmds.ls(tex=True)

        default_materials = cmds.ls(dn=True, mat=True)
        correct_materials = [i for i in materials if i not in default_materials]
        ignore_textures = cmds.ls(type=['file'])
        correct_textures = [i for i in textures if i not in ignore_textures]

        return correct_materials, correct_textures

    def list_lights(self, engine, selected=True, in_render=True):
        if in_render:
            light_types = self.get_type_nodes(engine, 'light')
        else:
            light_types = cmds.listNodeTypes('light')

        if light_types:
            if selected:
                selection = cmds.ls(sl=True)
                selection_shapes = self.get_shapes_from_objects(selection)
                light_shape_names = cmds.ls(selection_shapes, type=light_types)
            else:
                light_shape_names = cmds.ls(type=light_types)
        else:
            light_shape_names = []
        return light_shape_names

    def list_utilities(self, engine, selected=True, in_render=True):
        if in_render:
            type_list = self.get_type_nodes(engine, 'utility')  # only from specific render engine
        else:
            type_list = cmds.listNodeTypes('utility')  # all utilities

        if selected:
            selection = cmds.ls(sl=True)
            utilities = cmds.ls(selection, type=type_list)
        else:
            utilities = cmds.ls(type=type_list)

        exclude_software = self.get_type_nodes('mayaSoftware', 'utility')
        ignore_utilities = cmds.ls(type=exclude_software)
        correct_utilities = [i for i in utilities if i not in ignore_utilities]

        return correct_utilities

    def print_title(self, title):
        print('\n ################################################ \n')
        print('\t\t\t' + title)
        print('\n ################################################ \n')

    def convert_scene(self, file_name, lights=True, materials=True, selected=False, in_render=True):

        file_path = script_dir + '/Rules/' + file_name + '.json'
        data = self.load_json_file(file_path)

        source_engine = data['Engines'][0]

        engine_loaded = self.is_target_engine_loaded(data)
        if engine_loaded:

            unconverted_nodes = []
            unconverted_attributes = []

            if materials:
                scene_materials, scene_textures = self.list_materials(source_engine, selected=selected,
                                                                      in_render=in_render)
                self.print_title('Converting Materials:')
                for material in scene_materials:
                    print('\n\tMaterial:' + material)
                    print('****************************\n')
                    node, attributes = self.replace_node(data, material, 'material')
                    if node is not None:
                        unconverted_nodes.append(node)
                    unconverted_attributes.extend(attributes)

                self.print_title('Converting Textures:')
                for texture in scene_textures:
                    print('\n\tTexture:' + texture)
                    print('****************************\n')
                    node, attributes = self.replace_node(data, texture, 'texture')
                    if node is not None:
                        unconverted_nodes.append(node)
                    unconverted_attributes.extend(attributes)

            if lights:
                scene_lights = self.list_lights(source_engine, selected=selected, in_render=in_render)
                self.print_title('Converting Lights:')
                for light in scene_lights:
                    print('\n\tLight:' + light)
                    print('****************************\n')
                    node, attributes = self.replace_node(data, light, 'light')
                    if node is not None:
                        unconverted_nodes.append(node)
                    unconverted_attributes.extend(attributes)

            scene_utilities = self.list_utilities(source_engine, selected=selected, in_render=in_render)
            self.print_title('Converting Utilities:')
            for utility in scene_utilities:
                print('\n\tUtility:' + utility)
                print('****************************\n')
                node, attributes = self.replace_node(data, utility, 'utility')
                if node is not None:
                    unconverted_nodes.append(node)
                unconverted_attributes.extend(attributes)

            print('\n Nodes failed to be converted:' + str(len(unconverted_nodes)) + '\n')
            for node in unconverted_nodes:
                print('\n\t' + node)
            print('\n Attributes failed to be connected:' + str(len(unconverted_attributes)) + ' \n')
            for attribute in unconverted_attributes:
                print('\n\t' + attribute)

        else:
            cmds.inViewMessage(amg='In-view message <hl>Target render engine is not loaded</hl>.', pos='midCenter',
                               fade=True)

    def get_filenames(self, directory):
        file_list = []
        for root_paths, _, file_names in os.walk(directory):
            for f in file_names:
                if f.endswith('.json'):
                    file_name = f.strip('.json')
                    file_list.append(file_name)
        return file_list


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
