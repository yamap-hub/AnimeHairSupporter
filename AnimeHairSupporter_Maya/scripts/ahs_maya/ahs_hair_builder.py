# -*- coding: utf-8 -*-
"""
髪の毛の断面形状生成＆肉付けモジュール (Maya版・表示と選択維持の完全修正版)
"""
import maya.cmds as cmds
import math

def _normalize(v):
    l = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/l, v[1]/l, v[2]/l) if l > 0 else (0, 1, 0)

def _cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def execute(shape_type="diamond", width=1.0, height=1.0, root_taper=1.0, middle_taper=1.0, tip_taper=0.0):
    selected_objs = cmds.ls(selection=True, long=True)
    valid_curves = []

    # 1. 選択中のオブジェクトの中からNURBSカーブのみを厳密に抽出
    if selected_objs:
        for obj in selected_objs:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
            if shapes and cmds.nodeType(shapes[0]) == "nurbsCurve":
                valid_curves.append(obj)

    if not valid_curves:
        cmds.warning("肉付けのガイドとなるNURBSカーブを選択した状態で実行してください。")
        return

    # 2. ビューポートのNURBSサーフェス表示がオフになっている場合の対策（強制オン）
    model_panels = cmds.getPanel(type="modelPanel")
    if model_panels:
        for panel in model_panels:
            cmds.modelEditor(panel, edit=True, nurbsSurfaces=True)

    for curve in valid_curves:
        # 3. リアルタイム更新用のクリーンアップ処理
        base_name = curve.split("|")[-1].replace("_HairCurve", "")
        surface_name = "{}_HairSurface".format(base_name)
        profile_grp = "{}_Profiles".format(base_name)
        
        if cmds.objExists(surface_name):
            cmds.delete(surface_name)
        if cmds.objExists(profile_grp):
            cmds.delete(profile_grp)

        curve_shapes = cmds.listRelatives(curve, shapes=True, fullPath=True)
        curve_shape = curve_shapes[0]
        
        # 4. 断面（プロファイル）のベース頂点座標を定義
        if shape_type == "circle":
            rad = 0.5
            base_points = [
                (width * rad, 0, 0),
                (width * rad * 0.707, height * rad * 0.707, 0),
                (0, height * rad, 0),
                (-width * rad * 0.707, height * rad * 0.707, 0),
                (-width * rad, 0, 0),
                (-width * rad * 0.707, -height * rad * 0.707, 0),
                (0, -height * rad, 0),
                (width * rad * 0.707, -height * rad * 0.707, 0),
                (width * rad, 0, 0)
            ]
        elif shape_type == "flat":
            base_points = [(width*0.5, 0, 0), (width*0.1, 0, 0), (-width*0.1, 0, 0), (-width*0.5, 0, 0)]
        else: # diamond
            base_points = [(width*0.5, 0, 0), (0, height*0.5, 0), (-width*0.5, 0, 0), (0, -height*0.5, 0), (width*0.5, 0, 0)]

        # 5. カーブに沿って断面を配置
        num_profiles = 15
        temp_profiles = []
        current_up = (0, 1, 0)
        
        for i in range(num_profiles):
            u = float(i) / float(num_profiles - 1)
            
            pos = cmds.pointOnCurve(curve_shape, pr=u, top=True, position=True)
            tangent = cmds.pointOnCurve(curve_shape, pr=u, top=True, normalizedTangent=True)
            
            if i == 0:
                current_up = (0, 1, 0)
                if abs(_dot(tangent, current_up)) > 0.99:
                    current_up = (1, 0, 0)
            else:
                current_up = _normalize(_cross(_cross(tangent, current_up), tangent))

            p0 = tip_taper
            p1 = middle_taper
            p2 = root_taper
            current_scale = ((1.0 - u) ** 2) * p0 + 2.0 * (1.0 - u) * u * p1 + (u ** 2) * p2
            
            if current_scale < 0.001: 
                current_scale = 0.001
                
            scaled_points = [(p[0] * current_scale, p[1] * current_scale, p[2] * current_scale) for p in base_points]
            profile = cmds.curve(degree=1, point=scaled_points)
            cmds.xform(profile, translation=pos, worldSpace=True)
            
            temp_locator = cmds.spaceLocator()[0]
            cmds.xform(temp_locator, translation=[pos[0]+tangent[0], pos[1]+tangent[1], pos[2]+tangent[2]], worldSpace=True)
            aim_const = cmds.aimConstraint(temp_locator, profile, aimVector=(0,0,1), upVector=(0,1,0), worldUpType="vector", worldUpVector=current_up)
            
            cmds.delete(aim_const)
            cmds.delete(temp_locator)
            temp_profiles.append(profile)

        # 6. ロフト生成とWireデフォーマの適用
        loft_nodes = cmds.loft(temp_profiles, ch=True, uniform=True, degree=3, sectionSpans=1, range=0, polygon=0)
        surface_node = cmds.rename(loft_nodes[0], surface_name)
        
        cmds.group(temp_profiles, name=profile_grp)
        cmds.setAttr(profile_grp + ".visibility", False)

        # 【修正】法線が裏返って真っ黒になるのを防ぐため、表面の向き（U/V）を入れ替えて強制反転します
        cmds.reverseSurface(surface_node, ch=True, rpo=True, d=3)
        
        # サーフェスに元のカーブを「Wireデフォーマ」として適用
        cmds.wire(surface_node, wire=curve, dropoffDistance=[0, 100.0])
        
        # 【修正】wireデフォーマ適用によって非表示化されるのを防ぐため、必ず適用の後ろ側で可視性をONにします
        cmds.setAttr(surface_node + ".visibility", True)

    # 7. 最後にガイドカーブを選択し直す（スライダーの連続操作を可能にするため）
    cmds.select(valid_curves, replace=True)