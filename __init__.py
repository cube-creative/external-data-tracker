import bpy
from .external_data_tracker import *


bl_info = {
    "name": "External data tracker",
    "description": "Show a list of external data in the file",
    "version": (0, 0, 1),
    "category": "Import-Export",
    "author": "Cube"
}


def register():
    bpy.utils.register_class(DisplayExternalDataListOperator)
    bpy.utils.register_class(ExternalDataList)
    bpy.utils.register_class(ExternalData)
    bpy.utils.register_class(ExternalDataUtilsAddonProperties)
    bpy.utils.register_class(ExternalDataTrackerPanel)
    bpy.types.WindowManager.external_data_utils_addon = bpy.props.PointerProperty(type=ExternalDataUtilsAddonProperties)


def unregister():
    bpy.utils.unregister_class(DisplayExternalDataListOperator)
    bpy.utils.unregister_class(ExternalDataList)
    bpy.utils.unregister_class(ExternalData)
    bpy.utils.unregister_class(ExternalDataUtilsAddonProperties)
    bpy.utils.unregister_class(ExternalDataTrackerPanel)
    del bpy.types.WindowManager.external_data_utils_addon
