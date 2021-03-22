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

# Unique names query and state names
NAMES = [ name[0] for name in s.query(NameJSON.name).all() ]
STATES = [ f'{state.name}' for state in us.states.STATES ] + ['District of Columbia']
STATE_ABBR = [ f'{state.abbr}' for state in us.states.STATES ] + ['DC']

# Retrieve state population estimates
q = s.query(Estimate).all()
result = [
    {'state': v.state, 'year': int(v.year), 'population': int(v.population)}
    for v in q
]
POP_DF = pd.DataFrame(result)

def get_name(name):
    '''
    Function to produce DataFrame (year, state, births) from query by name.
    '''

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