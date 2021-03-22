import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db import NAMES, STATES, STATE_ABBR, POP_DF, get_name

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
        if (search_value.lower() or search_value)
        in o['label'].lower() or o['value'].lower() or o['label'] or o['value']
        in (value or [])
    ]

@app.callback(
    Output("name-plot", "figure"),
    Output("map-plot", "figure"),
    Input("name-dropdown", "value"),
    Input("state-dropdown", "value"),
    Input("rate-checkbox", "value")
)
def update_graph(value, s_ids, rate):
    if value:
        fig = go.Figure(layout_xaxis_range=[1960, 2020])
        map_fig = go.Figure()
        if rate:
            title = 'Baby Name by Population:'
            y_title = 'Births / 1M (pop.)'
        else:
            title = 'Baby Name(s) Totals:'
            y_title = 'Total Births'

        # For each name
        for val in value:
            df = get_name(val.capitalize())
            title = title + f' {val}'
            if val != value[-1]:
                title = title + ', '
                
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
        return [fig, map_fig]

    else:
        return [initial_fig, initial_map]


if __name__ == '__main__':
    app.run_server(debug=True)