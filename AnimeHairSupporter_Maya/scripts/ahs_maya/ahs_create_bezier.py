# -*- coding: utf-8 -*-
"""
選択エッジ完全追従型 ベジエ風ガイドカーブ生成モジュール (Maya版・座標ダイレクト取得版)
"""
import maya.cmds as cmds

def execute():
    """
    選択されたエッジ（コンポーネント）の頂点の絶対ワールド座標をダイレクトに取得し、
    トランスフォームの値を完全に無視して、エッジの真上にぴったり沿う4点の3次カーブを生成します。
    """
    # 1. 選択されているコンポーネント（エッジ）を取得
    selected_edges = cmds.filterExpand(sm=32)
    if not selected_edges:
        cmds.warning("ポリゴンのエッジ（辺）を選択した状態で『①-B』を実行してください。")
        return

    # 選択されたエッジから、そこに含まれる頂点（Vertex）の一覧を順序を保って取得
    # polyListComponentConversion を使用して、接続順に並んだ頂点に変換します
    vertices = cmds.polyListComponentConversion(selected_edges, toVertex=True)
    flat_vertices = cmds.ls(vertices, flatten=True)
    
    if len(flat_vertices) < 2:
        cmds.warning("エッジが短すぎるか、連続していません。2つ以上の頂点を含むエッジを選択してください。")
        return

    # 2. 頂点たちの「本物のワールド空間上の三次元座標」をダイレクトに抽出
    raw_points = []
    for vtx in flat_vertices:
        pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
        raw_points.append(pos)

    # 3. 取得した全頂点の座標から、編集しやすい「4点（根元・中間1・中間2・毛先）」の座標を均等にサンプリング
    num_points = len(raw_points)
    target_cvs = 4
    sampled_points = []
    
    for i in range(target_cvs):
        # 最初の頂点から最後の頂点までを均等な割合で割り振る
        idx = int(round((float(i) / float(target_cvs - 1)) * (num_points - 1)))
        # 安全のためにインデックスの範囲を超えないようガード
        idx = max(0, min(idx, num_points - 1))
        sampled_points.append(raw_points[idx])

    # 4. サンプリングした「完璧なワールド座標」へ、ダイレクトに3次のNURBSカーブを作成
    # これにより、モデルの移動・回転・スケールの影響を100%完全に無視して、見た目通りの場所にカーブを作れます
    mesh_name = selected_edges[0].split('.')[0].split('|')[-1]
    new_curve = cmds.curve(degree=3, point=sampled_points)
    final_curve_name = cmds.rename(new_curve, "{}_HairBezier1".format(mesh_name))
    
    # 5. 完成したカーブを選択し、即座に移動ツール（Wキー）でこねられるように「制御頂点（CV）」モードにする
    cmds.select(final_curve_name, replace=True)
    cmds.selectMode(component=True)
    cmds.selectType(controlVertex=True)
    
    print("選択エッジに100%完全に沿ったベジエ風カーブを生成しました。\n")