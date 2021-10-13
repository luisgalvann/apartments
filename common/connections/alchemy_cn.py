from contextlib import contextmanager
from apps.apartments.models.apartments_mdl import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import label
from common.data.constants import CONN_STRING


main_engine = create_engine(CONN_STRING)
Session = sessionmaker(main_engine)
session = Session()


@contextmanager
def alch_session():
    ''' Return the same session instance every time.
    The session must not be closed in a finally sentence'''

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise


# ============ Top queries ============
# Set of queries used in the top table

def res_top_query():
    with alch_session() as session:
        query = session.query(
            Reservation.id, func.concat(Customer.first_name, ' ', 
            Customer.last_name).label('customer'), Agency.agency_name,
            Apartment.apartment_name, Reservation.checkin_date,
            Reservation.checkout_date, Reservation.guests,
            Reservation.amount, Reservation.tax, Reservation.deposit, 
            Reservation.notes
            ).filter(Reservation.customer_id == Customer.id
            ).filter(Reservation.agency_id == Agency.id
            ).filter(Reservation.apartment_id == Apartment.id)
    return query


def srv_top_query():
    with alch_session() as session:
        query = session.query(
            Service.id, ServiceCategory.s_category_name, 
            ServiceType.s_type_name, func.concat(
            Employee.first_name, ' ', Employee.last_name
            ).label('employee'), Service.date, Service.time, 
            Service.hours, Service.extra_price, Service.notes
            ).filter(Service.reservation_id == Reservation.id
            ).filter(Service.s_category_id == ServiceCategory.id
            ).filter(Service.s_type_id == ServiceType.id
            ).filter(Service.employee_id == Employee.id)
    return query


def cus_top_query():
    with alch_session() as session:
        query = session.query(
            Customer.id, Customer.first_name, Customer.last_name, 
            Customer.phone, Customer.email, Customer.language, 
            Country.country_name, City.city_name, Customer.address, 
            Customer.zip_code, Customer.notes
            ).filter(Customer.id == Customer.id
            ).filter(Customer.country_id == Country.id
            ).filter(Customer.city_id == City.id)
    return query


def emp_top_query():
    with alch_session() as session:
        query = session.query(
            Employee.id, Employee.first_name, Employee.last_name, 
            Employee.phone, Employee.email, EmployeeCategory.e_category_name, 
            Employee.start_date, Employee.end_date, Country.country_name, 
            City.city_name, Employee.address, Employee.zip_code, Employee.notes
            ).filter(Employee.e_category_id == EmployeeCategory.id
            ).filter(Employee.country_id == Country.id
            ).filter(Employee.city_id == City.id)
    return query


def agn_top_query():
    with alch_session() as session:
        query = session.query(
            Agency.id, Agency.agency_name, Agency.phone, Agency.contact_person, 
            Agency.cp_phone, Agency.email, Agency.website, Country.country_name, 
            City.city_name, Agency.address, Agency.zip_code, Agency.notes
            ).filter(Agency.country_id == Country.id
            ).filter(Agency.city_id == City.id)
    return query


def own_top_query():
    with alch_session() as session:
        query = session.query(
            Owner.id, Owner.first_name, Owner.last_name, Owner.phone, 
            Owner.email, Owner.language, Country.country_name, City.city_name, 
            Owner.address, Owner.zip_code, Owner.notes
            ).filter(Owner.country_id == Country.id
            ).filter(Owner.city_id == City.id)
    return query


def apt_top_query():
    with alch_session() as session:
        query = session.query(
            Apartment.id, Apartment.apartment_name, Apartment.phone, 
            func.concat(Owner.first_name, ' ', Owner.last_name).label('owner'), 
            Apartment.max_guests, Country.country_name, City.city_name, 
            Apartment.address, Apartment.zip_code, Apartment.parking_spaces, 
            Apartment.notes
            ).filter(Apartment.owner_id == Owner.id
            ).filter(Apartment.country_id == Country.id
            ).filter(Apartment.city_id == City.id)
    return query


# ============ Sub queries ============
# Set of queries used in the sub table

def res_sub_query():
    query = srv_top_query()
    return query

def srv_sub_query():
    query = res_top_query()
    query = query.filter(Reservation.id == Service.reservation_id)
    return query


def cus_sub_query():
    query = res_top_query()
    query = query.with_entities(
            Reservation.id, Agency.agency_name, Apartment.apartment_name, 
            Reservation.checkin_date, Reservation.checkout_date, 
            Reservation.guests, Reservation.amount, Reservation.tax, 
            Reservation.deposit, Reservation.notes)
    return query


def emp_sub_query():
    query = srv_top_query()
    query = query.with_entities(
        Service.id, ServiceCategory.s_category_name, ServiceType.s_type_name, 
        Service.date, Service.time, Service.hours,
        Service.extra_price, Service.notes)
    return query


def agn_sub_query():
    query = res_top_query()
    query = query.with_entities(
        Reservation.id, func.concat(Customer.first_name, ' ', Customer.last_name
        ).label('customer'), Apartment.apartment_name, Reservation.checkin_date, 
        Reservation.checkout_date, Reservation.guests, Reservation.amount, 
        Reservation.tax, Reservation.deposit, Reservation.notes)
    return query


def own_sub_query():
    query = apt_top_query()
    query = query.with_entities(
        Apartment.id, Apartment.apartment_name, Apartment.phone, 
        Apartment.max_guests, Country.country_name, City.city_name, 
        Apartment.address,  Apartment.zip_code,
        Apartment.parking_spaces, Apartment.notes)
    return query


def apt_sub_query():
    query = res_top_query()
    query = query.with_entities(
        Reservation.id, func.concat(Customer.first_name, ' ', 
        Customer.last_name).label('customer'), Agency.agency_name, 
        Reservation.checkin_date, Reservation.checkout_date, 
        Reservation.guests, Reservation.amount, Reservation.tax, 
        Reservation.deposit, Reservation.notes)
    return query
