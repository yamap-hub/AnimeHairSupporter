# -*- coding: utf-8 -*-
"""
辺メッシュ > カーブ 変換モジュール (Maya版)
連続するエッジを綺麗に追跡し、NURBSカーブを生成します。
"""
import maya.cmds as cmds

def execute(degree=3, remove_mesh=True):
    """
    選択したポリゴン（辺メッシュ）の連続するエッジ（辺）を解析し、
    それぞれ独立した滑らかなNURBSカーブを作成します。
    """
    selected_meshes = cmds.ls(selection=True, objectsOnly=True, type='transform')
    if not selected_meshes:
        cmds.warning("辺メッシュオブジェクトを選択してください。")
        return

    created_curves = []

    for mesh in selected_meshes:
        # メッシュの形状ノードを確認
        shapes = cmds.listRelatives(mesh, shapes=True, fullPath=True)
        if not shapes or cmds.nodeType(shapes[0]) != "mesh":
            continue

        # --- エッジの接続関係から「一続きのライン」を解析する処理 ---
        # 頂点ごとの接続エッジ数を調べて、端点（接続数1）をリストアップ
        vtx_count = cmds.polyEvaluate(mesh, vertex=True)
        
        # 隣接関係を効率的に取得
        edge_connections = {}
        for i in range(vtx_count):
            vtx_str = "{}.vtx[{}]".format(mesh, i)
            # 接続している隣の頂点を取得
            connected_vtxs = cmds.polyListComponentConversion(vtx_str, toVertex=True)
            connected_vtx_list = cmds.ls(connected_vtxs, flatten=True)
            # 自分自身を除外した隣接リストを作成
            neighbors = [int(v.split('[')[-1].split(']')[0]) for v in connected_vtx_list if "{}.vtx".format(mesh) in v and int(v.split('[')[-1].split(']')[0]) != i]
            edge_connections[i] = neighbors

        # 既に訪問した頂点を追跡するセット
        visited = set()
        
        # 端点（接続されている隣の頂点が1つだけ）をスタート地点の候補にする
        start_vertices = [vtx for vtx, neighbors in edge_connections.items() if len(neighbors) == 1]
        
        # もし閉じた環状（輪っか）構造などで端点がない場合は、未訪問の適当な頂点から始める
        if not start_vertices:
            start_vertices = [vtx for vtx, neighbors in edge_connections.items() if len(neighbors) > 0]

        # 連続する頂点のラインを抽出
        for start_vtx in start_vertices:
            if start_vtx in visited:
                continue
                
            line_points = []
            current_vtx = start_vtx
            
            while current_vtx is not None and current_vtx not in visited:
                visited.add(current_vtx)
                # 座標を取得して追加
                pos = cmds.xform("{}.vtx[{}]".format(mesh, current_vtx), query=True, worldSpace=True, translation=True)
                line_points.append(pos)
                
                # 次の頂点を探す
                next_vtx = None
                for neighbor in edge_connections.get(current_vtx, []):
                    if neighbor not in visited:
                        next_vtx = neighbor
                        break
                current_vtx = next_vtx

            # 2つ以上の頂点があればカーブを生成
            if len(line_points) >= 2:
                # 頂点数が指定の次数(degree=3)より少ない場合は自動で次数を下げる(エラー防止)
                actual_degree = min(degree, len(line_points) - 1)
                
                # 安全な名前付け（型エラーの原因となる名前の直接指定時の「#」を排除）
                base_name = mesh.replace("_EdgeMesh", "")
                curve_name = cmds.curve(degree=actual_degree, point=line_points)
                # 生成後にリネームを行うことで安全に一意の名前を付与
                final_curve_name = cmds.rename(curve_name, "{}_HairCurve1".format(base_name))
                
                created_curves.append(final_curve_name)

        # 元の辺メッシュをクリーンアップ（標準仕様としてデフォルトTrue）
        if remove_mesh and created_curves:
            cmds.delete(mesh)

    if created_curves:
        cmds.select(created_curves, replace=True)
        cmds.print("辺メッシュからカーブへの変換が完了しました。\n")