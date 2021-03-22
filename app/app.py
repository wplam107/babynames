import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db import NAMES, STATES, POP_DF, get_name

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
name_options = [ {'label': name, 'value': name} for name in NAMES ]
state_options = [ {'label': state, 'value': state} for state in STATES ]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

initial_fig = px.line(
    range_x=[1960, 2019],
    range_y=[0, 1000]
)

app.layout = html.Div(
    [
        html.Br(),
        html.Label(
            [
                'Choose Name(s):',
                dcc.Dropdown(
                    id="name-dropdown",
                    placeholder="Select Name",
                    multi=True
                ),
            ]
        ),
        html.Label(
            [
                'Choose State(s):',
                dcc.Dropdown(
                    id="state-dropdown",
                    options=state_options,
                    placeholder='All',
                    multi=True,
                ),
            ]
        ),
        dcc.Checklist(id="rate-checkbox", options=[{'label': 'Per Million (Pop.)', 'value': 'rate'}]),
        html.Br(),
        dcc.Graph(
            id="name-plot",
            figure=initial_fig,
        ),
    ]
)


@app.callback(
    Output("name-dropdown", "options"),
    Input("name-dropdown", "search_value"),
    State("name-dropdown", "value")
)
def update_nd(search_value, value):
    if not search_value:
        raise dash.exceptions.PreventUpdate
    return [
        o for o in name_options
        if search_value in o['label'] or o['value'] in (value or [])
    ]

@app.callback(
    Output("name-plot", "figure"),
    Input("name-dropdown", "value"),
    Input("state-dropdown", "value"),
    Input("rate-checkbox", "value")
)
def update_graph(value, s_ids, rate):
    if value:
        fig = go.Figure(layout_xaxis_range=[1960, 2020])
        if rate:
            title = 'Baby Name by Population'
            y_title = 'Births / 1M (pop.)'
        else:
            title = 'Baby Name(s) Totals'
            y_title = 'Total Births'
        fig.update_layout(
            title=title,
            xaxis_title='Year',
            yaxis_title=y_title,
            legend_title='Name, Year Legend'
        )

        # For each name
        for val in value:
            df = get_name(val)
            groups = ['year']
            
            # If state(s) is selected
            if s_ids:
                groups.append('state')
                data = df.groupby(groups)['births'].sum().reset_index()
                data = data.merge(POP_DF, on=['year', 'state'], how='left')

                # For each state
                for s_id in s_ids:
                    y = data.loc[data['state'] == s_id]['births']

                    # If per 1M selected
                    if rate:
                        y = y / (data.loc[data['state'] == s_id]['population'] / 1000000)

                    fig.add_trace(go.Scatter(
                        name=f'Name: {val}, State: {s_id}',
                        x=data.loc[data['state'] == s_id]['year'],
                        y=y,
                        mode='markers+lines'
                    ))

            else:
                data = df.groupby(groups)['births'].sum().reset_index()
                y = data['births']

                # If per 1M selected
                if rate:
                    pop = POP_DF.groupby('year')['population'].sum().reset_index()
                    data = data.merge(pop, on=['year'], how='left')
                    y = y / (data['population'] / 1000000)  

                fig.add_trace(go.Scatter(
                    name=f'Name: {val}',
                    x=data['year'],
                    y=y,
                    mode='markers+lines'
                ))

        return fig

    else:
        return initial_fig


if __name__ == '__main__':
    app.run_server(debug=True)