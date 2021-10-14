import unittest
from unittest import TestCase
from PyQt5.QtWidgets import QApplication, QMainWindow
from apps.apartments.controllers.apartments_ctr import ApartmentsController
from apps.apartments.models.apartments_mdl import *
import sys


app = QApplication(sys.argv)
ctr = ApartmentsController(app)


class ControllerTest(TestCase):
    ''' Check controller instantiation and methods '''

    def test_controller_instantiation(self):
        ''' Check if controller instantiation is correct '''

        self.assertIsInstance(ctr, ApartmentsController)


    def test_extended_widgets(self):
        ''' Check if extended widget classes are set '''

        self.assertIsInstance(ctr.top_table, xQTableWidget)
        self.assertIsInstance(ctr.sub_table, xQTableWidget)
        self.assertIsInstance(ctr.field_id, xQIdLineEdit)
        self.assertIsInstance(ctr.field_notes, xQNotesTextEdit)
        self.assertIsInstance(ctr.attachments_list, xQListWidget)


    def test_nav_buttons(self):
        ''' Check if there is only one nav button checked '''

        nav_buttons = ctr.get_widgets_group('nav_btn', QPushButton)
        checked_btns = [btn.isChecked() for btn in nav_buttons].count(True)

        self.assertEqual(checked_btns, 1)


    def test_create_form_widget(self):
        ''' Check if "create_form_widget" method returns QWidget instance '''

        widget = ctr.create_form_widget(0, QLineEdit)

        self.assertIsInstance(widget, QLineEdit)


    def test_rename_form_label(self):
        ''' Check if "rename_form_label" method translates labels properly '''

        widget = QLineEdit()
        widget.field = 'customer'
        widget = ctr.rename_form_label(0, widget)

        self.assertEqual(ctr.labels[0].text(), 'Cliente')
        ctr.translate_app('french')
        self.assertEqual(ctr.labels[0].text(), 'Client')



    def test_find_form_children(self):
        ''' Check if all form children are editable '''

        children = ctr.find_form_children()

        for x in children:
            self.assertIsInstance(x, (
                QLineEdit, QTextEdit, QComboBox, QSpinBox, 
                QDoubleSpinBox, QDateEdit, QTimeEdit))


    def test_format_html(self):
        previous_text = 'border="1"'
        expected_text = 'border="1" style="border-collapse:collapse"'
        formatted_text = ctr.format_html(previous_text)

        self.assertIn(expected_text, formatted_text)


if __name__ == '__main__':
    unittest.main()
