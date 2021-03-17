from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI
from models import StateEntry, Estimate, Base

import numpy as np
import pandas as pd

import us


engine = create_engine(DATABASE_URI, executemany_mode='batch')
Session = sessionmaker(bind=engine)
states = [ f'{state.name}' for state in us.states.STATES ] + ['District of Columbia']

def get_pop_est(state, df):
    '''
    Function to create population estimates between census years
    '''
    
    years_ = range(1960, 2010)
    ps = np.array(df.loc[df['state'] == state]['population'])
    
    # Population slope between census data years
    ms = np.diff(ps) / 10
    
    # Initial population of decade
    cs = ps[:-1]
    
    # Create estimates through matrix operations
    ests = np.round((np.arange(0, 10).reshape(-1, 1) * ms + np.ones(10).reshape(-1,1) * cs)).T
    
    ests = [
        {'state': state, 'year': year, 'population': int(est)}
        for year, est in zip(years_, ests.flatten())
    ]
    
    return ests

def main():
    # Extract from database
    s = Session()
    q = s.query(StateEntry.state, StateEntry.year, StateEntry.population).all()
    s.close()

    # Transform to DataFrame
    pops = [ {'state': v[0], 'year': v[1], 'population': v[2]} for v in q ]
    pops = pd.DataFrame(pops)

    # Extract from Excel file, clean
    tens = pd.read_excel('data/nst-est2019-01.xlsx', index_col=0)
    tens = tens.loc[[ '.' + state for state in states ]]
    tens.index.name = 'state'
    tens = tens[[ f'Unnamed: {i}' for i in range(3, 13) ]]
    tens.columns = range(2010, 2020)
    tens.reset_index(inplace=True)
    tens['state'] = [ state[1:] for state in tens['state'] ]

    # Transform from wide to long
    df = tens.melt(
        id_vars='state',
        value_vars=range(2010, 2020),
        var_name='year',
        value_name='population'
    )

    # Concat data with estimates
    for state in states:
        df = pd.concat([df, pd.DataFrame(get_pop_est(state, pops))], ignore_index=True)

    # Transform to records entries
    data = df.to_dict('records')

    # Create table
    s = Session()
    Base.metadata.bind = engine
    Base.metadata.drop_all(tables=[Estimate.__table__])
    Base.metadata.create_all(tables=[Estimate.__table__])

    # Bulk write to database
    objects = []
    for datum in data:
        est = Estimate(
            state=datum['state'],
            year=datum['year'],
            population=datum['population']
        )
        objects.append(est)
    
    s.bulk_save_objects(objects)
    s.commit()
    s.close()


if __name__ == '__main__':
    main()