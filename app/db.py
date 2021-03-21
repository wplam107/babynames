import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Estimate, NameJSON
# from cloud_config import DATABASE_URI
from config import DATABASE_URI

import us

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
s = Session()

NAMES = [ name[0] for name in s.query(NameJSON.name).all() ]
STATES = [ f'{state.name}' for state in us.states.STATES ] + ['District of Columbia']

def get_name(name):
    q = s.query(NameJSON).\
    filter(NameJSON.name == name).\
    all()

    female = pd.DataFrame(q[0].data['Female']).fillna(0).reset_index().rename(columns={'index': 'year'})
    male = pd.DataFrame(q[0].data['Male']).fillna(0).reset_index().rename(columns={'index': 'year'})

    female = female.melt(
        id_vars='year',
        value_vars=[ col for col in female.columns if col != 'year' ],
        var_name='state',
        value_name='births')
    female['gender'] = 'Female'
    male = male.melt(
        id_vars='year',
        value_vars=[ col for col in male.columns if col != 'year' ],
        var_name='state',
        value_name='births')
    male['gender'] = 'Male'

    df = pd.concat([female, male])
    df['year'] = df['year'].astype('int')
    df['births'] = df['births'].astype('int')
    
    return df