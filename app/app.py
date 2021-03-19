import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output

import pandas as pd

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Estimate, NameJSON
from config import DATABASE_URI

import us

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
engine = create_engine(DATABASE_URI, executemany_mode='batch')
Session = sessionmaker(bind=engine)
s = Session()

names = [ name[0] for name in s.query(NameJSON.name).all() ]
states = [ f'{state.name}' for state in us.states.STATES ] + ['District of Columbia']

def possible_names(name):
    q = s.query(NameJSON.name).filter(NameJSON.name.ilike(f'%{name}%')).\
    order_by(NameJSON.birth_totals.desc()).\
    limit(10)
    results = [ v[0] for v in q ]
    
    return results

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Br(),
        dcc.Input(id="input1", type="text", placeholder="Baby Name"),
        html.Div(id="output"),
    ]
)


@app.callback(
    Output("output", "children"),
    Input("input1", "value"),
)
def update_output(input1):
    if input1 == 'Names in Database:':
        return None
    else:
        names = ', '.join(possible_names(input1))
        return 'Names in Database: {}'.format(names)


if __name__ == "__main__":
    app.run_server(debug=True)