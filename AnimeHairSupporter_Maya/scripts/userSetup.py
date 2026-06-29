# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel

def create_anime_hair_menu():
    """Mayaのメインメニューバーにカスタムメニューを自動追加する"""
    # Mayaのメインウィンドウのメニューバーを取得
    gMainWindow = mel.eval('$tmp = $gMainWindow')
    
    menu_name = "ahsMenu"
    # すでにメニューが存在する場合は、二重生成を防ぐために一旦削除
    if cmds.menu(menu_name, exists=True):
        cmds.deleteUI(menu_name)
        
    # トップメニューを追加 (「ヘルプ」の左側あたりに追加されます)
    custom_menu = cmds.menu(menu_name, label="AnimeHair", parent=gMainWindow, tearOff=True)
    
    # メニューの中に「ツール起動」の項目を追加
    cmds.menuItem(
        label="Anime Hair Supporter を起動", 
        command=lambda *args: launch_ahs_tool()
    )

def launch_ahs_tool():
    """ツールを安全にインポートしてUIを表示する"""
    try:
        import ahs_maya
        ahs_maya.show_ui()
    except Exception as e:
        cmds.warning("Anime Hair Supporter の起動に失敗しました: {}".format(e))

# Mayaが完全に起動しきったタイミングでメニューを構築させる（鉄則の遅延実行）
cmds.evalDeferred(create_anime_hair_menu)