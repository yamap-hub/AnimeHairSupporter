# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.api.OpenMaya as om

def get_active_object():
    """現在選択されている最後（アクティブ）のオブジェクトを取得"""
    sel = cmds.ls(selection=True, long=True)
    return sel[-1] if sel else None

def select(obj_name, add=False):
    """オブジェクトを選択"""
    if cmds.objExists(obj_name):
        cmds.select(obj_name, add=add)

def set_hide(obj_name, hide=True):
    """オブジェクトの表示/非表示を切り替え"""
    if cmds.objExists(obj_name):
        cmds.setAttr("{}.visibility".format(obj_name), not hide)

def get_world_position(obj_name):
    """オブジェクトのワールド座標を取得"""
    return cmds.xform(obj_name, query=True, worldSpace=True, translation=True)