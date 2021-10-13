import unittest
from unittest import TestCase
from apps.apartments.models.apartments_mdl import *


class AbstractClassesTest(TestCase):
    ''' Check instantiation of abstract and hibrid classes '''

    def test_abstract_contact_error(self):
        with self.assertRaises(TypeError) as cm:
            instance = Contact()
        
        msg = "Can't instantiate abstract class Contact with abstract method __str__"
        self.assertEqual(msg, str(cm.exception))
  

    def test_abstract_address_error(self): 
        with self.assertRaises(TypeError) as cm:
            instance = Address()
        
        msg = "Can't instantiate abstract class Address with abstract method __str__"
        self.assertEqual(msg, str(cm.exception))


    def test_abstract_person_error(self):
        with self.assertRaises(TypeError) as cm:
            instance = Person()
        
        msg = "Can't instantiate abstract class Person with abstract method __str__"
        self.assertEqual(msg, str(cm.exception))


    def test_abstract_inheritance_error(self):
        class NewClass(Contact):
            pass

        with self.assertRaises(TypeError) as cm:
            instance = NewClass()

        msg = "Can't instantiate abstract class NewClass with abstract method __str__"
        self.assertEqual(msg, str(cm.exception))


    def test_abstract_inheritance(self):
        class NewClass(Person):
            def __str__(self):
                pass

        instance = NewClass()

        self.assertIsInstance(instance, NewClass)
        self.assertIsInstance(instance, Person)


    def test_hibrid_inheritance_error(self):
        with self.assertRaises(TypeError) as cm:
            class NewClass(Base, Person):
                def __str__(self):
                    pass

        msg = 'metaclass conflict: the metaclass of a derived class must be '\
              'a (non-strict) subclass of the metaclasses of all its bases'
        self.assertEqual(msg, str(cm.exception))


    def test_hibrid_inheritance(self):
        class NewClass(Base, Person, metaclass=HibridMeta):
            __tablename__ = 'newclass'

            id = Column(Integer, primary_key=True)

            def __str__(self):
                pass
        
        instance = NewClass()
        
        self.assertIsInstance(instance, NewClass)
        self.assertIsInstance(instance, Base)
        self.assertIsInstance(instance, Person)

        # The object is an instance of the class 
        # The class is an instance of the metaclass
        self.assertIsInstance(type(instance), HibridMeta)


class DBClassesTest(TestCase):
    ''' Check instantiation of database classes '''

    def test_entity_instantiation(self):
        instance = Entity()

        self.assertIsInstance(instance, Entity)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'entity')


    def test_document_instantiation(self):
        instance = Document()

        self.assertIsInstance(instance, Document)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'document')


    def test_country_instantiation(self):
        instance = Country()

        self.assertIsInstance(instance, Country)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'country')


    def test_city_instantiation(self):
        instance = City()

        self.assertIsInstance(instance, City)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'city')


    def test_customer_instantiation(self):
        instance = Customer()

        self.assertIsInstance(instance, Customer)
        self.assertIsInstance(instance, Base)
        self.assertIsInstance(instance, Person)
        self.assertIsInstance(type(instance), HibridMeta)
        self.assertEqual(instance.__tablename__, 'customer')


    def test_owner_instantiation(self):
        instance = Owner()

        self.assertIsInstance(instance, Owner)
        self.assertIsInstance(instance, Base)
        self.assertIsInstance(instance, Person)
        self.assertIsInstance(type(instance), HibridMeta)
        self.assertEqual(instance.__tablename__, 'owner')


    def test_agency_instantiation(self):
        instance = Agency()

        self.assertIsInstance(instance, Agency)
        self.assertIsInstance(instance, Base)
        self.assertIsInstance(instance, Contact)
        self.assertIsInstance(instance, Address)
        self.assertIsInstance(type(instance), HibridMeta)
        self.assertEqual(instance.__tablename__, 'agency')


    def test_apartment_instantiation(self):
        instance = Apartment()

        self.assertIsInstance(instance, Apartment)
        self.assertIsInstance(instance, Address)
        self.assertIsInstance(type(instance), HibridMeta)
        self.assertEqual(instance.__tablename__, 'apartment')


    def test_employee_category_instantiation(self):
        instance = EmployeeCategory()

        self.assertIsInstance(instance, EmployeeCategory)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'employee_category')


    def test_employee_instantiation(self):
        instance = Employee()

        self.assertIsInstance(instance, Employee)
        self.assertIsInstance(instance, Base)
        self.assertIsInstance(instance, Person)
        self.assertIsInstance(type(instance), HibridMeta)
        self.assertEqual(instance.__tablename__, 'employee')


    def test_reservation_instantiation(self):
        instance = Reservation()

        self.assertIsInstance(instance, Reservation)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'reservation')


    def test_service_type_instantiation(self):
        instance = ServiceType()

        self.assertIsInstance(instance, ServiceType)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'service_type')


    def test_service_category_instantiation(self):
        instance = ServiceCategory()

        self.assertIsInstance(instance, ServiceCategory)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'service_category')


    def test_service_instantiation(self):
        instance = Service()

        self.assertIsInstance(instance, Service)
        self.assertIsInstance(instance, Base)
        self.assertEqual(instance.__tablename__, 'service')


if __name__ == '__main__':
    unittest.main()
