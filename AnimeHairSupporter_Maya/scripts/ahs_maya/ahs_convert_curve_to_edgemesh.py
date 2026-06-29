# -*- coding: utf-8 -*-
"""
カーブ > 辺メッシュ 変換モジュール (Maya版)
"""
import maya.cmds as cmds

def execute():
    """
    選択したNURBSカーブを、頂点とエッジのみで構成されたポリゴン（辺メッシュ）に変換します。
    """
    selected_curves = cmds.ls(selection=True, type='transform')
    if not selected_curves:
        cmds.warning("変換したいNURBSカーブを選択してください。")
        return

    created_meshes = []

    for curve in selected_curves:
        shapes = cmds.listRelatives(curve, shapes=True)
        if not shapes or cmds.nodeType(shapes[0]) != "nurbsCurve":
            cmds.warning("{} はNURBSカーブではないためスキップします。".format(curve))
            continue

        base_name = curve.replace("_HairCurve", "")
        out_name = "{}_EdgeMesh#".format(base_name)

        # 1. カーブから polyLine コマンドを使ってポリゴンラインを生成
        line_nodes = cmds.polyLine(curve, name=out_name, constructionHistory=False)
        
        if line_nodes:
            final_mesh = line_nodes[0]
            cmds.xform(final_mesh, centerPivots=True)
            created_meshes.append(final_mesh)
            
            # 2. 元のカーブを削除する（Blender版アドオンと同じ挙動）
            cmds.delete(curve)
            cmds.print("変換完了: {} -> {}\n".format(curve, final_mesh))

    if created_meshes:
        cmds.select(created_meshes, replace=True)