# imports
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_table
import plotly.graph_objects as go
import plotly.express as px



# functions
def get_state_label(value):
    for s in state_label_value:
        if s['value']==value:
            return s['label']


month_dict = {1: 'January',
              2: 'February',
              3: 'March',
              4: 'April',
              5: 'May',
              6: 'June',
              7: 'July',
              8: 'August',
              9: 'September',
              10: 'October',
              11: 'November',
              12: 'December'}


def map_months(m):
    #     m = int(m)
    if m < 1 or m > 12:
        return ''
    else:
        return month_dict[m]


def timeplot_title(plant, city, year):
    year_text = ''
    if year != 'All':
         year_text = ' for the Year: ' + str(year)
    return 'Time plot for Plant: ' + plant + ', ' + city + year_text

external_stylesheets = ['assets/opiods.css']

#Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]


# colors
BLUE_CONTAINER_COLOR = 'rgb(37,45,64)'
DARK_BLUE_HEADER_COLOR = 'rgb(28, 34, 48)'
SECONDARY_COLOR='#7fafdf'
HIGHLIGHT_COLOR='#2cfec1'

# Data Inits
DEFAULT_OPACITY = 0.8
state_init_selected = 'Select a State'
count_plants_state = ''
plant_table_headers = ['Plant', 'City', 'Total', 'Average', 'No. of Transactions']  # Plant table headers
dropdown_style_hidden = {
    'visibility': 'hidden',
        'margin-left': 20,
        'margin-right': 20
}
dropdown_style_visible = {
    'visibility': 'visible',
        'margin-left': 20,
        'margin-right': 20
}

# Data manipulation
invoice = pd.read_csv('data/dash_invoice.csv', low_memory=False)
invoice['Invoice Date']= pd.to_datetime(invoice['Invoice Date'])
# print(invoice.head())

state_agg = pd.DataFrame(invoice.groupby(['plant_state'])['Total Value'].sum()).reset_index()
metric = 'Total Value'
state_agg.loc[22] = ['Jammu and Kashmir',0]
state_agg.loc[13,'plant_state'] = ['Orissa']
# state_agg['text'] = state_agg['plant_state']+'<br>'+metric+': '+state_agg['Total Value'].astype(str)
state_plants_count = invoice.groupby('plant_state')['Plant'].nunique().sort_values()
# month yyyy
invoice['Month & Year'] = invoice['invoice_month'].map(map_months)
invoice['Month & Year'] =invoice['Month & Year'] + ' ' + invoice['invoice_year'].astype(str)
# YEARS
YEARS = list(invoice.invoice_year.unique())
YEARS.sort()

# map
geojson_link = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
bg_map_color = 'rgba(245,245,245,1)'
colorscale_map = 'Mint'
# colorscale_map = [
#     "#f2fffb",
#     "#bbffeb",
#     "#98ffe0",
#     "#79ffd6",
#     "#6df0c8",
#     "#69e7c0",
#     "#59dab2",
#     "#45d0a5",
#     "#31c194",
#     "#2bb489",
#     "#25a27b",
#     "#1e906d",
#     "#188463"
#     ]

india_map = go.Figure(data=go.Choropleth(
    geojson=geojson_link,
    featureidkey='properties.NAME_1', #ST_NM NAME_1
    locationmode='geojson-id',
    locations=state_agg['plant_state'],
    z=state_agg['Total Value'],


    autocolorscale=False,
    colorscale=colorscale_map,
    marker_line_color='black',

    colorbar=dict(
        title={'text': "TOTAL REVENUE"},

        thickness=15,
        len=0.35,
        bgcolor='rgba(220,220,220,0.8)',

        tick0=0,
        # dtick=20000,

        xanchor='left',
        x=.05,
        yanchor='bottom',
        y=0.05
    )
            )
               )

india_map.update_geos(
    resolution=50,
    showland=True, landcolor=bg_map_color,
    showocean=True, oceancolor=bg_map_color,
    visible=False,
    projection=dict(
        type='conic conformal',
        parallels=[12.472944444, 35.172805555556],
        rotation={'lat': 24, 'lon': 80}
    ),
    lonaxis={'range': [68, 98]},
    lataxis={'range': [6, 38]}
)

india_map.update_layout(
    title=dict(
        text="Total Value for States",
        xanchor='center',
        x=0.5,
        yref='paper',
        yanchor='bottom',
        y=0.9,
        pad={'b': 10}
    ),
    # text=state_agg['text'],
    margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    height=500,
    width=500

)
india_map.layout.plot_bgcolor = '#2bb489'
india_map.layout.paper_bgcolor = BLUE_CONTAINER_COLOR

# populate state for drop-down
state_label_value = []
states_list = invoice.plant_state.unique()
states_list.sort(axis=0)

for st in states_list:
    temp = {"label": st, "value": st}
    state_label_value.append(temp)
timeplot_options = [{'label': x, 'value': x} for x in ['Order type','Total']]
year_options = [{'label': str(x), 'value': str(x)} for x in YEARS]
year_options = [{'label': 'All', 'value': 'All'}] + year_options

# app-layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id='header',
            children=html.Div(
                # style={'color':'#7fafdf'},
                children=[html.H2(children='Mahindra FirstChoice Dash'),
                          html.P(id="description",
                                 children="""Distribution of various metrics according to the State.
                                 Get key information about every State after selection and their respective plants."""
                                 ),
                          ]
                            )
        ),

        html.Div(
            id="app-container",
            children=[
                html.Div(
                    # drop-down + map
                    id='left-column',
                    children=[
                        html.Div(
                            id='map-container',
                            children=[
                                html.Div(
                                    # drop-down selector for the map
                                    id='',
                                    children=[
                                        html.P(id="map-selector",
                                               children="Select:",
                                               style={
                                                   'color':SECONDARY_COLOR,
                                                   'font-size': 12,
                                                   'visibility':'hidden'
                                               })
                                        # ,dcc.Dropdown(
                                        #     options=[
                                        #         {
                                        #             "label": "Total revenue",
                                        #             "value": "total_revenue",
                                        #         },
                                        #         {
                                        #             "label": "Average revenue",
                                        #             "value": "average_revenue",
                                        #         },
                                        #         {
                                        #             "label": "Number of orders",
                                        #             "value": "number_of_orders",
                                        #         },
                                        #         {
                                        #             "label": "Count of Plants",
                                        #             "value": "count_of_plants",
                                        #         },
                                        #     ],
                                        #     value="total_revenue",
                                        #     id="map-dropdown",
                                        # )
                                    ]
                                )
                                    ]
                        ),
                        # html.Br(),
                        html.Div(
                            # map
                            id='',
                            children=[
                                dcc.Graph(figure=india_map)
                            ]
                            )

                    ]

                ),
                html.Div(
                    # right container - drop-down + info
                    id='graph-container',
                    children=[
                        # drop-down state selector
                        html.Div(
                            id='',
                            children=[
                                html.Div(
                                    # drop-down selector for the map
                                    id='',
                                    children=[
                                        html.P(id="chart-selector",
                                               children="Select state for more information about state:",
                                               style={
                                                    'color':SECONDARY_COLOR,
                                                    'font-size': 12
                                               }
                                               ),

                                        dcc.Dropdown(
                                            options=state_label_value,
                                            value=states_list[0],
                                            id="chart-dropdown",
                                        )
                                        ]
                                ),
                                html.Div(
                                    # state information*
                                    id='',
                                    children=[
                                        html.H3(
                                            id='title-chart-state',
                                            children='',
                                            style={'text-align': 'center'}
                                        ),
                                        html.P(
                                            id='plant-chart-state',
                                            children='',
                                            style={'text-align': 'center'}
                                        ),
                                        html.Hr(
                                            style={'border': '1px solid ' + HIGHLIGHT_COLOR}
                                        ),
                                        html.Br(),
                                        html.P(
                                            children='Revenue information for Plants & Cities in the State',
                                            style={'text-align': 'center',
                                                   'font-size': 14}
                                        ),
                                        html.Div(
                                            style={'padding': 2},
                                            children=[
                                                dash_table.DataTable(
                                                    id='plcttable-chart-state',
                                                    columns=[{"name": i, "id": i}
                                                             for i in plant_table_headers],
                                                    # data=,
                                                    editable=False,             # allow editing of data inside all cells
                                                    filter_action="none",     # allow filtering of data by user ('native') or not ('none')
                                                    sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                                                    sort_mode="single",         # sort across 'multi' or 'single' columns
                                                    column_selectable=False,    # allow users to select 'multi' or 'single' columns
                                                    row_selectable="single",     # allow users to select 'multi' or 'single' rows
                                                    row_deletable=False,        # choose if user can delete a row (True) or not (False)
                                                    selected_columns=[],        # ids of columns that user selects
                                                    selected_rows=[],           # indices of rows that user selects
                                                    page_action="native",       # all data is passed to the table up-front or not ('none')\
                                                    page_current=0,             # page number that user is on
                                                    page_size=5,

                                                    style_table={'color': 'white'},
                                                    style_header={
                                                        'font-weight': 'bold',
                                                        'backgroundColor': DARK_BLUE_HEADER_COLOR,
                                                        'color': 'white',
                                                        'textAlign': 'left',
                                                        'font-size': 12,
                                                        'border': '3px solid '+SECONDARY_COLOR, #7fafdf
                                                        'font-family': "'Open Sans', 'HelveticaNeue', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                                                                  },
                                                    style_cell={
                                                        'backgroundColor': BLUE_CONTAINER_COLOR,
                                                        'color': 'white',
                                                        'textAlign': 'left',
                                                        'font-size': 14,
                                                        'font-family': "'Open Sans', 'HelveticaNeue', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                                                    }
                                                    , style_data={ 'border': '1px solid #1C2230',
                                                                   # 'border-color': '#8D9CBD'
                                                                   }
                                                    , style_as_list_view=True

                                                    # ,
                                                    # style_filter = {
                                                    #     'backgroundColor': '#DCDCDC',
                                                    #     'color': 'white',
                                                    #     'textAlign': 'left',
                                                    #     'font-size': 14
                                                    # }
                                                    # ,style_filter_conditional = [{
                                                    #
                                                    #     'textAlign': 'left',
                                                    #     'font-size': 12
                                                    # }]
                                                )
                                            ]
                                        ),
                                        html.Br(), html.Br(), html.Br(),
                                        html.Div(
                                            children=[
                                                html.P(
                                                    children="""Select a Plant(above) to display the respective Time-plot""",
                                                    style={'text-align': 'center',
                                                           'color': SECONDARY_COLOR,
                                                           'font-size': 12}
                                                ), html.Br()
                                            ]
                                        ),# html.Br(),
                                        html.Div(
                                            style={
                                                'width': '50%',
                                                'float': 'left'
                                                # 'background-color': SECONDARY_COLOR
                                            },
                                            children=[
                                                # dcc.Slider(
                                                #     id="years-slider",
                                                #     min=min(YEARS),
                                                #     max=max(YEARS),
                                                #     value=min(YEARS),
                                                #     marks={
                                                #         str(year): {
                                                #             "label": str(year),
                                                #             # "value": str(year),
                                                #             "style": {"color": SECONDARY_COLOR}, #Sec
                                                #         }
                                                #         for year in YEARS
                                                #     },
                                                # )

                                                html.P(
                                                    children="Year:",
                                                    style={
                                                        'color': SECONDARY_COLOR,
                                                        'font-size': 12,
                                                        'margin-bottom': 5,
                                                        'margin-left': 40
                                                    }
                                                ),
                                                dcc.Dropdown(
                                                    options=year_options,
                                                    id="timeplot-year-dropdown",
                                                    value=year_options[0]['value'],
                                                    style=dropdown_style_hidden
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style={
                                                'width': '50%',
                                                'margin-left': '50%',

                                            },
                                            children=[
                                                html.P(
                                                    children="Mode:",
                                                    style={
                                                        'color':SECONDARY_COLOR,
                                                        'font-size': 12,
                                                        'margin-bottom': 5,
                                                        'margin-left': 40
                                                    }
                                                ),
                                                dcc.Dropdown(
                                                    options=timeplot_options,
                                                    id="timeplot-mode-dropdown",
                                                    value=timeplot_options[0]['value'],
                                                    style=dropdown_style_hidden
                                                )
                                            ]
                                        ),
                                        html.Br(),
                                        html.Div(
                                            # Timeplot
                                            id='figure-timeplot',
                                            style={
                                                'padding': '2px'
                                            },
                                            children=[]
                                        ),html.Br(),
                                        html.Hr(
                                            style={'border': '1px solid ' + HIGHLIGHT_COLOR}
                                        ),

                                        html.P(
                                            children='Make of the cars and their respective Models',
                                            style={'text-align': 'center',
                                                   'color':'white',
                                                   'font-size': 14}
                                        ),
                                        html.Div(
                                            children=[
                                                html.P(
                                                    id='checklist-model-title',
                                                    children='Check to show/hide Model:',
                                                    style={
                                                   'color':SECONDARY_COLOR,
                                                   'font-size': 12
                                               }
                                                ),
                                                dcc.Checklist(
                                                    id='checklist-model',
                                                    options=[{'label': 'Show Model', 'value': 'Show Model'}],
                                                    value=[]
                                                )
                                            ]
                                                # dashtable
                                        ),
                                        html.Div(
                                            id='mkmdtable-chart-state-container',
                                            children=[]
                                                # dashtable
                                        )
                                    ]
                                )
                            ]
                        )

                    ]
                )
                    ]
        )
    ]
)

# map-callback
# @app.callback(
#     [Output(component_id='', component_property='children')],
#     [Input(component_id='map-dropdown', component_property='value')]
# )
# def update_map(map_dropdown):
#     map_container = []
#     invoice.rename()
#     return map_container


# app-callback-primary-state
@app.callback(
    [Output(component_id='title-chart-state', component_property='children'),
     Output(component_id='plant-chart-state', component_property='children')],
    [Input(component_id='chart-dropdown', component_property='value')]
)
def update_all_graphs(state_selected):
    if state_selected not in states_list:
        return '', '', {}, None
    # state_callback = invoice[invoice.plant_state==st]
    # main title
    st_title = 'State - ' + str(state_selected)
    # plant counts (invoice)
    plant_count = 'Number of Plants in the state: ' + str(state_plants_count[state_selected])
    # Plant table

    return st_title, plant_count


# app-callback-plant_table-time_plot
@app.callback([ Output(component_id='figure-timeplot', component_property='children'),
                Output(component_id='plcttable-chart-state', component_property='data'),
                Output(component_id='timeplot-mode-dropdown', component_property='style'),
                Output(component_id='timeplot-year-dropdown', component_property='style')],
              [ Input(component_id='chart-dropdown', component_property='value'),
                Input(component_id='plcttable-chart-state', component_property='selected_rows'),
                Input(component_id='timeplot-mode-dropdown', component_property='value'),
                Input(component_id='timeplot-year-dropdown', component_property='value')]
              )
def update_timeplot_plant(state_selected, selected_rows, timeplot_mode, timeplot_year):
    # # timeplot
    # if time_plot_mode is timeplot_options[0]['value']:
    #     # Order-type
    #     temp = state_callback[state_callback.Plant == plant_selected].groupby(['Order Type'])
    #
    #     fig_timeplot
    # else:
    # # Total
    # initial
    timeplot_children = []
    pl = ''
    timeplot_dropdown_style = dropdown_style_hidden


    # dashtable
    state_plant_table = invoice[invoice.plant_state == state_selected].groupby(['Plant', 'plant_city']) \
        ['Total Value'].agg(['sum', 'mean', 'count']).reset_index()
    state_plant_table.columns = plant_table_headers
    state_plant_table['Total'] = state_plant_table['Total'].astype(int)
    state_plant_table['Average'] = state_plant_table['Average'].astype(int)
    state_plant_table_dict = state_plant_table.to_dict('records')

    if selected_rows != []:
        timeplot_dropdown_style = dropdown_style_visible
        pl = state_plant_table_dict[selected_rows[0]]['Plant']
        pl_city = state_plant_table_dict[selected_rows[0]]['City']

        plant_callback = invoice[invoice['Plant']==pl]\
            [['Plant', 'Invoice Date', 'invoice_month', 'invoice_year', 'Month & Year', 'Order Type', 'Total Value']]
        plant_callback.rename(columns={'Total Value': 'Revenue (INR)'}, inplace=True)
        plant_year_list = plant_callback.invoice_year.unique()

        if timeplot_year != 'All':
            if int(timeplot_year) not in plant_year_list:
                # print('not found')
                timeplot_children = [
                    html.H6(
                        children='No data found for the current selections.',
                        style={
                            'text-align': 'center',
                            'color': '#ff6666',
                            'margin': 20
                        }
                    )
                ]
                return timeplot_children, state_plant_table_dict, timeplot_dropdown_style, timeplot_dropdown_style
            else:
                plant_callback = plant_callback[plant_callback['invoice_year'] == int(timeplot_year)]

        if timeplot_mode==timeplot_options[0]['value']:
            # plot = plant_callback.groupby(['Invoice Date', 'Order Type'])\
            plot = plant_callback.groupby(['invoice_year', 'invoice_month', 'Month & Year', 'Order Type'])\
                ['Revenue (INR)'].sum().reset_index().sort_values(['invoice_year', 'invoice_month'])
                # .sort_values(['Invoice Date'])
            timeplot_fig = px.line(plot, x="Month & Year", y="Revenue (INR)", color="Order Type",
                                   line_group="Order Type", hover_name = "Month & Year")
        else:
            plot =\
                plant_callback.groupby(['invoice_year', 'invoice_month', 'Month & Year'])\
                ['Revenue (INR)'].sum().reset_index() \
                .sort_values(['invoice_year', 'invoice_month'])
            timeplot_fig = px.line(plot, x='Month & Year', y='Revenue (INR)',
                                   hover_name="Month & Year")
            # print(plot.head())

        timeplot_fig.update_layout(
            title=dict(
                        text=timeplot_title(pl, pl_city, timeplot_year),
                        xanchor='center',
                        x=0.45,
                        yref='paper',
                        yanchor='bottom',
                        y=1,
                        # pad={'b': 10},
                        # font= "Playfair Display"
                    ),
            margin=dict(t=50,l=0,b=0,r=0),
            width=800,
            height=500,
            legend={

                'x': 1.,
                'y': .95
            }
        )
        timeplot_fig.layout.template = 'plotly_dark'

        timeplot_children = [
            dcc.Graph(
                id='graph-timeplot',
                figure=timeplot_fig
            )
        ]
    # timeplot_fig = str(selected_rows) + pl
    return timeplot_children, state_plant_table_dict, timeplot_dropdown_style, timeplot_dropdown_style


# app-callback-model_make_table-time_plot
@app.callback([Output(component_id='mkmdtable-chart-state-container',component_property='children'),
               Output(component_id='checklist-model-title',component_property='children')],
              [Input(component_id='chart-dropdown',component_property='value'),
               Input(component_id='checklist-model', component_property='value')])
def update_text(st, checklist_model):
    # columns=[]
    # table_data_dict={}
    # datatable_container=[]
    state_cap = invoice[invoice.plant_state == st][['Model', 'Make', 'Total Value']]

    if checklist_model==[]:
        table_data = state_cap.groupby(['Make'])['Total Value'].agg(['sum', 'mean', 'count'])\
            .reset_index().sort_values(by='sum',ascending=False)
        checklist_title = 'Check to show Model:'
    else:
        table_data = state_cap.groupby(['Make', 'Model'])['Total Value'].agg(['sum', 'mean', 'count'])\
            .reset_index().sort_values(by='sum',ascending=False)
        checklist_title = 'Uncheck to hide Model:'
    table_data['sum'] = table_data['sum'].astype(int)
    table_data['mean'] = table_data['mean'].astype(int)

    table_data.rename({
        'sum': 'Total', 'mean': 'Average', 'count': 'No of Transactions'
    }, inplace=True)

    # columns=table_data.columns
    # table_data_dict = table_data.to_dict('records')

    datatable_container = [
        dash_table.DataTable(
            columns=[{"name": i, "id": i}
                     for i in table_data.columns],
            data=table_data.to_dict('records'),

            editable=False,  # allow editing of data inside all cells
            filter_action="none",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            column_selectable=False,  # allow users to select 'multi' or 'single' columns
            row_selectable=False,  # allow users to select 'multi' or 'single' rows
            row_deletable=False,  # choose if user can delete a row (True) or not (False)
            selected_columns=[],  # ids of columns that user selects
            selected_rows=[],  # indices of rows that user selects
            page_action="native",  # all data is passed to the table up-front or not ('none')\
            page_current=0,  # page number that user is on
            page_size=5,

            style_table={'color': 'white'},
            style_header={
                'font-weight': 'bold',
                'backgroundColor': DARK_BLUE_HEADER_COLOR,
                'color': 'white',
                'textAlign': 'left',
                'font-size': 12,
                'border': '3px solid ' + SECONDARY_COLOR,  # 7fafdf
                'font-family': "'Open Sans', 'HelveticaNeue', 'Helvetica Neue', Helvetica, Arial, sans-serif"
            },
            style_cell={
                'backgroundColor': BLUE_CONTAINER_COLOR,
                'color': 'white',
                'textAlign': 'left',
                'font-size': 14,
                'font-family': "'Open Sans', 'HelveticaNeue', 'Helvetica Neue', Helvetica, Arial, sans-serif"
            },
            style_data={'border': '1px solid #1C2230',
                          # 'border-color': '#8D9CBD'
                          },
            style_as_list_view=True

        )
    ]
    return datatable_container, checklist_title


if __name__ == '__main__':
    app.run_server(debug=True)