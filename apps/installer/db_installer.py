from apps.apartments.models.apartments_mdl import *
from common.connections.alchemy_cn import main_engine, alch_session


Base.metadata.drop_all(main_engine)
Base.metadata.create_all(main_engine)

with alch_session() as session:
    for stg in ('Host', 'Cleaner'):
        instance = EmployeeCategory(e_category_name=stg)
        session.add(instance)

    for stg in ('Day-time', 'Night-time', 'Weekend', 'Holiday'):
        instance = ServiceType(s_type_name=stg)
        session.add(instance)

    for stg in ('Check-in', 'Check-out', 'Cleaning', 'Extra'):
        instance = ServiceCategory(s_category_name=stg)
        session.add(instance)

for table in Base.metadata.sorted_tables:
    print(f'{table.schema}: {table.name}')
