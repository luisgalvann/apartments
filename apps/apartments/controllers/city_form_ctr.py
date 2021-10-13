import PyQt5
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import Qt, QtGui, QtCore, QtWidgets, uic
from common.connections.alchemy_cn import main_engine, alch_session
from apps.apartments.models.apartments_mdl import *
from common.data.constants import CITY_FORM_VIEW_PATH
from common.managers.language_mgr import LangManager
import pandas as pd


class CityFormController:
    def __init__(self, app_controller):
        self.view = uic.loadUi(CITY_FORM_VIEW_PATH, QMainWindow())
        self.app_controller = app_controller
        self.lang_manager = LangManager()

        self.view.country_cbx.currentTextChanged.connect(self.load_city_combo)
        self.view.city_cbx.currentTextChanged.connect(self.write_editline)
        self.view.new_btn.clicked.connect(self.select_blank)
        self.view.save_btn.clicked.connect(self.save_record)
        self.view.delete_btn.clicked.connect(self.delete_record)
        self.view.closeEvent = self.closeEvent

    def write_editline(self):
        text = self.view.city_cbx.currentText()
        self.view.name_edit.setText(text)

    def select_blank(self):
        if self.view.city_cbx.findData('$#') == -1:
            self.view.city_cbx.addItem('', '$#')
        self.view.city_cbx.setCurrentIndex(self.view.city_cbx.findData('$#'))
        self.view.name_edit.setText('')

    def delete_record(self):
        city_id = self.view.city_cbx.currentData()
        try:
            with alch_session() as session:
                condition = (City.id == city_id)
                session.query(City).filter(condition).delete()
            self.view.name_edit.setText('')
            self.show_success_message()
        except Exception as exc:
            self.show_error_message()
            print(exc)
        finally:
            self.load_combos()

    def save_record(self):
        try:
            with alch_session() as session:
                if self.view.city_cbx.currentData() == '$#':
                    city = City()
                else:
                    city_id = self.view.city_cbx.currentData()
                    condition = (City.id == city_id)
                    city = session.query(City).filter(condition).first()
                city.city_name = self.view.name_edit.text()
                city.country_id = self.view.country_cbx.currentData()
                session.add(city)
                self.show_success_message()
        except Exception as exc:
            self.show_error_message()
            print(exc)
        finally:
            self.load_combos()

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

    def load_combos(self):
        self.load_country_combo()
        self.load_city_combo()

    def load_country_combo(self):
        self.view.country_cbx.clear()
        countries = pd.read_sql('country', main_engine)

        for country_data in countries.itertuples():
            country_id = country_data[1]
            country_name = country_data[2]
            self.view.country_cbx.addItem(country_name, country_id)

    def load_city_combo(self):
        self.view.city_cbx.clear()
        country_id = self.view.country_cbx.currentData()
        cities = pd.read_sql('city', main_engine)
        cities = cities[cities['country_id']==country_id]
        
        for city_data in cities.itertuples():
            city_id = city_data[1]
            city_name = city_data[2]
            self.view.city_cbx.addItem(city_name, city_id)

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
        self.load_combos()
        self.translate_screen(self.app_controller.act_lang)
        self.show_view()

    def closeEvent(self, event):
        self.view.name_edit.setText('')
        self.app_controller.reset_screen()
        