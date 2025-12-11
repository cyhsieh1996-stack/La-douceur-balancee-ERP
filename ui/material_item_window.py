# ui/material_item_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from logic.materials_logic import add_material, update_material


class MaterialItemWindow(QDialog):

    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)

        self.edit_data = edit_data
        self.setWindowTitle("編輯原料" if edit_data else "新增原料")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # ------------ 欄位 ------------

        self.code = QLineEdit()
        self.name_zh = QLineEdit()
        self.name_en = QLineEdit()
        self.brand = QLineEdit()
        self.vendor = QLineEdit()
        self.vendor_code = QLineEdit()
        self.spec = QLineEdit()

        self.unit = QComboBox()
        self.unit.addItems(["g", "ml", "顆", "包", "瓶"])

        self.note = QLineEdit()

        form = [
            ("原料編號", self.code),
            ("中文名稱", self.name_zh),
            ("英文名稱", self.name_en),
            ("廠牌", self.brand),
            ("供應商", self.vendor),
            ("供應商料號", self.vendor_code),
            ("規格描述", self.spec),
            ("單位", self.unit),
            ("備註", self.note),
        ]

        for label, widget in form:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            layout.addLayout(row)

        # ------------ 按鈕 ------------
        btn_row = QHBoxLayout()
        save_btn = QPushButton("儲存")
        cancel_btn = QPushButton("取消")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.close)

        if edit_data:
            self.load_data()

    # ------------------------
    def load_data(self):
        d = self.edit_data
        self.code.setText(d["code"] or "")
        self.name_zh.setText(d["name_zh"])
        self.name_en.setText(d["name_en"] or "")
        self.brand.setText(d["brand"] or "")
        self.vendor.setText(d["vendor"] or "")
        self.vendor_code.setText(d["vendor_code"] or "")
        self.spec.setText(d["spec"] or "")
        self.unit.setCurrentText(d["unit"] or "")
        self.note.setText(d["note"] or "")

    # ------------------------
    def save(self):
        data = {
            "code": self.code.text(),
            "name_zh": self.name_zh.text(),
            "name_en": self.name_en.text(),
            "brand": self.brand.text(),
            "vendor": self.vendor.text(),
            "vendor_code": self.vendor_code.text(),
            "spec": self.spec.text(),
            "unit": self.unit.currentText(),
            "note": self.note.text(),
        }

        if self.edit_data:
            update_material(self.edit_data["id"], data)
        else:
            add_material(data)

        self.accept()
