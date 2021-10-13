import PyQt5
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from common.data.constants import QSS_STYLES_PATH, ICONS_PATH


class ThemeManager:
    ''' Change colors, icons and style of the interface '''

    def __init__(self, app_controller):
        self.app = app_controller.app
        self.view = app_controller.view
        self.theme = None
    
    def change_style(self, style):
        ''' Change general style of the interface '''

        if style == 'windows':
            if 'Windows' in QStyleFactory.keys():
                self.app.setStyle('Windows')
        elif style == 'fusion':
            if 'Fusion' in QStyleFactory.keys():
                self.app.setStyle('Fusion')

    def change_theme(self, theme):
        ''' Change colors and icons of the interface using Qss StyleSheets '''

        self.theme = theme
        if theme == 'green':
            path = QSS_STYLES_PATH + 'green.qss'
            icon_folder = 'green/'
        elif theme == 'blue':
            path = QSS_STYLES_PATH + 'blue.qss'
            icon_folder = 'blue/'
        elif theme == 'gray':
            path = QSS_STYLES_PATH + 'gray.qss'
            icon_folder = 'gray/'

        with open(path, 'r') as qss_file:
            self.app.setStyleSheet(qss_file.read())

        for button in self.view.findChildren(QPushButton):
            name = button.objectName()
            if 'up' in name:
                icon, size = 'arrow-up.png', QSize(10, 10)
            elif 'down' in name:
                icon, size = 'arrow-down.png', QSize(10, 10)
            elif 'attach' in name:
                icon, size = 'attach.png', QSize(12, 12)
            elif 'open' in name:
                icon, size = 'open.png', QSize(12, 12)
            elif 'recycle' in name:
                icon, size = 'recycle.png', QSize(12, 12)
            else: continue
            
            button.setIcon(QIcon(ICONS_PATH + icon_folder + icon))
            button.setIconSize(size)

    def apply_theme(self, dialog):
        ''' Apply active theme to dialog windows '''

        if self.theme == 'green':
            path = QSS_STYLES_PATH + 'green.qss'
        elif self.theme == 'blue':
            path = QSS_STYLES_PATH + 'blue.qss'
        elif self.theme == 'gray':
            path = QSS_STYLES_PATH + 'gray.qss'

        with open(path, 'r') as qss_file:
            dialog.setStyleSheet(qss_file.read())
