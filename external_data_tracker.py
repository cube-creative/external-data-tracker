import os.path
import bpy


class ExternalData(bpy.types.PropertyGroup):
    """Points toward an RNA element with a external data. Can be either image, text, or point cache."""
    IMAGE = "IMAGE"
    TEXT = "TEXT"
    CACHE = "CACHE"

    selected = bpy.props.BoolProperty(default=False)

    # TODO for the moment I can't find how to get a generic pointerProperty
    # maybe polymorphism?
    data_block_image = bpy.props.StringProperty()
    data_block_cache = bpy.props.StringProperty()
    data_block_text = bpy.props.StringProperty()
    data_block_type = bpy.props.StringProperty(default="IMAGE")

    def data_block(self):
        if self.data_block_type == self.IMAGE:
            return bpy.data.images[self.data_block_image]
        elif self.data_block_type == self.CACHE:
            return bpy.data.cache_files[self.data_block_cache]
        elif self.data_block_type == self.TEXT:
            return bpy.data.texts[self.data_block_text]

    def link(self, data_block):
        _type = type(data_block)
        if _type is bpy.types.Image:
            self.data_block_type = self.IMAGE
            self.data_block_image = data_block.name
        elif _type is bpy.types.CacheFile:
            self.data_block_type = self.CACHE
            self.data_block_cache = data_block.name
        elif _type is bpy.types.Text:
            self.data_block_type = self.TEXT
            self.data_block_text = data_block.name
        else:
            raise Exception("Wrong data-block type as external data-block: {}".format(_type))

    def get_name(self):
        return self.data_block().name

    def get_filepath(self):
        return self.data_block().filepath

    def set_directory_path(self, dir_path):
        self.data_block().filepath = os.path.join(dir_path, os.path.basename(self.data_block().filepath))

    def is_packed(self):
        if self.get_type() == "IMAGE":
            return self.data_block().packed_file is not None
        elif self.get_type() == "TEXT":
            return self.data_block().is_in_memory
        else:
            return False

    def exist_on_disk(self):
        return os.path.exists(self.get_filepath())

    def get_type(self):
        return self.data_block_type


class ExternalDataUtilsAddonProperties(bpy.types.PropertyGroup):
    """Global property group for all the addon variables"""
    external_data_list = bpy.props.CollectionProperty(type=ExternalData)
    external_data_list_active_index = bpy.props.IntProperty()


class ExternalDataList(bpy.types.UIList):
    """UI List in which is displayed external data"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            layout = layout.row(align=True)

            # selected
            layout.prop(item, "selected", text="")

            # type
            _type = item.get_type()
            if _type == ExternalData.IMAGE:
                _icon = "IMAGE_DATA"
            elif _type == ExternalData.TEXT:
                _icon = "TEXT"
            elif _type == ExternalData.CACHE:
                _icon = "MOD_MESHDEFORM"
            else:
                _icon = "EXTERNAL_DATA"
            layout.label(text="", icon=_icon)

            if _type == ExternalData.IMAGE:
                layout.label(text="", icon_value=layout.icon(item.data_block()))
            else:
                layout.label(text="", icon="BLANK1")

            # name
            layout = layout.split(percentage=0.25)
            layout.label(text=item.get_name())

            # path
            layout = layout.split(percentage=0.95)  # TODO risky magic value? yes I think so...
            layout.label(text=item.get_filepath())

            # packed/unpacked
            if item.is_packed():
                _icon = "PACKAGE"
            else:
                _icon = "UGLYPACKAGE"
            layout.label(text="", icon=_icon)

            # exists on disk
            if (not item.exist_on_disk()) and (not item.is_packed()):
                layout.label(text="", icon="ERROR")
            else:
                layout.label(text="", icon="BLANK1")


def update_external_data_list(context):
    """Update the addon data before displaying the list"""
    collection = context.window_manager.external_data_utils_addon.external_data_list
    collection.clear()

    for image in bpy.data.images:
        i = collection.add()
        i.link(image)
    for text in bpy.data.texts:
        t = collection.add()
        t.link(text)
    for cache in bpy.data.cache_files:
        c = collection.add()
        c.link(cache)


def toggle_selection_external_data_list(context, select):
    """Select or deselect all the element of the external data list"""
    collection = context.window_manager.external_data_utils_addon.external_data_list
    for e in collection:
        e.selected = select


def change_dir_path_external_data_list(context, path):
    """Change the directory of all selected item"""
    collection = context.window_manager.external_data_utils_addon.external_data_list
    for e in collection:
        if e.selected:
            e.set_directory_path(path)


class DisplayExternalDataListOperator(bpy.types.Operator):
    """Operator triggering the update and display of the list"""
    bl_idname = "cube.display_external_data_list_operator"
    bl_label = "External data tracker"
    bl_description = "Display the list of external data of this file"

    toggle_select_all = bpy.props.BoolProperty(name="Select all",
                                               description="Toggle select all",
                                               default=False)
    new_directory = bpy.props.StringProperty(name="New directory path")
    change_directory = bpy.props.BoolProperty(name="Change directory",
                                              description="Click to change directory of selected elements",
                                              default=False)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.toggle_select_all_prec = bool(self.toggle_select_all)
        update_external_data_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=1500)

    def draw(self, context):
        layout = self.layout

        # header
        row = layout.row()
        row = row.split(percentage=0.2)
        row.prop(self, "toggle_select_all")
        row = row.split(percentage=0.8)
        row.prop(self, "new_directory")
        row.prop(self, "change_directory")

        # list
        layout.template_list("ExternalDataList", "",
                             context.window_manager.external_data_utils_addon, "external_data_list",
                             context.window_manager.external_data_utils_addon, "external_data_list_active_index",
                             type="DEFAULT",
                             rows=35)

    def check(self, context):
        if self.toggle_select_all != self.toggle_select_all_prec:
            # update selection
            toggle_selection_external_data_list(context, self.toggle_select_all)
            self.toggle_select_all_prec = self.toggle_select_all
        if self.change_directory:
            self.change_directory = False
            change_dir_path_external_data_list(context, self.new_directory)
        return True


class ExternalDataTrackerPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "External data tracker"
    bl_category = "Cube"

    def draw(self, context):
        self.layout.operator("cube.display_external_data_list_operator")
