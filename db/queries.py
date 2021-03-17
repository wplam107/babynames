def usa_per_million(name, s):
    '''
    Function to make queries for births per 1 million in the USA.  Returns list of dictionaries.
    '''
    
    sub1 = s.query(NameEntry.year, NameEntry.gender, sa.func.sum(NameEntry.births).label('births')).\
    filter(NameEntry.name == name).\
    group_by(NameEntry.year, NameEntry.gender).\
    subquery()

    sub2 = s.query(Estimate.year, sa.func.sum(Estimate.population).label('population')).\
    group_by(Estimate.year).\
    subquery()

    q = s.query(
        sub1.c.year,
        sub1.c.gender,
        sa.cast(sub1.c.births, sa.Float()) / (sa.cast(sub2.c.population, sa.Float())/1000000)).\
    join(sub2, sub1.c.year == sub2.c.year).\
    all()
    
    return [ {'year': v[0], 'gender': v[1], 'births/1M_pop': v[2]} for v in q ]

def state_per_million(name, s):
    '''
    Function to make queries for births per 1 million by state.  Returns list of dictionaries.
    '''
    
    q = s.query(NameEntry.state,
                NameEntry.year,
                NameEntry.gender,
                sa.cast(NameEntry.births, sa.Float())/(sa.cast(Estimate.population, sa.Float())/1000000)
               ).\
    join(Estimate, sa.and_(NameEntry.state == Estimate.state, NameEntry.year == Estimate.year)).\
    filter(NameEntry.name == name).\
    all()

    return [ {'state': v[0], 'year': v[1], 'gender': v[2], 'births/1M_pop': v[3]} for v in q ]