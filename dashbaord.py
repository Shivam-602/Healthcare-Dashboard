#import
import dash
import dash_bootstrap_components as dbc
from dash import dcc,Input,Output, html
import plotly.express as px
import pandas as pd


#loading data
def load_data():
    df= pd.read_csv('healthcare.csv')
    df["Billing Amount"]=pd.to_numeric(df['Billing Amount'],errors='coerce')
    df['Date of Admission']=pd.to_datetime(df['Date of Admission'])
    df["YearMonth"]=df['Date of Admission'].dt.to_period("M")
    return df

data=load_data()

num_rec=len(data)
avg_billing=data["Billing Amount"].mean()


#creating a web app
app=dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#app layout and design
app.layout=dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=12, className="text-center my-5")
    ]),

    #Hospital statistics
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_rec}",className="text-center my-3 top-text"),width=6),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing:,.2f}",className="text-center my-3 top-text"),width=6)      
    ],class_name="mb-5"),

    #male or female demographics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("patient Demographics",className="card-title"),
                    dcc.Dropdown(
                        id="gender-filter",
                        options=[{"label":gender, "value":gender} for gender in data["Gender"].unique()],
                        value=None,
                        placeholder='select a Gender'
                    ),
                    dcc.Graph(id="age-distrubition")
                ])
            ])
        ],width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("medical Condition Distribution ",className="card-title"),
                    dcc.Graph(id="condition-distrubition")
                ])
            ])
        ],width=6)
    ]),

    #Insurance Provider data
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("insurance provider comparisoin ",className="card-title"),
                    dcc.Graph(id="Insurance-comparision")
                ])
            ])
        ],width=12)
    ]),

    #billind distribution
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Billing amount distribution ",className="card-title"),
                    dcc.Slider(
                        id="billing-slider",
                        min=data["Billing Amount"].min(),
                        max=data["Billing Amount"].max(),
                        value=data["Billing Amount"].median(),
                        marks={int(value): f"${int(value):,}" for value in data["Billing Amount"].quantile([0,0.25,0.5,0.75,1]).values},
                        step=100
                    ),
                    dcc.Graph(id="Billing-distibution")
                ])
            ])
        ],width=12)
    ]),

    #Trends in Admission
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trends in Admission ",className="card-title"),
                    dcc.RadioItems(
                        id='chart-type',
                        options=[{"label":"Line Chart", 'value':'line'},{"label":"Bar Chart", 'value':'bar'}],
                        value="line",
                        inline=True,
                        className="mb-4"
                    ),
                    dcc.Dropdown(
                        id='condition-filter',
                        options=[{"label":condition,"value":condition} for condition in data["Medical Condition"].unique()],
                        value=None,
                        placeholder="Select a Medical Condition"
                    ),
                    dcc.Graph(
                        id="admission-trends"
                    )
                ])
            ])
        ],width=12)
    ]),
],fluid=True)

#create  our callbacks
@app.callback(
    Output('age-distrubition','figure'),
    Input('gender-filter','value')
)

def update_distribution(selected_gender):
    if selected_gender:
        filtered_df=data[data["Gender"]==selected_gender]
    else:
        filtered_df=data

    if filtered_df.empty:
        return{}
    
    fig=px.histogram(
        filtered_df,
        x="Age",
        nbins=10,
        color="Gender",
        title="Age Distribution by Gender",
        color_discrete_sequence=["#050F57","#DE3813"]
    )

    return fig

#medical condition distribution
@app.callback(
    Output('condition-distrubition','figure'),
    Input('gender-filter','value')
)

def update_medical_condition(selected_gender):
    filtered_df=data[data["Gender"]==selected_gender] if selected_gender else data
    fig=px.pie(filtered_df,names="Medical Condition", title="Medical Condition Distribution")
    return fig

#insurance provider comparision
@app.callback(
    Output('Insurance-comparision','figure'),
    Input('gender-filter','value')
)

def update_insurance(selected_gender):
    filtered_df=data[data["Gender"]==selected_gender] if selected_gender else data
    fig=px.bar(
        filtered_df,x="Insurance Provider", y="Billing Amount", color="Medical Condition",
        barmode="group",
        title="Insurance Provider Price Comparision",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    return fig

#Billing distribution
@app.callback(
    Output('Billing-distibution','figure'),
    [Input('gender-filter','value'),
    Input('billing-slider','value')]
)

def update_billing(selected_gender,slider_value):
    filtered_df=data[data["Gender"]==selected_gender] if selected_gender else data
    filtered_df=filtered_df[filtered_df["Billing Amount"]<=slider_value]

    fig=px.histogram(filtered_df, x="Billing Amount", nbins=10, title="Billing Amount Distribution")
    return fig

#Trends in admission
@app.callback(
    Output('admission-trends','figure'),
    [Input('chart-type','value'),
     Input('condition-filter','value')]
)

def update_trends(chart_type,selected_condition):
    filtered_df=data[data["Medical Condition"]==selected_condition] if selected_condition else data
    
    trend_df=filtered_df.groupby("YearMonth").size().reset_index(name='Count')
    trend_df["YearMonth"]=trend_df["YearMonth"].astype(str)

    if chart_type=="line":
        fig=px.line(trend_df,x="YearMonth",y="Count",title="Admission Trends over time")
    else:
        fig=px.bar(trend_df,x="YearMonth",y="Count",title="Admission Trends over time")

    return fig






if __name__=="__main__":
    app.run(debug=True)