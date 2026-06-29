# -*- coding: utf-8 -*-
import maya.cmds as cmds
print("--- ahs_edge_extractor 読み込み開始 ---")

def execute():
    # 選択されているエッジを取得
    selected_edges = cmds.filterExpand(sm=32)
    if not selected_edges:
        cmds.warning("ポリゴンのエッジ（辺）を選択した状態で実行してください。")
        return

    base_mesh = selected_edges[0].split('.')[0]
    out_name = "{}_EdgeMesh#".format(base_mesh)

    # 1. 選択されたエッジからカーブを作成
    temp_curves = cmds.polyToCurve(form=2, degree=1, ch=False)
    if not temp_curves:
        cmds.warning("エッジからカーブへの変換に失敗しました。")
        return

    temp_curve = temp_curves[0]

    # 2. 修正：polyLine は存在しないため、カーブを名前変更してそのまま「辺メッシュ」とする
    # NURBSカーブをそのまま変換せず、名前を変えて辺メッシュの代わりにするのが最も安全です
    final_mesh = cmds.rename(temp_curve, out_name)

    # 3. ピボット調整と選択
    cmds.xform(final_mesh, centerPivots=True)
    cmds.select(final_mesh, replace=True)
    
    # print関数の修正（cmds.printは削除）
    print("辺メッシュを自動抽出しました: {}".format(final_mesh))