# -*- coding: utf-8 -*-
"""
カーブ > アーマチュア（ジョイント）変換モジュール (Maya版・端まで均等配置修正版)
"""
import maya.cmds as cmds

def execute(bone_subdivide_count=4, joint_size=1.0):
    """
    選択したNURBSカーブに沿って、始点から終点まで等間隔にジョイントチェーンを生成します。
    
    Args:
        bone_subdivide_count (int): 1つのカーブに対して作成するジョイントの数（分割数）
        joint_size (float): ジョイントの表示サイズ（半径）
    """
    selected_curves = cmds.ls(selection=True, long=True)
    if not selected_curves:
        cmds.warning("ジョイント化したいNURBSカーブを選択してください。")
        return

    created_roots = []

    for curve in selected_curves:
        shapes = cmds.listRelatives(curve, shapes=True, fullPath=True)
        if not shapes or cmds.nodeType(shapes[0]) != "nurbsCurve":
            cmds.warning("{} はNURBSカーブではないためスキップします。".format(curve))
            continue

        curve_shape = shapes[0]
        
        # 既存のベース名を取得
        base_name = curve.split("|")[-1].replace("_HairCurve", "")

        joints_in_chain = []
        num_joints = bone_subdivide_count + 1
        
        for i in range(num_joints):
            # 【修正ポイント】0.0（始点）から 1.0（終点）までの割合（パーセンテージ）を計算
            t = float(i) / float(num_joints - 1)
            
            # 【修正ポイント】top=True (Turn On Percentage) にすることで、
            # カーブの長さに対して正確に等間隔（0.0〜1.0）でワールド座標を取得します。
            pos = cmds.pointOnCurve(curve_shape, pr=t, top=True, position=True)
            
            jnt_name = "{}_Jnt_{:02d}".format(base_name, i + 1)
            
            # 前回の修正（サイズ変更）を維持
            new_jnt = cmds.joint(position=pos, name=jnt_name, radius=joint_size)
            joints_in_chain.append(new_jnt)

        if not joints_in_chain:
            continue

        # ジョイントの方向を綺麗に整える処理
        root_jnt = joints_in_chain[0]
        cmds.joint(root_jnt, edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True)
        created_roots.append(root_jnt)

    return created_roots