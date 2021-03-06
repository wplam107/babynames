import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db import NAMES, STATES, STATE_ABBR, POP_DF, get_name
from search import find_alts

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
name_options = [ {'label': name, 'value': name} for name in NAMES ]
state_options = [ {'label': state, 'value': state} for state in STATES ]
state_dict = { s: a for s, a in zip(STATES, STATE_ABBR) }

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

initial_fig = px.line(
    range_x=[1960, 2019],
    range_y=[0, 1000]
)
initial_fig.update_layout(
    title_text='Baby Names by Year'
)

initial_map = go.Figure(data=go.Choropleth(
    locations=STATE_ABBR,
    z=[],
    locationmode='USA-states',
    colorscale='cividis',
    colorbar_title='Births',
))
initial_map.update_layout(title_text='Peak Baby Name Popularity by State', geo_scope='usa')

app.layout = html.Div(
    [
        html.H1(children=[
            'Baby Names Dashboard',
            html.A(
                html.Img(
                    src='assets/GitHub-Mark-64px.png',
                    style={'float': 'right', 'height': '50px'}
                ), href='https://github.com/wplam107/babynames'
            )
        ]),
        html.P('Data: US Social Security Office, US Census Bureau'),
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
        html.Div(children=[
            dcc.Checklist(
                id="rate-checkbox",
                options=[
                    {'label': 'Per Million (Pop.)', 'value': 'rate'},
                ],
            ),
            dcc.Checklist(
                id="alts-checkbox",
                options=[
                    {'label': 'Include Alternative Spellings', 'value': 'alt_names'},
                ]
            ),
            dcc.Checklist(
                id="color-checkbox",
                options=[
                    {'label': 'Log Color Spectrum', 'value': 'log_color'},
                ]
            ),
        ], style={"display": "flex"}),
        html.Div(id="alt-labels"),
        html.Br(),
        html.Div(children=
            [
                html.Div(dcc.Graph(
                    id="name-plot",
                    figure=initial_fig,
                    # style={"width": "50%"},
                ), className='six columns'),
                html.Div(dcc.Graph(
                    id="map-plot",
                    figure=initial_map,
                    # style={"width": "50%"},
                ), className='six columns'),
            ]
        ),
    ]
)

# Update name dropdown options
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
        if search_value.lower() in o['value'].lower()
        or o['value'] in (value or [])
    ]

# Update both plots
@app.callback(
    Output("name-plot", "figure"),
    Output("map-plot", "figure"),
    Output("alt-labels", "children"),
    Input("name-dropdown", "value"),
    Input("state-dropdown", "value"),
    Input("rate-checkbox", "value"),
    Input("alts-checkbox", "value"),
    Input("color-checkbox", "value"),
)
def update_graph(value, s_ids, rate, alt_names, log_color):
    if value:
        fig = go.Figure(layout_xaxis_range=[1960, 2020])
        map_fig = go.Figure()
        if rate:
            title = 'Baby Name(s) Births by Population:'
            y_title = 'Births / 1M (pop.)'
        else:
            title = 'Baby Name(s) Birth Totals:'
            y_title = 'Total Births'

        alt_label = ''
        if alt_names:
            alt_label = 'Alternatives Include:'

        # For each name
        for val in value:
            df = get_name(val.capitalize())
            title = title + f' {val}'
            if val != value[-1]:
                title = title + ','

            if alt_names:
                alternatives = [
                    name.capitalize() for name in find_alts(val.lower(), alts=[], checked=[])
                    if name.lower() != val.lower()
                ]

                alt_label = alt_label + f' {alternatives}'
                if val != value[-1]:
                    alt_label = alt_label + ','

                for alt in alternatives:
                    df = pd.concat([df, get_name(alt)])
                df = df.groupby(['year', 'state'])['births'].sum().reset_index()

            groups = ['year'] # Groups in case add gender splits

            # Make map plot of first entered name
            if val == value[0]:
                temp = df.merge(POP_DF, on=['year', 'state'], how='left')
                temp = temp.groupby(['state', 'year', 'population'])['births'].sum()
                temp = temp.reset_index()
                temp['b_rate'] = temp['births'] / (temp['population'] / 1000000)
                locations = []
                z = []
                text = []
                for state in STATES:
                    sd = temp.loc[temp['state'] == state].set_index('year')['b_rate']
                    year = sd.idxmax()
                    b_rate = sd.max()
                    text.append(f'State: {state}<br>Peak Year: {year}<br>Peak Birth Rate: {b_rate}')
                    z.append(b_rate)
                    locations.append(state_dict[state])

                if log_color:
                    map_fig.add_trace(go.Choropleth(
                        locations=locations,
                        z=np.nan_to_num(np.log10(z)),
                        hovertext=text,
                        hoverinfo='text',
                        locationmode='USA-states',
                        colorscale='cividis',
                        zmin=0,
                        zmax=3,
                        colorbar=dict(tickvals=[0,1,2,3], ticktext=['0','10','100','1000']),
                        colorbar_title='Peak Birth Rate (Log10)',
                        marker_line_color='white'
                    ))
                else:
                    map_fig.add_trace(go.Choropleth(
                        locations=locations,
                        z=z,
                        hovertext=text,
                        hoverinfo='text',
                        locationmode='USA-states',
                        colorscale='cividis',
                        colorbar_title='Peak Birth Rate',
                        marker_line_color='white'
                    ))
                map_fig.update_layout(
                    title_text=f'Peak "{val}" Popularity by State',
                    geo_scope='usa'
                )
            
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

        fig.update_layout(
            title=title,
            xaxis_title='Year',
            yaxis_title=y_title,
            legend_title='Name Legend'
        )
        return [fig, map_fig, alt_label]

    else:
        return [initial_fig, initial_map, None]



if __name__ == '__main__':
    app.run_server(debug=True)