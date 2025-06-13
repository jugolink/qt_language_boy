import sys
import os
import configparser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox, QMessageBox, QMenu
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPoint
from pathlib import Path
import subprocess

import resource.resource_rc 

CONFIG_DIR = Path.home() / ".ts_qm_tool"
CONFIG_FILE = CONFIG_DIR / "config.ini"

class TranslationToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt 多语言转换工具")
        self.setWindowIcon(QIcon(':/language_boy/logo'))
        self.resize(800, 650)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.config = configparser.ConfigParser()
        self.load_settings()

        self.layout = QVBoxLayout(self.central_widget)

        self.init_tool_paths_group()
        self.init_project_group()
        self.init_ts_output_group()
        self.init_action_buttons()
        self.connect_signals()

        self.ts_list_widget = QListWidget()
        self.ts_list_widget.itemDoubleClicked.connect(self.open_linguist_from_item)
        self.ts_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ts_list_widget.customContextMenuRequested.connect(self.show_ts_context_menu)
        self.layout.addWidget(QLabel("TS 文件列表（双击使用 Linguist 打开）："))
        self.layout.addWidget(self.ts_list_widget)

        self.restore_paths()
        self.update_generate_button_state()
        if self.project_path_edit.text():
            self.populate_file_list(self.project_path_edit.text())

    def init_tool_paths_group(self):
        group = QGroupBox("工具路径设置")
        layout = QVBoxLayout(group)

        self.lupdate_edit = self._add_path_selector(layout, "lupdate.exe 路径：")
        self.lrelease_edit = self._add_path_selector(layout, "lrelease.exe 路径：")
        self.linguist_edit = self._add_path_selector(layout, "linguist.exe 路径：")

        self.layout.addWidget(group)

    def init_project_group(self):
        group = QGroupBox("项目设置")
        layout = QVBoxLayout(group)

        hbox = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        browse_btn = QPushButton("选择项目目录")
        browse_btn.clicked.connect(self.choose_project_directory)
        hbox.addWidget(QLabel("项目根目录："))
        hbox.addWidget(self.project_path_edit)
        hbox.addWidget(browse_btn)

        layout.addLayout(hbox)

        self.file_list_widget = QListWidget()
        layout.addWidget(QLabel("包含的 .py / .ui 文件（可取消勾选）："))
        layout.addWidget(self.file_list_widget)

        self.layout.addWidget(group)

    def init_ts_output_group(self):
        group = QGroupBox("TS 文件输出设置")
        layout = QVBoxLayout(group)

        self.ts_output_edit = self._add_path_selector(layout, "ts 输出目录：", directory=True)

        name_layout = QHBoxLayout()
        self.ts_file_name_edit = QLineEdit()
        name_layout.addWidget(QLabel("TS 文件名（可选）："))
        name_layout.addWidget(self.ts_file_name_edit)
        layout.addLayout(name_layout)

        layout.addWidget(QLabel("选择目标语言："))
        self.lang_checkboxes = []
        languages = ["zh_CN", "zh_TW", "en_US", "ja_JP", "de_DE", "fr_FR"]
        lang_layout = QHBoxLayout()
        for lang in languages:
            cb = QCheckBox(lang)
            cb.setChecked(True)
            lang_layout.addWidget(cb)
            self.lang_checkboxes.append(cb)
        layout.addLayout(lang_layout)

        self.layout.addWidget(group)

    def init_action_buttons(self):
        hbox = QHBoxLayout()
        self.gen_ts_btn = QPushButton("生成 TS 文件")
        hbox.addWidget(self.gen_ts_btn)
        self.layout.addLayout(hbox)

    def connect_signals(self):
        self.gen_ts_btn.clicked.connect(self.generate_ts_files)
        for edit in [self.lupdate_edit, self.lrelease_edit, self.linguist_edit,
                     self.project_path_edit, self.ts_output_edit]:
            edit.editingFinished.connect(self.on_paths_changed)

    def on_paths_changed(self):
        self.save_settings()
        self.update_generate_button_state()

    def update_generate_button_state(self):
        valid = all(Path(p.text()).exists() for p in [self.lupdate_edit, self.lrelease_edit, self.linguist_edit])
        self.gen_ts_btn.setEnabled(valid)

    def _add_path_selector(self, layout, label_text, directory=False):
        hbox = QHBoxLayout()
        edit = QLineEdit()
        btn = QPushButton("浏览")

        def browse():
            if directory:
                path = QFileDialog.getExistingDirectory(self, label_text)
            else:
                path, _ = QFileDialog.getOpenFileName(self, label_text)
            if path:
                edit.setText(path)
                self.on_paths_changed()

        btn.clicked.connect(browse)
        hbox.addWidget(QLabel(label_text))
        hbox.addWidget(edit)
        hbox.addWidget(btn)
        layout.addLayout(hbox)
        return edit

    def choose_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择项目根目录")
        if directory:
            self.project_path_edit.setText(directory)
            self.populate_file_list(directory)
            self.save_settings()

    def populate_file_list(self, root):
        self.file_list_widget.clear()
        for ext in ('*.py', '*.ui'):
            for path in Path(root).rglob(ext):
                item = QListWidgetItem(str(path))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                self.file_list_widget.addItem(item)

    def get_checked_files(self):
        return [self.file_list_widget.item(i).text()
                for i in range(self.file_list_widget.count())
                if self.file_list_widget.item(i).checkState() == Qt.CheckState.Checked]

    def generate_ts_files(self):
        self.ts_list_widget.clear()
        project_path = self.project_path_edit.text()
        lupdate_path = self.lupdate_edit.text()
        ts_output_dir = self.ts_output_edit.text()
        ts_name = self.ts_file_name_edit.text().strip() or Path(project_path).name

        files = self.get_checked_files()
        if not all([project_path, lupdate_path, ts_output_dir, files]):
            QMessageBox.warning(self, "警告", "请填写必要路径并选择文件")
            return

        for cb in self.lang_checkboxes:
            if cb.isChecked():
                ts_file = Path(ts_output_dir) / f"{ts_name}_{cb.text()}.ts"
                cmd = [
                    lupdate_path,
                    *files,
                    "-ts", str(ts_file)
                ]
                try:
                    subprocess.run(cmd, check=True)
                    self.ts_list_widget.addItem(str(ts_file))
                except subprocess.CalledProcessError:
                    QMessageBox.critical(self, "错误", f"生成 TS 文件失败: {ts_file}")

        QMessageBox.information(self, "完成", "TS 文件生成完成")

    def open_linguist_from_item(self, item):
        linguist_path = self.linguist_edit.text()
        if linguist_path and Path(item.text()).exists():
            subprocess.Popen([linguist_path, item.text()])

    def show_ts_context_menu(self, pos: QPoint):
        item = self.ts_list_widget.itemAt(pos)
        if not item:
            return

        menu = QMenu()
        action_release = menu.addAction("发布为 QM 文件")
        action = menu.exec(self.ts_list_widget.mapToGlobal(pos))
        if action == action_release:
            self.generate_qm_for_file(Path(item.text()))

    def generate_qm_for_file(self, ts_path: Path):
        lrelease_path = self.lrelease_edit.text()
        if not lrelease_path or not Path(lrelease_path).exists():
            QMessageBox.warning(self, "警告", "lrelease 路径无效")
            return

        qm_file = ts_path.with_suffix(".qm")
        cmd = [lrelease_path, str(ts_path), "-qm", str(qm_file)]
        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "完成", f"QM 文件已发布：{qm_file}")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "错误", f"生成 QM 文件失败: {qm_file}")

    def load_settings(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        if CONFIG_FILE.exists():
            self.config.read(CONFIG_FILE, encoding='utf-8')
        else:
            self.config['Paths'] = {}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                self.config.write(f)

    def save_settings(self):
        self.config['Paths'] = {
            'lupdate': self.lupdate_edit.text(),
            'lrelease': self.lrelease_edit.text(),
            'linguist': self.linguist_edit.text(),
            'project': self.project_path_edit.text(),
            'ts_output': self.ts_output_edit.text(),
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            self.config.write(f)
        return True

    def restore_paths(self):
        try:
            paths = self.config['Paths']
            self.lupdate_edit.setText(paths.get('lupdate', ''))
            self.lrelease_edit.setText(paths.get('lrelease', ''))
            self.linguist_edit.setText(paths.get('linguist', ''))
            self.project_path_edit.setText(paths.get('project', ''))
            self.ts_output_edit.setText(paths.get('ts_output', ''))
            self.update_generate_button_state()
        except KeyError:
            pass  # 或者记录错误日志

def main():
    app = QApplication(sys.argv)
    window = TranslationToolGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()