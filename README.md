# Baby Names Web App/Dashboard
- App: [Heroku](https://us-babynames.herokuapp.com/)
- Packages: [Dash](https://plotly.com/), [Plotly](https://plotly.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Pandas](https://pandas.pydata.org/), [US](https://github.com/unitedstates/python-us)
- Database: PostgreSQL
- Data:
  - Top 100 Baby Names by State by Year: [US Social Security Office](https://www.ssa.gov/oact/babynames/)
  - Historical US Populations (by state): [Wikipedia](https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_historical_population)
  - Recent Decade US Populations (by state): [US Census Bureau](https://www.census.gov/data/tables/time-series/demo/popest/2010s-state-total.html)

## Purpose:
- To work with SQL, PostgreSQL, and SQLAlchemy.
- To create data visualizations.
- To better understand dashboarding.

## Notes:
- A name is searchable if it has made the top 100 baby names of any state (and District of Columbia) from 1960 through 2019.
- Dash app in ```app``` directory.
- Local database and data scrape files located in ```db``` directory.
- Notebooks:
  - Creating Population Estimates by State: [```pop_est_nb.ipynb```](https://github.com/wplam107/babynames/blob/main/db/pop_est_nb.ipynb)
  - Data Transformation for Heroku PostgreSQL: [```etl_to_json_nb.ipynb```](https://github.com/wplam107/babynames/blob/main/db/etl_to_json_nb.ipynb)
