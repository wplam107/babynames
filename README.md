# Baby Names Web App/Dashboard
- App: [Heroku](https://us-babynames.herokuapp.com/)
- Data: [US Social Security Office](https://www.ssa.gov/oact/babynames/)
- Packages: [Dash](https://plotly.com/), [Plotly](https://plotly.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Pandas](https://pandas.pydata.org/), [Us](https://github.com/unitedstates/python-us)
- Database: PostgreSQL

## Notes:
- A name is searchable if it has made the top 100 baby names of any state (and District of Columbia) from 1960 through 2019.
- Notebooks:
  - Creating Population Estimates by State: [```pop_est_nb.ipynb```](https://github.com/wplam107/babynames/blob/main/db/pop_est_nb.ipynb)
  - Data Transformation for Heroku PostgreSQL: [```etl_to_json_nb.ipynb```](https://github.com/wplam107/babynames/blob/main/db/etl_to_json_nb.ipynb)
