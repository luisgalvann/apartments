import PyQt5
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import Qt, QtGui, QtCore, QtWidgets, uic
from common.connections.alchemy_cn import main_engine, alch_session
from common.data.constants import FORM_VIEW_PATH
from common.managers.language_mgr import LangManager
import pandas as pd


class FormController:
    def __init__(self, model, table_name, app_controller):
        self.view = uic.loadUi(FORM_VIEW_PATH, QMainWindow())

        self.model = model
        self.table_name = table_name
        self.app_controller = app_controller
        self.lang_manager = LangManager()
        self.combobox = self.view.findChildren(QComboBox)[0]
        self.name_attr = [
            x for x in dir(model) if 'name' in x and (x != '__tablename__')][0]

        self.combobox.currentTextChanged.connect(self.write_editline)
        self.view.new_btn.clicked.connect(self.select_blank)
        self.view.save_btn.clicked.connect(self.save_record)
        self.view.delete_btn.clicked.connect(self.delete_record)
        self.view.closeEvent = self.closeEvent

    def write_editline(self):
        text = self.combobox.currentText()
        self.view.name_edit.setText(text)

    def select_blank(self):
        if self.combobox.findData('$#') == -1:
            self.combobox.addItem('', '$#')
        self.combobox.setCurrentIndex(self.combobox.findData('$#'))
        self.view.name_edit.setText('')

    def delete_record(self):
        instance_id = self.combobox.currentData()
        try:
            with alch_session() as session:
                condition = (self.model.id == instance_id)
                session.query(self.model).filter(condition).delete()
            self.view.name_edit.setText('')
            self.show_success_message()
        except Exception as exc:
            self.show_error_message()
            print(exc)
        finally:
            self.load_combo()

    def save_record(self):
        try:
            with alch_session() as session:
                if self.combobox.currentData() == '$#':
                    instance = self.model()
                else:
                    instance_id = self.combobox.currentData()
                    condition = (self.model.id == instance_id)
                    instance = session.query(self.model).filter(condition).first()
                setattr(instance, self.name_attr, self.view.name_edit.text())
                session.add(instance)
                self.show_success_message()
        except Exception as exc:
            self.show_error_message()
            print(exc)
        finally:
            self.load_combo()

    def show_success_message(self):
        msg = QMessageBox()
        msg.setWindowTitle(self.lang_manager.translate('success_title'))
        msg.setText(self.lang_manager.translate('success_message'))
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_error_message(self):
        msg = QMessageBox()
        msg.setWindowTitle(self.lang_manager.translate('error_title'))
        msg.setText(self.lang_manager.translate('error_message'))
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def load_combo(self):
        self.combobox.clear()
        records = pd.read_sql(self.table_name, main_engine)

        for record_data in records.itertuples():
            record_id = record_data[1]
            record_name = record_data[2]
            self.combobox.addItem(record_name, record_id)

    def translate_screen(self, lang):
        self.lang_manager.change_language(lang)
        for widget in self.view.findChildren((QLabel, QPushButton)):
            widget.setText(self.lang_manager.translate(widget.objectName()))

    def show_view(self):
        self.view.setWindowModality(QtCore.Qt.ApplicationModal)
        rectangle = self.view.frameGeometry()
        point = QDesktopWidget().availableGeometry(1).center()
        rectangle.moveCenter(point)
        self.view.move(rectangle.topLeft())
        self.view.show()

    def start(self):
        self.load_combo()
        self.translate_screen(self.app_controller.act_lang)
        self.show_view()

    def closeEvent(self, event):
        self.view.name_edit.setText('')
        self.app_controller.reset_screen()
