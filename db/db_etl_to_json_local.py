import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI
from models import NameEntry, NameJSON, Base

import us

engine = create_engine(DATABASE_URI, executemany_mode='batch')
Session = sessionmaker(bind=engine)
states = [ f'{state.name}' for state in us.states.STATES ] + ['District of Columbia']

def get_ys_totals(name):
    '''
    Function to retrieve name entries.
    '''
    
    s = Session()
    q = s.query(NameEntry).\
    filter(NameEntry.name == name).\
    all()
    
    s.close()

    return [
        {'state': v.state,
         'year': v.year,
         'name': v.name,
         'gender': v.gender,
         'births': v.births}
        for v in q
    ]

def get_birth_totals(name):
    '''
    Function to retrieve total births by name entry.
    '''

    s = Session()
    q = s.query(sa.func.sum(NameEntry.births)).\
        filter(NameEntry.name == name).\
        all()

    s.close()

    return q[0][0]


def to_json(name_data):
    '''
    Function to convert name entries into a single JSON by name
    '''
    
    states = [ state.name for state in us.states.STATES ] + ['District of Columbia']
    json_data = {
        "Female": { f"{state}": {} for state in states },
        "Male": { f"{state}": {} for state in states }
    }

    for entry in name_data:
        json_data[entry['gender']][entry['state']][f"{entry['year']}"] = entry['births']
        
    return json_data

def main():
    # Get all distinct names from 'babynames' table
    s = Session()
    q = s.query(sa.distinct(NameEntry.name)).all()
    all_names = [ v[0] for v in q ]

    # Create table
    Base.metadata.bind = engine
    Base.metadata.drop_all(tables=[NameJSON.__table__])
    Base.metadata.create_all(tables=[NameJSON.__table__])

    s.close()

    objects = []
    for name_entry in all_names:
        totals = get_ys_totals(name_entry)
        json_data = to_json(totals)
        birth_totals = get_birth_totals(name_entry)
        obj = NameJSON(
            name=name_entry,
            data=json_data,
            birth_totals=birth_totals
        )
        objects.append(obj)

    s.bulk_save_objects(objects)
    s.commit()
    s.close()

if __name__ == '__main__':
    main()