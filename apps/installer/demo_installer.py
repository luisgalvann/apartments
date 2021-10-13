from sqlalchemy import create_engine
from common.connections.alchemy_cn import main_engine, alch_session
from apps.apartments.models.apartments_mdl import *
from common.managers.language_mgr import LangManager
from datetime import time, date, datetime, timedelta
from unidecode import unidecode
import pandas as pd
import random as rd


DB_PATH = 'sqlite:///common/resources/dbs/demo.db'


class DemoInstaller:
    def __init__(self):
        demo_engine = create_engine(DB_PATH)
        self.countries = pd.read_sql('countries', demo_engine)
        self.cities = pd.read_sql('cities', demo_engine)
        self.addresses = pd.read_sql('addresses', demo_engine)
        self.names = pd.read_sql('names', demo_engine)
        self.surnames = pd.read_sql('surnames', demo_engine)
        self.agency_names = pd.read_sql('agencies', demo_engine)
        self.apartment_names = pd.read_sql('apartments', demo_engine)

        self.cities = self.cities.rename(columns={'id': 'city_id'})
        self.name_details = pd.merge(
            self.names, self.surnames, on='country_id')
        df = pd.merge(self.countries, self.cities,
                      left_on='id', right_on='country_id')
        df = pd.merge(df, self.addresses, on='country_id')
        self.address_details = df.rename(columns={'city_id_x': 'city_id'})

        self.our_country = 1
        self.our_city = 5
        self.start_year = 2020
        self.start_month = 1
        self.min_res_apt = 2
        self.max_res_apt = 5

        self.total_agencies = 5
        self.total_owners = 5
        self.total_apartments = 10
        self.total_hosts = 2
        self.total_cleaners = 2

        self.create_main_objects()
        self.create_reservations()

    def create_main_objects(self):
        with alch_session() as session:
            for country_data in self.countries.itertuples():
                country = Country()
                country.country_name = country_data[2]
                session.add(country)
                print('Creating Country: ', country.country_name)

            for city_data in self.cities.itertuples():
                city = City()
                city.city_name = city_data[2]
                city.country_id = city_data[3]
                session.add(city)
                print('Creating City: ', city.city_name)

            for _ in range(self.total_agencies):
                agency = self.get_random_instance(Agency())
                self.add_entity(agency, session)
                print('Creating Agency: ', agency.agency_name)

            for _ in range(self.total_owners):
                owner = self.get_random_instance(Owner())
                self.add_entity(owner, session)
                print('Creating Owner: ', owner.first_name, owner.last_name)

            for _ in range(self.total_apartments):
                apartment = self.get_random_instance(
                    Apartment(), self.our_country, self.our_city)
                self.add_entity(apartment, session)
                print('Creating Apartment: ', apartment.apartment_name)

            for _ in range(self.total_hosts):
                employee = self.get_random_instance(
                    Employee(), self.our_country, self.our_city)
                employee.e_category_id = 1
                self.add_entity(employee, session)
                print('Creating Employee (host): ',
                      employee.first_name, employee.last_name)

            for _ in range(self.total_cleaners):
                employee = self.get_random_instance(
                    Employee(), self.our_country, self.our_city)
                employee.e_category_id = 2
                self.add_entity(employee, session)
                print('Creating Employee (cleaner): ',
                      employee.first_name, employee.last_name)

    def create_reservations(self):
        with alch_session() as session:
            apartments = pd.read_sql('apartment', main_engine)
            apartments = apartments[['id', 'max_guests']]

            for apartment_data in apartments.itertuples():
                checkin_date = date(
                    self.start_year, self.start_month, rd.randint(1, 28))

                for _ in range(rd.randint(self.min_res_apt, self.max_res_apt)):
                    customer = self.get_random_instance(Customer())
                    self.add_entity(customer, session)
                    print('Creating Customer:',
                          customer.first_name, customer.last_name)

                    reservation = Reservation()
                    reservation.customer_id = customer.id
                    reservation.agency_id = self.get_random_agency()
                    reservation.apartment_id = apartment_data[1]
                    reservation.guests = rd.randint(1, apartment_data[2])
                    reservation.checkin_date = checkin_date
                    rd_days = timedelta(total_days := rd.randint(2, 7))
                    reservation.checkout_date = checkin_date + rd_days
                    rd_amount = ((reservation.checkout_date -
                                 checkin_date).days * rd.randint(40, 75))
                    reservation.amount = round(rd_amount + rd.random(), 2)
                    reservation.tax = total_days * 2.00
                    reservation.deposit = round(reservation.amount / 3, 2)
                    reservation.notes = LangManager.lorem_ipsum(1)
                    self.add_entity(reservation, session)
                    stg = f'{reservation.apartment_id} | {checkin_date} - {reservation.checkout_date}'
                    print(f'Creating Reservation: apartment: {stg}')

                    free_employees = False
                    loop = 0

                    while not free_employees:
                        loop += 1
                        checkin_time = time(rd.randint(13, 23), 0)
                        cleaning_time = time(checkin_time.hour - 1)
                        services_date = self.format_date(checkin_date)
                        host_id = self.get_random_employee(
                            services_date, checkin_time, 1)
                        cleaner_id = self.get_random_employee(
                            services_date, cleaning_time, 2)

                        if host_id and cleaner_id:
                            service_cleaner = Service()
                            service_cleaner.reservation_id = reservation.id
                            service_cleaner.s_category_id = 3
                            x = 3 if checkin_date.weekday() > 4 else 1 if checkin_time.hour > 8 else 2
                            service_cleaner.s_type_id = x
                            service_cleaner.employee_id = cleaner_id
                            service_cleaner.date = checkin_date
                            service_cleaner.time = cleaning_time
                            service_cleaner.hours = timedelta(hours=1)
                            service_cleaner.extra_price = 0.00
                            service_cleaner.notes = LangManager.lorem_ipsum(1)
                            self.add_entity(service_cleaner, session)

                            service_host = Service()
                            service_host.reservation_id = reservation.id
                            service_host.s_category_id = 1
                            x = 3 if checkin_date.weekday() > 4 else 1 if checkin_time.hour > 8 else 2
                            service_host.s_type_id = x
                            service_host.employee_id = host_id
                            service_host.date = checkin_date
                            service_host.time = checkin_time
                            service_host.hours = timedelta(hours=1)
                            service_host.extra_price = 0.00
                            service_host.notes = LangManager.lorem_ipsum(1)
                            self.add_entity(service_host, session)

                            stg = f'Creating Service: R[{reservation.id}]'
                            print(
                                f'{stg} | Cleaning: {cleaning_time} Check-in: {checkin_time}')
                            free_employees = True
                        if loop > 50:
                            print(
                                'No se realizarán los servicios de check-in para esta reserva')
                            break

                    free_employees = False
                    loop = 0

                    while not free_employees:
                        loop += 1
                        checkout_date = reservation.checkout_date
                        checkout_time = time(rd.randint(7, 11))
                        cleaning_time = time(checkout_time.hour + 1)
                        services_date = self.format_date(checkout_date)
                        host_id = self.get_random_employee(
                            services_date, checkout_time, 1)
                        cleaner_id = self.get_random_employee(
                            services_date, cleaning_time, 2)

                        if host_id and cleaner_id:
                            service_host = Service()
                            service_host.reservation_id = reservation.id
                            service_host.s_category_id = 2
                            x = 3 if checkout_date.weekday() > 4 else 1 if checkout_time.hour > 8 else 2
                            service_host.s_type_id = x
                            service_host.employee_id = host_id
                            service_host.date = checkout_date
                            service_host.time = checkout_time
                            service_host.hours = timedelta(hours=1)
                            service_host.extra_price = 0.00
                            service_host.notes = LangManager.lorem_ipsum(1)
                            self.add_entity(service_host, session)

                            service_cleaner = Service()
                            service_cleaner.reservation_id = reservation.id
                            service_cleaner.s_category_id = 3
                            x = 3 if checkout_date.weekday() > 4 else 1 if cleaning_time.hour > 8 else 2
                            service_cleaner.s_type_id = x
                            service_cleaner.employee_id = cleaner_id
                            service_cleaner.date = reservation.checkout_date
                            service_cleaner.time = cleaning_time
                            service_cleaner.hours = timedelta(hours=1)
                            service_cleaner.extra_price = 0.00
                            service_cleaner.notes = LangManager.lorem_ipsum(1)
                            self.add_entity(service_cleaner, session)

                            stg = f'Creating Service: R[{reservation.id}]'
                            print(
                                f'{stg} | Check-out: {checkout_time} Cleaning: {cleaning_time}')
                            free_employees = True
                        if loop > 50:
                            print(
                                'No se realizarán los servicios de check-out para esta reserva')
                            break

                    checkin_date = reservation.checkout_date + \
                        timedelta(rd.randint(1, 5))

    def add_entity(self, instance, session):
        entity = Entity()
        session.add(entity)
        session.commit()
        instance.entity_id = entity.id
        session.add(instance)
        session.commit()

    def format_date(self, srv_date):
        day = srv_date.day if srv_date.day > 9 else '0' + str(srv_date.day)
        month = srv_date.month if srv_date.month > 9 else '0' + \
            str(srv_date.month)
        formatted_date = f'{srv_date.year}-{month}-{day}'
        return formatted_date

    def format_string(self, string):
        string = string.lower().replace("'", '').replace(' ', '')
        formatted_string = unidecode(string, 'utf-8')
        return formatted_string

    def get_random_owner(self):
        owners = pd.read_sql('owner', main_engine)
        apartments = pd.read_sql('apartment', main_engine)

        all_owners = set(owners['id'])
        owners_with_apartment = set(apartments['owner_id'])
        owners_without_apartment = all_owners - owners_with_apartment
        if owners_without_apartment:
            return rd.choice(list(owners_without_apartment))
        return rd.choice(list(all_owners))

    def get_random_agency(self):
        agencies = pd.read_sql('agency', main_engine)
        reservations = pd.read_sql('reservation', main_engine)

        all_agencies = set(agencies['id'])
        agencies_with_reservation = set(reservations['agency_id'])
        agencies_without_reservation = all_agencies - agencies_with_reservation
        if agencies_without_reservation:
            return rd.choice(list(agencies_without_reservation))
        return rd.choice(list(all_agencies))

    def get_random_employee(self, srv_date, srv_time, emp_category):
        services = pd.read_sql('service', main_engine)
        employees = pd.read_sql('employee', main_engine)
        employees = employees[employees['e_category_id'] == emp_category]
        all_employees_in_category = set(employees['id'])
        employees = pd.merge(services, employees,
                             left_on='employee_id', right_on='id')
        employees = employees[(employees['time'] == srv_time) & (
            employees['date'] == srv_date)]
        not_free_employees_in_category = set(employees['employee_id'])
        free_employees_in_category = all_employees_in_category - \
            not_free_employees_in_category
        if not free_employees_in_category:
            return None
        return rd.choice(list(free_employees_in_category))

    def get_random_instance(self, instance, country_id=None, city_id=None):
        if not country_id:
            country_id = rd.choice(self.countries['id'])
        if not city_id:
            city_id = rd.choice(
                list(self.cities[self.cities['country_id'] == country_id]['city_id']))

        df = self.name_details
        df = df[df['country_id'] == country_id]
        name_details = df.iloc[rd.randint(0, len(df)-1)]
        df = self.address_details
        df = df[(df['country_id'] == country_id) & (df['city_id'] == city_id)]
        address_details = df.iloc[rd.randint(0, len(df)-1)]

        attributes = [x for x in dir(instance) if not callable(x)]
        has = lambda x: x in attributes

        instance.country_id = int(country_id)
        instance.city_id = int(city_id)

        if has('first_name'):
            instance.first_name = name_details['name']
        if has('last_name'):
            instance.last_name = name_details['surname']
        if has('language'):
            instance.language = address_details['language']
        if has('address'):
            instance.address = f'{address_details["address"]}, {rd.randint(1, 5)}'
        if has('zip_code'):
            instance.zip_code = address_details['zip_code']
        if has('notes'):
            instance.notes = LangManager.lorem_ipsum(1)
        if has('apartment_name'):
            instance.apartment_name = rd.choice(
                self.apartment_names['apartment'])
        if has('max_guests'):
            instance.max_guests = rd.randint(2, 8)
        if has('parking_spaces'):
            instance.parking_spaces = rd.randint(0, 3)
        if has('agency_name'):
            instance.agency_name = rd.choice(self.agency_names['agency'])
        if has('contact_person'):
            instance.contact_person = f'{name_details["name"]} {name_details["surname"]}'
        if has('phone'):
            instance.phone = f'{address_details["prefix"]} {rd.randint(615746368, 698365826)}'
        if has('cp_phone'):
            instance.cp_phone = f'{address_details["prefix"]} {rd.randint(615746368, 698365826)}'
        if has('email') and has('agency_name'):
            instance.email = self.format_string(
                instance.agency_name) + '@gmail.com'
        elif has('email'):
            instance.email = self.format_string(
                instance.first_name + instance.last_name) + '@gmail.com'
        if has('website'):
            instance.website = self.format_string(
                instance.agency_name) + '.com'
        if has('start_date'):
            instance.start_date = datetime(
                self.start_year, self.start_month, 1)
        if has('end_date'):
            instance.end_date = instance.start_date - timedelta(1)
        if has('owner_id'):
            instance.owner_id = self.get_random_owner()

        return instance


if __name__ == '__main__':
    start = datetime.now()
    installer = DemoInstaller()
    end = datetime.now() - start
    print(f'{str(end)[:-3]} milliseconds)'.replace('.', ' ('))
