from abc import ABC, ABCMeta, abstractmethod
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, SmallInteger, String, Text
from sqlalchemy import Date, Time, Float, ForeignKey
from datetime import date, time
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QAbstractItemView as qa
from common.data.constants import DB_NAME


# ============ EXTENDED WIDGETS ============
# Add polimorphism to widgets classes

class xQLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.clear()

    def set_data(self, value):
        self.setText(str(value))

    def get_data(self):
        return self.text()


class xQComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.setCurrentIndex(self.findData('$#'))

    def set_data(self, value):
        self.setCurrentIndex(self.findData(value))

    def get_data(self):
        return self.itemData(self.currentIndex())


class xQDateEdit(QDateEdit):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.setDate(QDate(2000, 1, 1))

    def set_data(self, value):
        if value:
            self.setDate(value)
        else:
            self.setDate(QDate(2000, 1, 1))

    def get_data(self):
        dt = self.date()
        return date(dt.year(), dt.month(), dt.day())


class xQTimeEdit(QTimeEdit):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.setTime(QTime(0, 0))

    def set_data(self, value):
        self.setTime(value)

    def get_data(self):
        tm = self.time()
        return time(tm.hour(), tm.minute())


class xQSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.clear()

    def set_data(self, value):
        self.setValue(value)

    def get_data(self):
        return self.value()


class xQDoubleSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.field = None
        self.setMaximum(1000000)

    def clear_data(self):
        self.clear()

    def set_data(self, value):
        self.setValue(value)

    def get_data(self):
        return self.value()


class xQTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.field = None

    def clear_data(self):
        self.clear()

    def set_data(self, value):
        self.setText(str(value))

    def get_data(self):
        return self.toPlainText()


class xQCountryComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Country

    def get_text(self, instance):
        return instance.country_name


class xQCityComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return City

    def get_text(self, instance):
        return instance.city_name


class xQReservationComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Reservation

    def get_text(self, instance):
        return str(instance.id)


class xQCustomerComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Customer

    def get_text(self, instance):
        return f'{instance.first_name} {instance.last_name}'


class xQEmployeeComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Employee

    def get_text(self, instance):
        return f'{instance.first_name} {instance.last_name}'


class xQAgencyComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Agency

    def get_text(self, instance):
        return instance.agency_name


class xQOwnerComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Owner

    def get_text(self, instance):
        return f'{instance.first_name} {instance.last_name}'


class xQApartmentComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return Apartment

    def get_text(self, instance):
        return instance.apartment_name


class xQServiceTypeComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return ServiceType

    def get_text(self, instance):
        return instance.s_type_name


class xQServiceCategoryComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return ServiceCategory

    def get_text(self, instance):
        return instance.s_category_name


class xQEmployeeCategoryComboBox(xQComboBox):
    def __init__(self):
        super().__init__()

    def get_model(self):
        return EmployeeCategory

    def get_text(self, instance):
        return instance.e_category_name


class xQListWidget(QListWidget):
    ''' QListWidget enhanced with drag and drop functions '''

    def __init__(self, function):
        self.add_docs_to_db_and_list = function
        self.setSelectionMode(qa.MultiSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    paths.append(str(url.toLocalFile()))
            self.add_docs_to_db_and_list(paths)
        else:
            event.ignore()


class xQTableWidget(QTableWidget):
    def __init__(self):
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(qa.NoEditTriggers)
        self.setSelectionMode(qa.SingleSelection)
        self.setSelectionBehavior(qa.SelectRows)
        self.setSortingEnabled(True)


class xQIdLineEdit(xQLineEdit):
    def __init__(self):
        self.field = 'id'
        self.setEnabled(False)


class xQNotesTextEdit(xQTextEdit):
    def __init__(self):
        self.field = 'notes'


class xQCityToolButton(QToolButton):
    def __init__(self, main_contr):
        super().__init__()
        form = main_contr.city_form_controller
        controller = form(main_contr)
        self.clicked.connect(lambda: controller.start())


class xQCountryToolButton(QToolButton):
    def __init__(self, main_contr):
        super().__init__()
        form = main_contr.form_controller
        controller = form(Country, 'country', main_contr)
        self.clicked.connect(lambda: controller.start())


class xQEmployeeCategoryToolButton(QToolButton):
    def __init__(self, main_contr):
        super().__init__()
        form = main_contr.form_controller
        controller = form(EmployeeCategory, 'employee_category', main_contr)
        self.clicked.connect(lambda: controller.start())


class xQServiceCategoryToolButton(QToolButton):
    def __init__(self, main_contr):
        super().__init__()
        form = main_contr.form_controller
        controller = form(ServiceCategory, 'service_category', main_contr)
        self.clicked.connect(lambda: controller.start())


class xQServiceTypeToolButton(QToolButton):
    def __init__(self, main_contr):
        super().__init__()
        form = main_contr.form_controller
        controller = form(ServiceType, 'service_type', main_contr)
        self.clicked.connect(lambda: controller.start())


# ============ ABSTRACT CLASES ============
# Implementation of abstract classes and methods

class Contact(ABC):
    phone = Column(String(50))
    email = Column(String(50))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError(
            'users must define __str__ to use this base class')


class Address(ABC):
    address = Column(String(50))
    zip_code = Column(String(50))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError(
            'users must define __str__ to use this base class')


class Person(Contact, Address):
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError(
            'users must define __str__ to use this base class')


# ============ HIBRID (CONCRETE/ABSTRACT) METACLASS ============
# the metaclass of a derived class must be a subclass of the metaclasses of all its bases
# The metaclass of a class is its 'type'. The metaclass of ABC is 'ABCMeta'

Base = declarative_base()


class HibridMeta(type(Base), ABCMeta):
    pass


# ============ DATABASE CLASSES ============
# Classes that represent tables in the database

class Entity(Base):
    __tablename__ = 'entity'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)

    document = relationship(
        'Document', backref=backref('entity', uselist=False))
    customer = relationship(
        'Customer', backref=backref('entity', uselist=False))
    owner = relationship('Owner', backref=backref('entity', uselist=False))
    agency = relationship('Agency', backref=backref('entity', uselist=False))
    apartment = relationship(
        'Apartment', backref=backref('entity', uselist=False))
    employee = relationship(
        'Employee', backref=backref('entity', uselist=False))
    reservation = relationship(
        'Reservation', backref=backref('entity', uselist=False))

    def __str__(self):
        return f'Entity ID: {self.id}'


class Document(Base):
    __tablename__ = 'document'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    foreign_entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False)
    file_path = Column(Text, nullable=False)

    def __str__(self):
        return f'Document: {self.id}, {self.file_path}'


class Country(Base):
    __tablename__ = 'country'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    country_name = Column(String(50), nullable=False)

    city = relationship('City', backref='country')
    customer = relationship('Customer', backref='country')
    owner = relationship('Owner', backref='country')
    agency = relationship('Agency', backref='country')
    apartment = relationship('Apartment', backref='country')
    employee = relationship('Employee', backref='country')

    def __str__(self):
        return f'Country: {self.id}, {self.country_name}'


class City(Base):
    __tablename__ = 'city'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    city_name = Column(String(50), nullable=False)
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)

    customer = relationship('Customer', backref='city')
    owner = relationship('Owner', backref='city')
    agency = relationship('Agency', backref='city')
    apartment = relationship('Apartment', backref='city')
    employee = relationship('Employee', backref='city')

    def __str__(self):
        return f'City: {self.id}, {self.city_name}'


class Customer(Base, Person, metaclass=HibridMeta):
    __tablename__ = 'customer'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    language = Column(String(50))
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)
    city_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.city.id', ondelete='CASCADE'),
        nullable=False)
    notes = Column(Text())

    reservation = relationship('Reservation', backref='customer')

    fields = [
        'first_name', 'last_name', 'phone', 'email', 'language',
        'country_id', 'city_id', 'address', 'zip_code']
    qtypes = [
        xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit,
        xQCountryComboBox, xQCountryToolButton, xQCityComboBox,
        xQCityToolButton, xQLineEdit, xQLineEdit]

    def __str__(self):
        return f'Customer: {self.id}, {self.first_name} {self.last_name}'


class Owner(Base, Person, metaclass=HibridMeta):
    __tablename__ = 'owner'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    language = Column(String(50))
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)
    city_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.city.id', ondelete='CASCADE'),
        nullable=False)
    notes = Column(Text())

    apartment = relationship('Apartment', backref='owner')

    fields = [
        'first_name', 'last_name', 'phone', 'email', 'language',
        'country_id', 'city_id', 'address', 'zip_code']
    qtypes = [
        xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit,
        xQCountryComboBox, xQCountryToolButton, xQCityComboBox,
        xQCityToolButton, xQLineEdit, xQLineEdit]

    def __str__(self):
        return f'Owner: {self.id}, {self.first_name} {self.last_name}'


class Agency(Base, Contact, Address, metaclass=HibridMeta):
    __tablename__ = 'agency'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    agency_name = Column(String(50), nullable=False)
    contact_person = Column(String(50))
    cp_phone = Column(String(50))
    website = Column(String(50))
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)
    city_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.city.id', ondelete='CASCADE'),
        nullable=False)
    notes = Column(Text())

    reservation = relationship('Reservation', backref='agency')

    fields = [
        'agency_name', 'phone', 'contact_person', 'cp_phone', 'email',
        'website', 'country_id', 'city_id', 'address', 'zip_code']
    qtypes = [
        xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit,
        xQLineEdit, xQCountryComboBox, xQCountryToolButton,
        xQCityComboBox, xQCityToolButton, xQLineEdit, xQLineEdit]

    def __str__(self):
        return f'Agency: {self.id}, {self.agency_name}'


class Apartment(Base, Address, metaclass=HibridMeta):
    __tablename__ = 'apartment'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    apartment_name = Column(String(50), nullable=False)
    phone = Column(String(50))
    owner_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.owner.id', ondelete='CASCADE'),
        nullable=False)
    max_guests = Column(SmallInteger)
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)
    city_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.city.id', ondelete='CASCADE'),
        nullable=False)
    parking_spaces = Column(SmallInteger)
    notes = Column(Text())

    reservation = relationship('Reservation', backref='apartment')

    fields = [
        'apartment_name', 'phone', 'owner_id', 'max_guests', 'country_id',
        'city_id', 'address', 'zip_code', 'parking_spaces']
    qtypes = [
        xQLineEdit, xQLineEdit, xQOwnerComboBox, xQSpinBox,
        xQCountryComboBox, xQCountryToolButton, xQCityComboBox,
        xQCityToolButton, xQLineEdit, xQLineEdit, xQSpinBox]

    def __str__(self):
        return f'Apartment: {self.id}, {self.apartment_name}'


class EmployeeCategory(Base):
    __tablename__ = 'employee_category'
    __table_args__ = {'schema': DB_NAME}

    id = Column(SmallInteger, primary_key=True)
    e_category_name = Column(String(50), nullable=False)

    employee = relationship('Employee', backref='employee_category')

    def __str__(self):
        return f'Employee Category: {self.id}, {self.e_category_name}'


class Employee(Base, Person, metaclass=HibridMeta):
    __tablename__ = 'employee'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    e_category_id = Column(
        SmallInteger,
        ForeignKey(f'{DB_NAME}.employee_category.id', ondelete='CASCADE'),
        nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    country_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.country.id', ondelete='CASCADE'),
        nullable=False)
    city_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.city.id', ondelete='CASCADE'),
        nullable=False)
    notes = Column(Text())

    service = relationship('Service', backref='employee')

    fields = [
        'first_name', 'last_name', 'phone', 'email', 'e_category_id',
        'start_date', 'end_date', 'country_id', 'city_id', 'address',
        'zip_code']
    qtypes = [
        xQLineEdit, xQLineEdit, xQLineEdit, xQLineEdit,
        xQEmployeeCategoryComboBox, xQEmployeeCategoryToolButton,
        xQDateEdit, xQDateEdit, xQCountryComboBox, xQCountryToolButton,
        xQCityComboBox, xQCityToolButton, xQLineEdit, xQLineEdit]

    def __str__(self):
        return f'Employee: {self.id}, {self.first_name} {self.last_name}'


class Reservation(Base):
    __tablename__ = 'reservation'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    customer_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.customer.id', ondelete='CASCADE'),
        nullable=False)
    agency_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.agency.id', ondelete='CASCADE'),
        nullable=False)
    apartment_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.apartment.id', ondelete='CASCADE'),
        nullable=False)
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    guests = Column(SmallInteger)
    amount = Column(Float(10))
    tax = Column(Float(10))
    deposit = Column(Float(10))
    notes = Column(Text())

    service = relationship('Service', backref='reservation')

    fields = [
        'customer_id', 'agency_id', 'apartment_id', 'checkin_date',
        'checkout_date', 'guests', 'amount', 'tax', 'deposit']
    qtypes = [
        xQCustomerComboBox, xQAgencyComboBox, xQApartmentComboBox,
        xQDateEdit, xQDateEdit, xQSpinBox, xQDoubleSpinBox,
        xQDoubleSpinBox, xQDoubleSpinBox]

    def __str__(self):
        return f'Reservation: {self.id}, {self.checkin_date} | {self.checkout_date}'


class ServiceType(Base):
    __tablename__ = 'service_type'
    __table_args__ = {'schema': DB_NAME}

    id = Column(SmallInteger, primary_key=True)
    s_type_name = Column(String(50), nullable=False)

    service = relationship('Service', backref='service_type')

    def __str__(self):
        return f'Service Type: {self.id}, {self.s_type_name}'


class ServiceCategory(Base):
    __tablename__ = 'service_category'
    __table_args__ = {'schema': DB_NAME}

    id = Column(SmallInteger, primary_key=True)
    s_category_name = Column(String(50), nullable=False)

    service = relationship('Service', backref='service_category')

    def __str__(self):
        return f'Service Category: {self.id}, {self.s_category_name}'


class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {'schema': DB_NAME}

    id = Column(Integer, primary_key=True)
    entity_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.entity.id', ondelete='CASCADE'),
        nullable=False,
        unique=True)
    reservation_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.reservation.id', ondelete='CASCADE'),
        nullable=False)
    s_category_id = Column(
        SmallInteger,
        ForeignKey(f'{DB_NAME}.service_category.id', ondelete='CASCADE'),
        nullable=False)
    s_type_id = Column(
        SmallInteger,
        ForeignKey(f'{DB_NAME}.service_type.id', ondelete='CASCADE'),
        nullable=False)
    employee_id = Column(
        Integer,
        ForeignKey(f'{DB_NAME}.employee.id', ondelete='CASCADE'),
        nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    hours = Column(Time, nullable=False)
    extra_price = Column(Float(10))
    notes = Column(Text())

    fields = [
        'reservation_id', 's_category_id', 's_type_id', 'employee_id',
        'date', 'time', 'hours', 'extra_price']
    qtypes = [
        xQReservationComboBox, xQServiceCategoryComboBox,
        xQServiceCategoryToolButton, xQServiceTypeComboBox,
        xQServiceTypeToolButton, xQEmployeeComboBox, xQDateEdit,
        xQTimeEdit, xQTimeEdit, xQDoubleSpinBox]

    def __str__(self):
        return f'Service: {self.id} | reservation: {self.reservation_id}), date: {self.date}'
