import os
import sys
import subprocess
from os.path import exists
from pandas import DataFrame
from PyQt5 import uic
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import QApplication
from apps.apartments.models.apartments_mdl import *
from common.connections.alchemy_cn import *
from common.managers.theme_mgr import ThemeManager
from common.managers.language_mgr import LangManager
from apps.apartments.controllers.form_ctr import FormController
from apps.apartments.controllers.city_form_ctr import CityFormController
from common.data.constants import APT_VIEW_PATH, EXPORTS_PATH


class ApartmentsController:
    def __init__(self, app):
        ''' Initialize state and build interface '''

        self.app = app
        self.view = uic.loadUi(APT_VIEW_PATH, QMainWindow())

        self.lang_mgr = LangManager()
        self.theme_mgr = ThemeManager(self)
        self.form_controller = FormController
        self.city_form_controller = CityFormController

        self.layouts = self.get_widgets_group('field_lay', QLayout)
        self.labels = self.get_widgets_group('field_lbl', QLabel)

        self.top_table = self.view.top_table
        self.sub_table = self.view.sub_table
        self.top_search = self.view.top_search_edit
        self.sub_search = self.view.sub_search_edit
        self.top_total = self.view.top_total_lbl
        self.sub_total = self.view.sub_total_lbl
        self.form = self.view.form
        self.attachments_list = self.view.files_lst
        self.field_id = self.view.id_edit
        self.field_notes = self.view.notes_edit

        self.top_model = None
        self.sub_model = None
        self.top_query = None
        self.sub_query = None
        self.top_data = None
        self.sub_data = None
        self.act_table = None
        self.act_model = None
        self.act_lang = None
        self.menubar = None

        self.modify_widgets_class()
        self.initialize_widgets()
        self.modify_nav_buttons()
        self.build_menubar()
        self.connect_signals()

        self.change_reservation()
        self.change_app_theme('blue')
        self.change_app_style('fusion')
        self.translate_app('spanish')

    def try_function(function):
        ''' Generic try-catch wrapper '''

        def wrapper(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
                return result
            except Exception as exc:
                self = args[0]
                self.show_error_message()
        return wrapper

    def modify_widgets_class(self):
        ''' Add extended classes to widgets '''

        self.top_table.__class__ = xQTableWidget
        self.sub_table.__class__ = xQTableWidget
        self.field_id.__class__ = xQIdLineEdit
        self.field_notes.__class__ = xQNotesTextEdit
        self.attachments_list.__class__ = xQListWidget

    def initialize_widgets(self):
        ''' Call widgets constructors '''

        self.top_table.__init__()
        self.sub_table.__init__()
        self.field_id.__init__()
        self.field_notes.__init__()
        function = self.add_docs_to_db_and_list
        self.attachments_list.__init__(function)

    def modify_nav_buttons(self):
        ''' Set Checkable buttons properties '''

        nav_buttons = self.get_widgets_group('nav_btn', QPushButton)
        for button in nav_buttons:
            button.setCheckable(True)
            if 'reservation' in button.objectName():
                button.setChecked(True)

    def build_menubar(self):
        ''' Build menubar and actions dynamically '''

        self.menubar = QMenuBar()
        self.view.setMenuBar(self.menubar)

        menu_titles = ('languages', 'themes', 'styles', 'help')
        submenu_groups = [
            [
                ('english', lambda: self.translate_app('english')),
                ('spanish', lambda: self.translate_app('spanish')),
                ('french', lambda: self.translate_app('french'))],
            [
                ('blue', lambda: self.change_app_theme('blue')),
                ('green', lambda: self.change_app_theme('green')),
                ('gray', lambda: self.change_app_theme('gray'))],
            [
                ('windows', lambda: self.change_app_style('windows')),
                ('fusion', lambda: self.change_app_style('fusion'))],
            [
                ('help', self.show_help_message),
                ('about', self.show_help_message)]
        ]

        for menu_title, submenu_group in zip(menu_titles, submenu_groups):
            menu = self.menubar.addMenu(menu_title)
            for title, function in submenu_group:
                action = menu.addAction(title)
                action.triggered.connect(function)

        for action in self.menubar.findChildren(QAction):
            action.setData(action.text())

    def connect_signals(self):
        ''' Connect interface elements and functions '''

        s, v = self, self.view
        clicked_groups = [
            (v.reservation_nav_btn, s.change_reservation),
            (v.service_nav_btn, s.change_service),
            (v.customer_nav_btn, s.change_customer),
            (v.employee_nav_btn, s.change_employee),
            (v.agency_nav_btn, s.change_agency),
            (v.owner_nav_btn, s.change_owner),
            (v.apartment_nav_btn, s.change_apartment),
            (v.clear_btn, s.reset_form_widgets),
            (v.cancel_btn, s.cancel_form_edition),
            (v.save_btn, s.save_instance),
            (v.attach_btn, s.open_add_docs_dialog),
            (v.open_btn, s.open_docs_with_program),
            (v.recycle_btn, s.delete_docs_from_db_and_list),
            (v.top_new_btn, s.set_new_top_form),
            (v.sub_new_btn, s.set_new_sub_form),
            (v.top_delete_btn, s.delete_top_row),
            (v.sub_delete_btn, s.delete_sub_row),
            (v.top_export_btn, s.export_top_data),
            (v.sub_export_btn, s.export_sub_data),
            (v.top_print_btn, s.print_top_data),
            (v.sub_print_btn, s.print_sub_data),
            (v.top_up_btn, lambda: s.navigate_top(step=-1)),
            (v.sub_up_btn, lambda: s.navigate_sub(step=-1)),
            (v.top_down_btn, lambda: s.navigate_top(step=1)),
            (v.sub_down_btn, lambda: s.navigate_sub(step=1)),
            (s.top_table, lambda: s.navigate_top()),
            (s.sub_table, lambda: s.navigate_sub())]

        for widget, function in clicked_groups:
            widget.clicked.connect(function)

        changed_groups = [
            (s.top_search, s.search_top_table),
            (s.sub_search, s.search_sub_table)]

        for widget, function in changed_groups:
            widget.textChanged.connect(function)

    def change_reservation(self):
        ''' Set Reservation screen variables '''

        self.top_model = Reservation
        self.sub_model = Service
        self.top_query = res_top_query()
        self.sub_query = res_sub_query()
        self.reset_screen()

    def change_service(self):
        ''' Set Service screen variables '''

        self.top_model = Service
        self.sub_model = Reservation
        self.top_query = srv_top_query()
        self.sub_query = srv_sub_query()
        self.reset_screen()

    def change_customer(self):
        ''' Set Customer screen variables '''

        self.top_model = Customer
        self.sub_model = Reservation
        self.top_query = cus_top_query()
        self.sub_query = cus_sub_query()
        self.reset_screen()

    def change_employee(self):
        ''' Set Employee screen variables '''

        self.top_model = Employee
        self.sub_model = Service
        self.top_query = emp_top_query()
        self.sub_query = emp_sub_query()
        self.reset_screen()

    def change_agency(self):
        ''' Set Agency screen variables '''

        self.top_model = Agency
        self.sub_model = Reservation
        self.top_query = agn_top_query()
        self.sub_query = agn_sub_query()
        self.reset_screen()

    def change_owner(self):
        ''' Set Owner screen variables '''

        self.top_model = Owner
        self.sub_model = Apartment
        self.top_query = own_top_query()
        self.sub_query = own_sub_query()
        self.reset_screen()

    def change_apartment(self):
        ''' Set reservation screen variables '''

        self.top_model = Apartment
        self.sub_model = Reservation
        self.top_query = apt_top_query()
        self.sub_query = apt_sub_query()
        self.reset_screen()

    def reset_screen(self):
        ''' Reset top data and call navigate '''

        self.top_search.setText(None)
        self.load_top_data()
        self.navigate_top()

    def navigate_top(self, step=0):
        ''' Set top table and model '''

        self.act_table = self.top_table
        self.act_model = self.top_model
        self.sub_search.setText(None)
        self.change_top_row(step)
        self.load_sub_data()
        self.build_and_load_form()

    def navigate_sub(self, step=0):
        ''' Set sub table and model '''

        self.act_table = self.sub_table
        self.act_model = self.sub_model
        self.change_sub_row(step)
        self.build_and_load_form()

    def build_and_load_form(self):
        ''' Call form building and load form data '''

        self.build_form()
        self.load_form_combos()
        self.load_form_data()

    def build_form(self):
        ''' Build form elements dinamically '''

        self.clear_form_layouts()
        index = 0
        for qtype in self.act_model.qtypes:
            if QToolButton in qtype.__bases__:
                widget = qtype(self)
                index -= 1  # Place button in previous layout
            else:
                widget = self.create_form_widget(index, qtype)
                self.rename_form_label(index, widget)

            self.layouts[index].addWidget(widget)
            index += 1
        self.reset_form_labels(self.labels, index)

    def clear_form_layouts(self):
        ''' Delete form widgets from layouts '''

        for layout in self.layouts:
            while (item:= layout.takeAt(0)):
                item.widget().deleteLater()

    def create_form_widget(self, index, qtype):
        ''' Return instance of QType with field attribute '''

        widget = qtype()
        widget.field = self.act_model.fields[index]
        return widget

    def rename_form_label(self, index, widget):
        ''' Change and translate form labels texts '''

        text = self.lang_mgr.translate(widget.field)
        self.labels[index].setText(text)

    def reset_form_labels(self, labels, index):
        ''' Show or hide form labels '''

        for label in labels[:index]:
            label.show()
        for label in labels[index:]:
            label.hide()

    @try_function
    def load_form_combos(self):
        ''' Load database combo info '''

        for combo in self.form.findChildren(xQComboBox):
            with alch_session() as session:
                instances = session.query(combo.get_model()).all()
            for instance in instances:
                combo.addItem(combo.get_text(instance), instance.id)

    def load_form_data(self):
        ''' Retrieve data for active table and id'''

        selected_items = self.act_table.selectedItems()
        if selected_items and (act_id := int(selected_items[0].text())):
            act_instance = self.get_db_instance(act_id)
            self.set_widgets_value(act_instance)
            self.reset_attachments_list()
        else:
            self.reset_form_widgets()
            self.field_id.setText(None)

    @try_function
    def get_db_instance(self, act_id):
        ''' Get active instance from database '''

        with alch_session() as session:
            model = self.act_model
            condition = (model.id == act_id)
            instance = session.query(model).filter(condition).first()
            return instance

    def set_widgets_value(self, instance):
        ''' Set display widgets info '''

        for widget in self.find_form_children():
            if hasattr(widget, 'field'):
                value = getattr(instance, widget.field)
                widget.set_data(value)

    def reset_attachments_list(self):
        ''' Clear attachments list and reset it '''

        self.attachments_list.clear()
        documents = self.get_act_instance_docs()
        if (paths:= [x.file_path for x in documents]):
            self.attachments_list.addItems(paths)

    def change_top_row(self, step):
        ''' Move top selection from the end to the beginning and viceversa '''

        if self.top_data:
            act_row = self.top_table.currentRow()
            if (i:= (act_row + step)) == (end:= len(self.top_data)):
                new_row = 0
            elif i < 0:
                new_row = end - 1
            else:
                new_row = i
            self.top_table.selectRow(new_row)

    def change_sub_row(self, step):
        ''' Move sub selection from the end to the beginning and viceversa '''

        if self.sub_data:
            act_row = self.sub_table.currentRow()
            if (i:= (act_row + step)) == (end:= len(self.sub_data)):
                new_row = 0
            elif i < 0:
                new_row = end - 1
            else:
                new_row = i
            self.sub_table.selectRow(new_row)

    @try_function
    def load_top_data(self):
        ''' Load top data and reset top widgets '''

        self.top_data = self.top_query.all()
        self.load_top_widgets()

    def load_top_widgets(self):
        ''' Load top table and top total '''

        self.load_table(self.top_table, self.top_data)
        self.top_total.setText(str(len(self.top_data)))

    @try_function
    def load_sub_data(self):
        ''' Load sub data and reset sub widgets '''

        top_id = int(self.top_table.selectedItems()[0].text())
        condition = (self.top_model.id == top_id)
        self.sub_data = self.sub_query.filter(condition).all()
        self.load_sub_widgets()

    def load_sub_widgets(self):
        ''' Load sub table and sub total '''

        self.load_table(self.sub_table, self.sub_data)
        self.sub_total.setText(str(len(self.sub_data)))

    def load_table(self, table, data):
        ''' Build top or sub table and format size '''

        if not len(data):
            table.setRowCount(0)
        else:
            table.setColumnCount(len(data[0]))
            table.setRowCount(len(data))
            columns = [x for x in data[0].keys()]
            columns = [self.lang_mgr.translate(x) for x in columns]
            table.setHorizontalHeaderLabels(columns)
            for r, row in enumerate(data):
                for c, column in enumerate(row):
                    table.setItem(r, c, QTableWidgetItem(str(column)))
                    table.setRowHeight(r, 10)
            table.resizeColumnsToContents()
            table.selectRow(0)

    def search_top_table(self):
        ''' Top search widget function '''

        if self.act_table != self.top_table:
            self.sub_search.setText(None)
            self.act_table = self.top_table
            self.act_model = self.top_model
            self.build_form()
            self.load_form_combos()
        self.load_top_data()
        text = self.top_search.text()
        items = self.top_table.findItems(text, Qt.MatchContains)
        id_list = [int(self.top_table.item(x.row(), 0).text()) for x in items]
        condition = self.top_model.id.in_(id_list)
        self.load_top_widgets_and_form(condition)
        self.reset_sub_widgets()

    @try_function
    def load_top_widgets_and_form(self, condition):
        ''' Get top data ready and reload top widgets and form '''

        self.top_data = self.top_query.filter(condition).all()
        self.load_top_widgets()
        self.load_form_data()

    def reset_sub_widgets(self):
        ''' Load sub table and sub total '''
        
        if self.top_data:
            self.load_sub_data()
        else:
            self.sub_table.setRowCount(0)
            self.sub_total.setText('0')

    def search_sub_table(self):
        ''' Sub search widget function '''

        if self.act_table != self.sub_table:
            self.act_table = self.sub_table
            self.act_model = self.sub_model
            self.build_form()
            self.load_form_combos()
        self.load_sub_data()
        text = self.sub_search.text()
        items = self.sub_table.findItems(text, Qt.MatchContains)
        id_list = [int(self.sub_table.item(x.row(), 0).text()) for x in items]
        condition = self.sub_model.id.in_(id_list)
        self.load_sub_widgets_and_form(condition)

    @try_function
    def load_sub_widgets_and_form(self, condition):
        ''' Get sub data ready and reload sub widgets and form '''

        self.sub_data = self.sub_query.filter(condition).all()
        self.load_sub_widgets()
        self.load_form_data()

    def cancel_form_edition(self):
        ''' Reload previous form data '''

        if self.act_table == self.top_table:
            self.navigate_top()
        elif self.act_table == self.sub_table:
            self.navigate_sub()

    def delete_top_row(self):
        ''' Delete top row and reload both tables '''

        if self.top_data:
            top_id = int(self.top_table.selectedItems()[0].text())
            if self.show_confirmation_message():
                self.delete_row_from_db(self.top_model, top_id)
                self.load_top_data()
                self.load_sub_data()

    def delete_sub_row(self):
        ''' Delete sub row and reload sub table '''

        if self.sub_data:
            sub_id = int(self.sub_table.selectedItems()[0].text())
            if self.show_confirmation_message():
                self.delete_row_from_db(self.sub_model, sub_id)
                self.load_sub_data()

    @try_function
    def delete_row_from_db(self, model, instance_id):
        ''' Delete record from database '''
        
        with alch_session() as session:
            condition = (model.id == instance_id)
            session.query(model).filter(condition).delete()

    def reset_form_widgets(self):
        ''' Clear widgets except for id field '''

        id_text = self.field_id.text()
        for widget in self.find_form_children():
            widget.clear_data()
        self.field_id.setText(id_text)

    def set_new_top_form(self):
        ''' Select top table and set form to new '''

        if self.act_table != self.top_table:
            self.navigate_top()
        self.set_new_form()

    def set_new_sub_form(self):
        ''' Select sub table and set form to new '''

        if self.act_table != self.sub_table:
            self.navigate_sub()
        self.set_new_form()

    def set_new_form(self):
        ''' Clear form widgets and show "new" in id field '''

        for widget in self.find_form_children():
            widget.clear_data()
        self.attachments_list.clear()
        self.field_id.setText('(new)')

    def save_instance(self):
        ''' Create new record or edit the old one '''

        if (edit_id:= self.field_id.text()) == '(new)':
            self.create_new_instance()
        else:
            self.edit_old_instance(edit_id)

    @try_function
    def create_new_instance(self):
        ''' Create new record in database '''

        with alch_session() as session:
            entity = Entity()
            session.add(entity)
            session.commit()
            instance = self.act_model()
            instance.entity_id = entity.id
            instance = self.fill_with_widgets_data(instance)
            session.add(instance)
        self.show_success_message()
        self.reset_screen()

    def edit_old_instance(self, edit_id):
        ''' Edit old record in database '''

        old_instance = self.get_db_instance(edit_id)
        self.fill_with_widgets_data(old_instance)
        self.show_success_message()
        self.reset_screen()

    def fill_with_widgets_data(self, instance):
        ''' Assign widget values to database instance '''

        for widget in self.find_form_children():
            if hasattr(widget, 'field'):
                attr_name = widget.field
                if attr_name != 'id':
                    value = widget.get_data()
                    setattr(instance, attr_name, value)
        return instance

    def find_form_children(self):
        ''' Return editable form widgets '''

        children = (xQLineEdit, xQTextEdit, xQComboBox, QAbstractSpinBox)
        widgets = self.form.findChildren(children)
        return widgets

    def add_docs_to_db_and_list(self, files_paths):
        ''' Update attached docs in database and attachments list '''

        act_id = int(self.act_table.selectedItems()[0].text())
        if files_paths and act_id:
            act_instance = self.get_db_instance(act_id)
            self.add_docs_to_db(act_instance, files_paths)
            self.attachments_list.addItems(files_paths)
            self.show_success_message()

    @try_function
    def add_docs_to_db(self, instance, paths):
        ''' Update attached docs in database '''

        with alch_session() as session:
            for path in paths:
                document = Document()
                document.foreign_entity_id = instance.entity_id
                document.file_path = path
                session.add(document)

    def delete_docs_from_db_and_list(self):
        ''' Delete attached docs in database and attachments list '''

        selected_documents = self.attachments_list.selectedItems()
        documents_paths = [x.text() for x in selected_documents]
        if documents_paths:
            success = []
            for document in self.get_act_instance_docs():
                if document.file_path in documents_paths:
                    done = self.delete_doc_from_db(document)
                    success.append(done)
            if success:  # Send only one success message for all documents
                self.show_success_message()
            self.reset_attachments_list()

    @try_function
    def delete_doc_from_db(self, document):
        ''' Delete the document from database '''

        with alch_session() as session:
            condition = (Document.id == document.id)
            session.query(Document).filter(condition).delete()
            return True

    def get_act_instance_docs(self):
        ''' Get active instance and its documents  '''

        act_id = int(self.act_table.selectedItems()[0].text())
        act_instance = self.get_db_instance(act_id)
        documents = self.get_instance_docs(act_instance)
        return documents

    @try_function
    def get_instance_docs(self, instance):
        ''' Get active instance from database '''

        with alch_session() as session:
            condition = (Document.foreign_entity_id == instance.entity_id)
            documents = session.query(Document).filter(condition).all()
            return documents

    def open_add_docs_dialog(self):
        ''' Open dialog to append documents paths '''

        dialog = QFileDialog()
        self.theme_mgr.apply_theme(dialog)
        dialog.setWindowTitle(self.lang_mgr.translate('attach_message'))
        dialog.setDirectory(EXPORTS_PATH)
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        if dialog.exec_():
            files_paths = dialog.selectedFiles()
            self.add_docs_to_db_and_list(files_paths)

    def open_docs_with_program(self):
        ''' Get paths from selected documents and open them '''

        selected_documents = self.attachments_list.selectedItems()
        documents_paths = [x.text() for x in selected_documents]

        if not all([exists(x) for x in documents_paths]):
            self.show_not_found_message()
        try:
            for file_path in documents_paths:
                command = self.get_command_for_os(file_path)
                subprocess.call(command)
        except Exception as exc:
            self.show_error_message()

    def get_command_for_os(self, file_path):
        ''' Get command for Operative System '''

        if str(os.name) == 'nt':
            command = ('cmd /c start "" "' + file_path + '"')
        else:
            if sys.platform.startswith('darwin'):
                command = ('open', file_path)
            else:
                command = ('xdg-open', file_path)
        return command

    def print_top_data(self):
        ''' Get top table data and call print dialog '''

        if (data := self.top_data):
            df = DataFrame(data=data, columns=data[0].keys())
            self.open_print_dialog(df)

    def print_sub_data(self):
        ''' Get sub table data and call print dialog '''

        if (data := self.sub_data):
            df = DataFrame(data=data, columns=data[0].keys())
            self.open_print_dialog(df)

    def open_print_dialog(self, df):
        ''' Print data from Dataframe '''

        dialog = QPrintPreviewDialog()
        self.theme_mgr.apply_theme(dialog)
        editor = QTextEdit(self.view)
        editor.setHtml(self.format_html(df.to_html()))
        printer = dialog.printer()
        printer.setOrientation(QPrinter.Landscape)
        printer.setPageSize(QPrinter.A4)
        printer.setDocName(EXPORTS_PATH + 'data.pdf')
        dialog.paintRequested.connect(editor.print_)
        if dialog.exec_() == QDialog.Accepted:
            self.open_printer(editor, printer)

    @try_function
    def open_printer(self, editor, printer):
        ''' Try to print the data selected '''

        editor.print_(printer)
        self.show_success_message()

    def export_top_data(self):
        ''' Get top table data and call export dialog '''

        if (data := self.top_data):
            df = DataFrame(data=data, columns=data[0].keys())
            self.open_export_dialog(df)

    def export_sub_data(self):
        ''' Get sub table data and call export dialog '''

        if (data := self.sub_data):
            df = DataFrame(data=data, columns=data[0].keys())
            self.open_export_dialog(df)

    def open_export_dialog(self, df):
        ''' Open export dialog and call format documents '''

        dialog = QFileDialog()
        self.theme_mgr.apply_theme(dialog)
        dialog.setWindowTitle(self.lang_mgr.translate('export_message'))
        dialog.setDirectory(EXPORTS_PATH)
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            self.export_to_formats(df, folder)

    @try_function
    def export_to_formats(self, df, folder):
        ''' Try to export the documents to 3 different formats '''

        html_text = self.format_html(df.to_html())
        with open(f'{folder}/data.html', 'w') as file:
            file.writelines(html_text)
        df.to_csv(f'{folder}/data.csv')
        df.to_json(f'{folder}/data.json')
        self.show_success_message()

    def format_html(self, text):
        ''' Change the default html format '''

        old_format = 'border="1"'
        new_format = 'border="1" style="border-collapse:collapse"'
        text = text.replace(old_format, new_format)
        return text

    def show_confirmation_message(self):
        ''' Get translated message for confirmation and show dialog '''

        msg = QMessageBox()
        self.theme_mgr.apply_theme(msg)
        msg.setWindowTitle(self.lang_mgr.translate('confirmation_title'))
        msg.setText(self.lang_mgr.translate('confirmation_message'))
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return True if (msg.exec_() == QMessageBox.Ok) else False

    def show_success_message(self):
        ''' Get translated message for success and show dialog '''

        msg = QMessageBox()
        self.theme_mgr.apply_theme(msg)
        msg.setWindowTitle(self.lang_mgr.translate('success_title'))
        msg.setText(self.lang_mgr.translate('success_message'))
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_error_message(self):
        ''' Get translated message for error and show dialog '''

        msg = QMessageBox()
        self.theme_mgr.apply_theme(msg)
        msg.setWindowTitle(self.lang_mgr.translate('error_title'))
        msg.setText(self.lang_mgr.translate('error_message'))
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_not_found_message(self):
        ''' Get translated message for not_found and show dialog '''

        msg = QMessageBox()
        self.theme_mgr.apply_theme(msg)
        msg.setWindowTitle(self.lang_mgr.translate('not_found_title'))
        msg.setText(self.lang_mgr.translate('not_found_message'))
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_help_message(self):
        ''' Get translated message for help and show dialog '''

        msg = QMessageBox()
        self.theme_mgr.apply_theme(msg)
        msg.setWindowTitle(self.lang_mgr.translate('help_title'))
        msg.setText(self.lang_mgr.translate('help_message'))
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()

    def get_widgets_group(self, text, qtype):
        ''' Return list of filtered and sorted widgets '''

        widgets = [x for x in self.view.findChildren(qtype)]
        condition = lambda x: text in x.objectName()
        criteria = lambda x: x.objectName()
        widgets = filter(condition, widgets)
        widgets = sorted(widgets, key=criteria)
        return widgets

    def change_app_theme(self, theme):
        ''' Change color of interface elements and icons '''

        self.theme_mgr.change_theme(theme)

    def change_app_style(self, style):
        ''' Change general style of interface elements '''

        self.theme_mgr.change_style(style)

    def translate_app(self, language):
        ''' Change active language and translate interface elements '''

        self.act_lang = language
        self.lang_mgr.change_language(language)
        for widget in self.view.findChildren((QPushButton, QLabel)):
            widget.setText(self.lang_mgr.translate(widget.objectName()))
        for action in self.menubar.findChildren(QAction):
            action.setText(self.lang_mgr.translate(action.data()))
        self.reset_screen()

    def start(self):
        ''' Show main window centered '''

        rectangle = self.view.frameGeometry()
        point = QDesktopWidget().availableGeometry(1).center()
        rectangle.moveCenter(point)
        self.view.move(rectangle.topLeft())
        self.view.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = ApartmentsController(app)
    controller.start()
    sys.exit(app.exec_())
