import unittest
from unittest import TestCase
from common.connections.alchemy_cn import *


class DatabaseTest(TestCase):
    ''' Check SQLAlchemy connection to database '''

    def test_singleton_session(self):
        ''' Check if all instances sessions are the same '''

        with alch_session() as first_session:
            pass

        with alch_session() as second_session:
            pass

        self.assertIs(first_session, second_session)


    def test_tables_in_database(self):
        ''' Check if all tables are created in the database '''

        tables = [
            'agency', 'apartment', 'city', 'country', 'customer', 'document', 
            'employee', 'employee_category', 'entity', 'owner', 'reservation', 
            'service', 'service_category', 'service_type']

        for table in tables:
            self.assertTrue(main_engine.has_table(table))


    def test_query_models(self):
        ''' Check if all models can be queried from database '''

        models = [
            Agency, Apartment, City, Country, Customer, Document, 
            Employee, EmployeeCategory, Entity, Owner, Reservation, 
            Service, ServiceCategory, ServiceType]

        with alch_session() as session:
            for model in models:
                records = session.query(model).count()
                self.assertGreaterEqual(records, 0)


if __name__ == '__main__':
    unittest.main()
