import os
import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output

import plotly.express as px

import pandas as pd

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Estimate, NameJSON
from cloud_config import DATABASE_URI

import us

# DATABASE_URL = os.environ['DATABASE_URL']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
engine = create_engine(DATABASE_URI)
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
    
    return df


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

initial_fig = px.line(
    range_x=[1960, 2019],
    range_y=[0, 1000]
)

app.layout = html.Div(
    [
        html.Br(),
        dcc.Dropdown(id="name-dropdown"),
        html.Br(),
        dcc.Graph(
            id="name-plot",
            figure=initial_fig,
        ),
    ]
)


@app.callback(
    Output("name-dropdown", "options"),
    Input("name-dropdown", "search_value")
)
def update_dropdown(search_value):
    if not search_value:
        raise dash.exceptions.PreventUpdate
    return [ {'label': v, 'value': v} for v in possible_names(search_value) ]

@app.callback(
    Output("name-plot", "figure"),
    Input("name-dropdown", "value")
)
def update_graph(value):
    if not value:
        raise dash.exceptions.PreventUpdate

    if value:
        df = get_name(value)
        groups = ['year', 'gender']
        fig = px.line(
            df.groupby(groups)['births'].sum().reset_index(),
            x='year',
            y='births',
            line_group='gender',
            color='gender',
            color_discrete_map={'Female': 'red', 'Male': 'blue'}
        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)