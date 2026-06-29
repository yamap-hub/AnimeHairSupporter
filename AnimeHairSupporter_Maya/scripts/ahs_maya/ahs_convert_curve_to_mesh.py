# -*- coding: utf-8 -*-
"""
カーブ > メッシュ 変換モジュール (Maya版・バグ完全修正・法線反転対策版)
"""
import maya.cmds as cmds

def execute(is_join=True, is_remove_doubles=True, is_uv_pack_islands=True, keep_original=True):
    target = cmds.ls(selection=True, long=True)
    if not target:
        cmds.warning("肉付けされたオブジェクトを選択してください。")
        return

    cmds.delete(target, constructionHistory=True)
    
    new_polys = []

    for obj in target:
        if cmds.nodeType(cmds.listRelatives(obj, shapes=True)[0]) == "nurbsSurface":
            # NURBSサーフェスをポリゴンに変換
            poly = cmds.nurbsToPoly(obj, format=3, polygonType=1, ch=False)
            poly_mesh = poly[0]
            
            # 【修正】ポリゴン化した際に法線が裏返って黒くなるのを防ぐため、ここで法線を反転して表に向けます
            cmds.polyNormal(poly_mesh, normalMode=0, ch=False)
            
            new_polys.append(poly_mesh)
            
            if keep_original:
                cmds.setAttr("{}.visibility".format(obj), False)
            else:
                cmds.delete(obj)
        else:
            new_polys.append(obj)

    if not new_polys:
        return

    final_mesh = new_polys[0]
    if is_join and len(new_polys) > 1:
        united = cmds.polyUnite(new_polys, ch=False, centerPivot=True)
        final_mesh = united[0]

    if is_remove_doubles:
        cmds.polyMergeVertex(final_mesh, distance=0.001, ch=False)
        cmds.polySoftEdge(final_mesh, angle=30, ch=False)

    if is_uv_pack_islands:
        cmds.polyMultiLayoutUV(final_mesh, scale=1, layoutMethod=1, percentageSpace=0.2,)

    cmds.select(final_mesh, replace=True)
    # 標準の print文に変更してエラーを回避
    print("AnimeHairSupporter: ポリゴン化およびクリーンアップが完了しました。")