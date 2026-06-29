# -*- coding: utf-8 -*-
import sys
import importlib
import maya.cmds as cmds

# 現在作成済みのモジュールだけを読み込む設定
MODULE_NAMES = [
    "ahs_common",
    "ahs_panel",
    "ahs_convert_edgemesh_to_curve"
]

def show_ui():
    """ツールを初期化してUIを表示します"""
    try:
        # モジュールの読み込み・更新
        for name in MODULE_NAMES:
            fullname = "ahs_maya." + name
            if fullname in sys.modules:
                importlib.reload(sys.modules[fullname])
            else:
                importlib.import_module(fullname)
                
        # UIの起動
        from ahs_maya import ahs_panel
        ahs_panel.show()
        
    except Exception as e:
        cmds.error("UIの読み込みに失敗しました: {}".format(e))