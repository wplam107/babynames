import requests
import us
from bs4 import BeautifulSoup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI
from models import Base, StateEntry


def main():
    states = [ state.name for state in us.states.STATES ] + ['District of Columbia']
    engine = create_engine(DATABASE_URI, executemany_mode='batch')
    Session = sessionmaker(bind=engine)
    s = Session()
    Base.metadata.bind = engine
    Base.metadata.drop_all(tables=[StateEntry.__table__])
    Base.metadata.create_all(tables=[StateEntry.__table__])

    url = 'https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_historical_population'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")

    pop_table = soup.find_all('table')[3]
    rows = pop_table.find_all('tr')[1:]
    objects = []
    for row in rows:
        cols = row.find_all('td')
        state = cols[0].find('a').text
        if state in states:
            for i, year in enumerate(range(1960, 2020, 10)):
                j = i + 1
                population = ''.join(cols[j].text.rstrip().split(','))
                syp = StateEntry(
                    state=state,
                    year=year,
                    population=population
                )
                objects.append(syp)
        else:
            pass

    s.bulk_save_objects(objects)
    s.commit()
    s.close()


if __name__ == '__main__':
    main()