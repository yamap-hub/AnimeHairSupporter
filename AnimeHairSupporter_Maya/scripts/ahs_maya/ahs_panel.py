# -*- coding: utf-8 -*-
"""
Anime Hair Supporter for Maya - UI Panel Module (3点テーパー対応版)
"""
import maya.cmds as cmds
import maya.mel as mel

WINDOW_NAME = "AnimeHairSupporterWindow"
WINDOW_TITLE = "アニメ髪支援 (for MAYA ver0.1)"

class AnimeHairSupporterUI(object):
    def __init__(self):
        self.ui_elements = {}
        self.create_ui()

    def create_ui(self):
        if cmds.window(WINDOW_NAME, exists=True):
            cmds.deleteUI(WINDOW_NAME)
        
        # ウィンドウサイズを設定
        window = cmds.window(WINDOW_NAME, title=WINDOW_TITLE, widthHeight=(350, 590), sizeable=True)
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))

        # =====================================================================
        # メインセクション: 制作ステップ
        # =====================================================================
        cmds.frameLayout(label="制作ステップ (上から順番に操作します)", collapsable=False, parent=main_layout)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
        
        cmds.text(label="【Step 1】 髪の毛のガイドラインを用意する\nポリゴンエッジを選択 ＞ 作成したいカーブのボタンを選択", align="left", font="boldLabelFont")
        cmds.button(label="エッジ選択 ＞ EPカーブ生成", command=self.cmd_extract_edge)
        cmds.button(label="エッジ選択 ＞ ベジェカーブ生成", command=self.cmd_create_bezier)
        
        cmds.separator(height=10, style='in')
        
        cmds.text(label="【Step 2】 カーブに肉付けする (Hair Builder)\nカーブを選択 ＞ 断面形状を選択 ＞ 数値を変える", align="left", font="boldLabelFont")
        
        # 断面形状ラジオボタン
        self.ui_elements['shape_radio'] = cmds.radioButtonGrp(
    		label="断面形状", labelArray3=["円形", "平面", "ひし形"], numberOfRadioButtons=3, select=3,
    		changeCommand=lambda x: None 
	)

        cmds.button(label="カーブ ＞ 肉付け (プロファイル生成)", command=self.cmd_build_hair,visible=False  # 最初から非表示
        )

        # 各種スライダー
        self.ui_elements['width_slider'] = cmds.floatSliderGrp(
            label="幅", field=True, minValue=0.1, maxValue=10.0, value=1.0,
            dragCommand=self.cmd_build_hair, changeCommand=self.cmd_build_hair
        )
        self.ui_elements['height_slider'] = cmds.floatSliderGrp(
            label="厚み", field=True, minValue=0.1, maxValue=10.0, value=1.0,
            dragCommand=self.cmd_build_hair, changeCommand=self.cmd_build_hair
        )
        self.ui_elements['root_taper_slider'] = cmds.floatSliderGrp(
            label="根元の太さ", field=True, minValue=0.0, maxValue=2.0, value=0.0,
            dragCommand=self.cmd_build_hair, changeCommand=self.cmd_build_hair
        )
        # 【ここを追加】中間の太さをコントロールするスライダー
        self.ui_elements['middle_taper_slider'] = cmds.floatSliderGrp(
            label="中間の太さ", field=True, minValue=0.0, maxValue=10.0, value=1.0,
            dragCommand=self.cmd_build_hair, changeCommand=self.cmd_build_hair
        )
        self.ui_elements['tip_taper_slider'] = cmds.floatSliderGrp(
            label="毛先の細さ", field=True, minValue=0.0, maxValue=2.0, value=0.0,
            dragCommand=self.cmd_build_hair, changeCommand=self.cmd_build_hair
        )
        
        cmds.separator(height=10, style='in')
        
        cmds.text(label="【Step 3】 ポリゴン化\nサーフェスを選択 ＞ ポリゴン化　でポリゴンにする", 
        align="left",    font="boldLabelFont")
        cmds.button(label="ポリゴン化", command=self.cmd_convert_curve_to_mesh)
        
        cmds.separator(height=10, style='in')

        cmds.text(label="【Step 4】 ジョイント作成\nカーブを選択 ＞ ジョイント（骨）自動生成　でジョイントを作成する", 
        align="left", font="boldLabelFont")

        # 骨の分割数スライダー
        self.ui_elements['bone_subdivide_slider'] = cmds.intSliderGrp(
            label="骨の分割数", field=True, minValue=1, maxValue=10, value=4
        )
        
        # ジョイントのサイズスライダー
        self.ui_elements['joint_size_slider'] = cmds.floatSliderGrp(
            label="ジョイントのサイズ", field=True, minValue=0.01, maxValue=5.0, value=0.1, step=0.01
        )
        
        cmds.button(label="ジョイント（骨）自動生成", command=self.cmd_convert_curve_to_armature)

        cmds.showWindow(window)

    def cmd_create_bezier(self, *args):
        from ahs_maya import ahs_create_bezier
        import importlib
        importlib.reload(ahs_create_bezier)
        cmds.undoInfo(openChunk=True)
        try:
            ahs_create_bezier.execute()
        finally:
            cmds.undoInfo(closeChunk=True)

    def cmd_extract_edge(self, *args):
        from ahs_maya import ahs_edge_extractor
        import importlib
        importlib.reload(ahs_edge_extractor)
        cmds.undoInfo(openChunk=True)
        try:
            ahs_edge_extractor.execute()
        finally:
            cmds.undoInfo(closeChunk=True)

    def cmd_convert_edgemesh_to_curve(self, *args):
        from ahs_maya import ahs_convert_edgemesh_to_curve
        import importlib
        importlib.reload(ahs_convert_edgemesh_to_curve)
        cmds.undoInfo(openChunk=True)
        try:
            ahs_convert_edgemesh_to_curve.execute()
        finally:
            cmds.undoInfo(closeChunk=True)

    def cmd_build_hair(self, *args):
        from ahs_maya import ahs_hair_builder
        import importlib
        importlib.reload(ahs_hair_builder)
        cmds.undoInfo(openChunk=True)
        try:
            radio_index = cmds.radioButtonGrp(self.ui_elements['shape_radio'], query=True, select=True)
            shape_map = {1: "circle", 2: "flat", 3: "diamond"}
            
            width = cmds.floatSliderGrp(self.ui_elements['width_slider'], query=True, value=True)
            height = cmds.floatSliderGrp(self.ui_elements['height_slider'], query=True, value=True)
            root_val = cmds.floatSliderGrp(self.ui_elements['root_taper_slider'], query=True, value=True)
            middle_val = cmds.floatSliderGrp(self.ui_elements['middle_taper_slider'], query=True, value=True) # 追加
            tip_val = cmds.floatSliderGrp(self.ui_elements['tip_taper_slider'], query=True, value=True)
            
            ahs_hair_builder.execute(shape_type=shape_map.get(radio_index, "diamond"), 
                                     width=width, height=height, 
                                     root_taper=root_val, middle_taper=middle_val, tip_taper=tip_val) # 引数を追加
        finally:
            cmds.undoInfo(closeChunk=True)

    def cmd_convert_curve_to_mesh(self, *args):
        from ahs_maya import ahs_convert_curve_to_mesh
        import importlib
        importlib.reload(ahs_convert_curve_to_mesh)
        cmds.undoInfo(openChunk=True)
        try:
            ahs_convert_curve_to_mesh.execute(is_join=True, is_remove_doubles=True, is_uv_pack_islands=True, keep_original=True)
        finally:
            cmds.undoInfo(closeChunk=True)

    def cmd_convert_curve_to_armature(self, *args):
        from ahs_maya import ahs_convert_curve_to_armature
        import importlib
        importlib.reload(ahs_convert_curve_to_armature)
        cmds.undoInfo(openChunk=True)
        try:
            subdivide_count = cmds.intSliderGrp(self.ui_elements['bone_subdivide_slider'], query=True, value=True)
            joint_size_val = cmds.floatSliderGrp(self.ui_elements['joint_size_slider'], query=True, value=True)
            
            ahs_convert_curve_to_armature.execute(
                bone_subdivide_count=subdivide_count,
                joint_size=joint_size_val
            )
        finally:
            cmds.undoInfo(closeChunk=True)

def show():
    AnimeHairSupporterUI()