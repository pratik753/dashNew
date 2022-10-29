# from tkinter.ttk import Style
import os
import pandas as pd
# import numpy as np
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc
# import dash_core_components as dcc
from dash import html
# import dash_html_components as html
# from plotly.subplots import make_subplots
# import matplotlib.pyplot as plt
from jupyter_dash import JupyterDash  # pip install dash
# import dash_cytoscape as cyto
from dash.dependencies import Output, Input


# external JavaScript files
external_scripts = [
    # 'https://www.google-analytics.com/analytics.js',
    # {'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js'},
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor',
        'crossorigin': 'anonymous'
    },
    'https://www.w3schools.com/w3css/4/w3.css'
]

dir=os.path.dirname(os.path.realpath(__file__))
# print(dir)

df = pd.read_excel(os.path.join(dir,'Book2.xlsx'))

df.drop(df[df['Transaction Type'] == 'Deposit'].index, inplace=True)
df.reset_index(drop=True, inplace=True)
df_trade = pd.read_excel(os.path.join(dir,'Item_file_1.xlsx'))
df_item = pd.read_csv(os.path.join(dir,'Trade_File_1.csv'))
df_item.columns = ['Product/Service', 'Category']
df['day'] = pd.to_datetime(df['Date'], format="%d-%m-%Y").dt.day  # inegrate
df['Date_month'] = pd.to_datetime(df['Date'], format="%d-%m-%Y").dt.month
df['Date_year'] = pd.to_datetime(df['Date'], format="%d-%m-%Y").dt.year
df['Date_Month1'] = pd.to_datetime(df['Date'], format="%d-%m-%Y").dt.month
day = []  # inegrate
for i in range(len(df)):  # inegrate
    x1 = str(df['Date_year'][i])+'-'+str(df['Date_month'][i]) + \
        '-'+str(df['day'][i])  # inegrate
    day.append(x1)  # inegrate
df['day'] = day  # inegrate
df['Date_Month1'].replace({1: 'Jan', 2: 'Feb', 3: 'March', 4: 'Apr', 5: 'May', 6: 'June',
                          7: 'July', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}, inplace=True)  # inegrate
# df.drop(['Qty', 'Sales Price'], axis=1, inplace=True)  # inegrate
df_new = df.copy()  # inegrate


def changeP(x):
    if x >= 10e+6:
        x = round(x/10e+6, 3)
        x = str(x)+' Cr.'
    elif x < 10e+6 and x >= 10e+4:
        x = round(x/10e+4, 3)
        x = str(x)+' Lakhs.'
    elif x < 10e+4 and x >= 10e+2:
        x = round(x/10e+2, 3)
        x = str(x)+' K.'
    else:
        x = str(x)
    return x


def merge_file(original, merge1, on1):
    data1 = original.copy()
    data2 = merge1.copy()
    lst_cust = data1[on1].unique()
    customer = []
    for i in lst_cust:
        if i not in list(data2[on1].unique()):
            customer.append(i)
    col = list(merge1.columns)
    Trade = ['New_'+col[-1]+'_Head']*len(customer)
    df1 = pd.DataFrame()
    df1[on1] = customer
    df1[col[-1]] = Trade
    data2 = pd.concat([data2, df1], axis=0)
    data1 = pd.merge(data1, data2, on=on1)
    data1['Date'] = pd.to_datetime(data1['Date'], format="%d-%m-%Y")
    data1.sort_values('Date', ascending=True, inplace=True)
    data1.reset_index(inplace=True, drop=True)
    return data1


def custom_customer_trader_head(data_1, axis, initial, final, no_cust='10', data_2=df_trade):
    no_cust = str(no_cust)
    data1 = data_1.copy()
    data2 = data_2.copy()
    col1 = list(data2.columns)
    data1 = merge_file(data1, data2, col1[0])
    mon_yr = []
    for i in range(len(data1)):
        x1 = data1['Date_Month1'][i]+'-'+str(data1['Date_year'][i])
        mon_yr.append(x1)
    data1['Month_year'] = mon_yr
    ini = list(data1[data1['day'] == initial].index)[0]
    fin = list(data1[data1['day'] == final].index)[-1]
    output = data1.loc[ini:fin]
    sum_c = []
    sum_c_p = []
    sum_c_2 = []
    con = pd.DataFrame()
    for k in list(output[axis].unique()):
        x = round(output[output[axis] == k]['Amount'].sum(), 2)
        sum_c.append(x)
        sum_c_p.append(round(x*100/output['Amount'].sum(), 2))
        sum_c_2.append(changeP(x))
    con[axis] = list(output[axis].unique())
    con['Amount'] = sum_c
    con['Amount (Rs.)'] = sum_c_2
    con['Sale_Amount (%)'] = sum_c_p
    con.sort_values('Amount', ascending=False, inplace=True)
    con.reset_index(drop=True, inplace=True)
    if (no_cust).upper() == 'ALL' or int(no_cust) > len(con):
        con = con
    else:
        con = con.loc[0:int(no_cust)-1]
    output2 = pd.DataFrame()
    for j in list(output['Month_year'].unique()):
        sum_1 = []
        sum_2 = []
        sum_3 = []
        test = output[output['Month_year'] == j]
        for i in list(test[axis].unique()):
            x = round(test[test[axis] == i]['Amount'].sum(), 2)
            sum_1.append(x)
            sum_2.append(round(x*100/test['Amount'].sum(), 2))
            sum_3.append(changeP(x))
        output1 = pd.DataFrame()
        output1[axis] = list(test[axis].unique())
        output1['Amount'] = sum_1
        output1['Amount (Rs.)'] = sum_3
        output1['Sale_Amount (%)'] = sum_2
        output1['Month'] = [j]*len(sum_1)
        if (no_cust).upper() == 'ALL' or len(sum_1) < int(no_cust):
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output2 = pd.concat([output2, output1], axis=0)
        else:
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output1 = output1.loc[0:int(no_cust)-1]
            output2 = pd.concat([output2, output1], axis=0)
    return (output2, con)


def month_customer_trader_head(data_1, axis, initial, no_cust=2, data_2=df_trade):
    no_cust = str(no_cust)
    data1 = data_1.copy()
    data2 = data_2.copy()
    coln = list(data2.columns)
    data1 = merge_file(data1, data2, coln[0])
    mon_yr = []
    for i in range(len(data1)):
        x1 = str(data1['Date_Month1'][i])+'-'+str(data1['Date_year'][i])
        mon_yr.append(x1)
    data1['Month_year'] = mon_yr
    new = data1[data1['Month_year'] == initial]
    sum_c = []
    sum_c_p = []
    sum_c_2 = []
    con = pd.DataFrame()
    for k in list(output[axis].unique()):
        x = round(output[output[axis] == k]['Amount'].sum(), 2)
        sum_c.append(x)
        sum_c_p.append(round(x*100/output['Amount'].sum(), 2))
        sum_c_2.append(changeP(x))
    con[axis] = list(output[axis].unique())
    con['Amount'] = sum_c
    con['Amount (Rs.)'] = sum_c_2
    con['Sale_Amount (%)'] = sum_c_p
    con.sort_values('Amount', ascending=False, inplace=True)
    con.reset_index(drop=True, inplace=True)
    if (no_cust).upper() == 'ALL' or int(no_cust) > len(con):
        con = con
    else:
        con = con.loc[0:int(no_cust)-1]
    lst1 = list(new[axis].unique())
    amount_sum = []
    amount_sum_per = []
    for i in lst1:
        x = round(new[new[axis] == i]['Amount'].sum(), 2)
        amount_sum.append(x)
        amount_sum_per.append(round(x*100/new['Amount'].sum(), 2))
    output = pd.DataFrame()
    output[axis] = lst1
    output['Amount'] = amount_sum
    output['Sale_Amount (%)'] = amount_sum_per
    output.sort_values('Amount', ascending=False, inplace=True)
    output.reset_index(drop=True, inplace=True)
    output['Month'] = [initial]*len(lst1)
    if (no_cust).upper() == 'ALL' or len(lst1) < int(no_cust):
        output.sort_values('Amount', ascending=False, inplace=True)
        output.reset_index(drop=True, inplace=True)
        output2 = output
    else:
        output.sort_values('Amount', ascending=False, inplace=True)
        output.reset_index(drop=True, inplace=True)
        output = output.loc[0:int(no_cust)-1]
        output2 = output
    return output2, con


def Quarter_customer_trader_head(data_1, axis, Qtr, year, no_cust=2, data_2=df_trade):
    no_cust = str(no_cust)
    year = int(year)
    data1 = data_1.copy()
    data2 = data_2.copy()
    coln = list(data2.columns)
    data1 = merge_file(data1, data2, coln[0])
    mon_yr = []
    for i in range(len(data1)):
        x = str(data1['Date_Month1'][i])+'-'+str(data1['Date_year'][i])
        mon_yr.append(x)
    data1['Month_year'] = mon_yr
    Qtd = {'Date_month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
           'Quarter': ['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4']}
    Qtd_df = pd.DataFrame(Qtd)
    output = pd.merge(data1, Qtd_df, on='Date_month')
    output2 = pd.DataFrame()
    test1 = output[(output['Quarter'] == Qtr) & (output['Date_year'] == year)]
    sum_c = []
    sum_c_p = []
    sum_c_2 = []
    con = pd.DataFrame()
    for k in list(output[axis].unique()):
        x = round(output[output[axis] == k]['Amount'].sum(), 2)
        sum_c.append(x)
        sum_c_p.append(round(x*100/output['Amount'].sum(), 2))
        sum_c_2.append(changeP(x))
    con[axis] = list(output[axis].unique())
    con['Amount'] = sum_c
    con['Amount (Rs.)'] = sum_c_2
    con['Sale_Amount (%)'] = sum_c_p
    con.sort_values('Amount', ascending=False, inplace=True)
    con.reset_index(drop=True, inplace=True)
    if (no_cust).upper() == 'ALL' or int(no_cust) > len(con):
        con = con
    else:
        con = con.loc[0:int(no_cust)-1]
    for j in list(test1['Month_year'].unique()):
        sum_1 = []
        sum_2 = []
        sum_3 = []
        test = output[output['Month_year'] == j]
        for k in list(test[axis].unique()):
            x = round(test[test[axis] == k]['Amount'].sum(), 2)
            sum_1.append(x)
            sum_2.append(round(x*100/test['Amount'].sum(), 2))
            sum_3.append(changeP(x))
        output1 = pd.DataFrame()
        output1[axis] = list(test[axis].unique())
        output1['Amount'] = sum_1
        output1['Amount (Rs.)'] = sum_3
        output1['Sale_Amount (%)'] = sum_2
        output1['Month'] = [j]*len(sum_1)
        if (no_cust).upper() == 'ALL' or len(sum_1) < int(no_cust):
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output2 = pd.concat([output2, output1], axis=0)
        else:
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output1 = output1.loc[0:int(no_cust)-1]
            output2 = pd.concat([output2, output1], axis=0)
    return (output2, con)


def past_VI_XII_month(data_1, axis, step=6, no_cust=2, data_2=df_trade):
    no_cust = str(no_cust)
    data1 = data_1.copy()
    data2 = data_2.copy()
    coln = list(data2.columns)
    data1 = merge_file(data1, data2, coln[0])
    mon_yr = []
    for i in range(len(data1)):
        x = str(data1['Date_month'][i])+'-'+str(data1['Date_year'][i])
        mon_yr.append(x)
    data1['Month_year'] = mon_yr
    month1 = dt.datetime.now().month
    year1 = dt.datetime.now().year
    if (str(month1)+'-'+str(year1)) not in (data1['Month_year'].unique()):
        month1 = data1['Date_month'][len(data1)-1]
        year1 = data1['Date_year'][len(data1)-1]
    month2 = month1 - step + 1
    year2 = dt.datetime.now().year
    if month2 <= 0:
        month2 = 12+month2
        year2 = year1-1
    if ((str(month2)+'-'+str(year2)) not in list(data1['Month_year'].unique())):
        month2 = data1['Date_month'][0]
        year2 = data1['Date_year'][0]
    fin1 = (str(month1)+'-'+str(year1))
    ini1 = (str(month2)+'-'+str(year2))
    mon_yr1 = []
    for i in range(len(data1)):
        x1 = data1['Date_Month1'][i]+'-'+str(data1['Date_year'][i])
        mon_yr1.append(x1)
    data1['Month_year1'] = mon_yr1
    ini = list(data1[data1['Month_year'] == ini1].index)[0]
    fin = list(data1[data1['Month_year'] == fin1].index)[-1]
    data1.drop(['Month_year'], axis=1, inplace=True)
    output = data1.loc[ini:fin]
    sum_c = []
    sum_c_p = []
    sum_c_2 = []
    con = pd.DataFrame()
    for k in list(output[axis].unique()):
        x = round(output[output[axis] == k]['Amount'].sum(), 2)
        sum_c.append(x)
        sum_c_p.append(round(x*100/output['Amount'].sum(), 2))
        sum_c_2.append(changeP(x))
    con[axis] = list(output[axis].unique())
    con['Amount'] = sum_c
    con['Amount (Rs.)'] = sum_c_2
    con['Sale_Amount (%)'] = sum_c_p
    con.sort_values('Amount', ascending=False, inplace=True)
    con.reset_index(drop=True, inplace=True)
    if (no_cust).upper() == 'ALL' or int(no_cust) > len(con):
        con = con
    else:
        con = con.loc[0:int(no_cust)-1]
    output2 = pd.DataFrame()
    for j in list(output['Month_year1'].unique()):
        sum_1 = []
        sum_2 = []
        sum_3 = []
        test = output[output['Month_year1'] == j]
        for i in list(test[axis].unique()):
            x = round(test[test[axis] == i]['Amount'].sum(), 2)
            sum_1.append(x)
            sum_2.append(round(x*100/test['Amount'].sum(), 2))
            sum_3.append(changeP(x))
        output1 = pd.DataFrame()
        output1[axis] = list(test[axis].unique())
        output1['Amount'] = sum_1
        output1['Amount (Rs.)'] = sum_3
        output1['Sale_Amount (%)'] = sum_2
        output1['Month'] = [j]*len(sum_1)
        if (no_cust).upper() == 'ALL' or len(sum_1) < int(no_cust):
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output2 = pd.concat([output2, output1], axis=0)
        else:
            output1.sort_values('Amount', ascending=False, inplace=True)
            output1.reset_index(drop=True, inplace=True)
            output1 = output1.loc[0:int(no_cust)-1]
            output2 = pd.concat([output2, output1], axis=0)
    return (output2, con)


app = JupyterDash(__name__,
                  external_scripts=external_scripts,
                  external_stylesheets=external_stylesheets)
# if __name__ == '__main__':
#     app.run_server(mode="external")

# app = JupyterDash(__name__,
#                   external_scripts=external_scripts,
#                   external_stylesheets=external_stylesheets)
fig_plot = html.Div(id='fig_plot')
fig_dropdown1 = dcc.Dropdown(
    id='fig_dropdown1',
    value=None,
    placeholder='Item Set',
    clearable=False,
    options=[
        {'label': name, 'value': name}
        for name in ['Customer', 'Trade', 'Category']
    ]
)

fig_dropdown = dcc.Dropdown(
    id='fig_dropdown',
    value=None,
    placeholder='Filter',
    clearable=False,
    options=[
        {'label': name, 'value': name}
        for name in ['MTD', 'Custom', 'Quarter', 'Past 6 Month', 'Past 12 month']
    ])
table_graph = dcc.Dropdown(
    id='table_graph',
    value='Relative',
    placeholder='Table/Graph',
    clearable=False,
    options=[
        {'label': name, 'value': name}
        for name in ['Relative', 'Absolute']
    ], style={'width': '50%'})
date_mtd1 = dcc.DatePickerSingle(
    id='date1',
    min_date_allowed=dt.date(1995, 8, 5),
    max_date_allowed=dt.datetime.now().date(),
    initial_visible_month=dt.datetime.now().date(),
    date=dt.datetime.now().date(),
    display_format='DD/MM/YYYY',
    style={'padding': '3px 6px'})
date_mtd2 = dcc.DatePickerSingle(
    id='date2',
    min_date_allowed=dt.date(1995, 8, 5),
    max_date_allowed=dt.datetime.now().date(),
    initial_visible_month=dt.datetime.now().date(),
    date=dt.datetime.now().date(),
    display_format='DD/MM/YYYY',
    style={'padding': '3px 6px'})
date_mtd3 = dcc.DatePickerSingle(
    id='date3',
    min_date_allowed=dt.date(1995, 8, 5),
    max_date_allowed=dt.datetime.now().date(),
    initial_visible_month=dt.datetime.now().date(),
    date=dt.datetime.now().date(),
    display_format='DD/MM/YYYY',
    style={'padding': '3px 6px'})
Input1 = dcc.Input(id='input1', type='text', placeholder='1-all',
                   style={'widht': '40%', 'height': '65%', 'padding': '10px 10px', 'margin': '5px'})
Input2 = dcc.Input(id='input', type='text', placeholder='Q(1-4)-YYYY',
                   className="quainput")
heading = str('Stacker Plot')

sideBar = html.Div([
    html.Ul([
        html.Div([

            html.Div([fig_dropdown1], className="sideBarDrop"),
            html.Div([fig_dropdown], className="sideBarDrop"),
            html.Div([html.H5(children='Date for MTD'), date_mtd1],
                     className="sideBarDrop"),
            html.Div([html.H5(children='Initial Date for Custom'), date_mtd2],
                     className="sideBarDrop"),
            html.Div([html.H5(children='Final date for Custom'), date_mtd3],
                     className="sideBarDrop"),
            html.Div([html.H5(children='Quarter'), Input2],
                     className="sideBarDrop"),


        ], className='sideBarList')
        # fig_dropdown1,
    ], className="w3-ul myli"),
], className="sideBar")

navBar = html.Div(
    [html.Span(["Analytics Panal"], className="navText")], className="navBar")

# fig_dropdown1
app.layout = html.Div([
    navBar,
    sideBar,

    html.Div([
        # html.Div([
        # html.Div(
        # [
        # html.Div([
        #     html.Span(
        #         [fig_dropdown], className="categoriesFont")],
        #     className="col", style={'margin': 'auto'},),
        # html.Div([html.Span(children='No. of Performer:'), Input1],

        #          className="cold")
        # ],

        #     className="row row-cols-1 row-cols-sm-2 row-cols-md-4")],
        # className="container filterDiv"),
        # html.Div([
        # html.Div(
        # [
        # html.Div([
        # html.Span(
        # [html.Div([html.H5(children='Date for MTD'), date_mtd1], style={'display': 'flex'})], className="categoriesFont")],
        # className="col"),
        # html.Div([
        #     html.Span(
        #         [html.Div([html.H5(children='Initial Date for Custom'), date_mtd2], style={'display': 'flex'})], className="categoriesFont")],
        #     className="col"),
        # html.Div([
        #     html.Span(
        #         [html.Div([
        #             html.H5(children='Final date for Custom'), date_mtd3], style={'display': 'flex'})], className="categoriesFont")],
        #     className="col"),
        # html.Div([
        #     html.Span(
        #         [html.Div([html.H5(children='Quarter'), Input2], style={'display': 'flex'})], className="categoriesFont")],
        #     className="col"),

        # ],

        # className="row row-cols-1 row-cols-sm-2 row-cols-md-4")],
        # className="container filterDiv"),


        html.Div([
            # html.Div([html.H3(children='Initial Date for Custom'), "date_mtd2"],
            #          style={'display': 'flex', 'padding': '5px 20px'}),
            # html.Div([html.H3(children='Final date for Custom'),
            #           date_mtd3], style={'display': 'flex', 'padding': '5px 20px'}),
            # html.Div([html.H3(children='Quarter'), Input2],
            #  style={'display': 'flex', 'padding': '5px 20px'})

        ],
            style={'width': '30%', 'display': 'flex'}
        ),

        # html.Div([html.Div([html.H3(children='No. of Performer:'), Input1],style={'display': 'flex', 'padding': '5px 20px'})]),
        html.H2(children="Consolidated Table followed by Graph", className="graphTitle"), html.Div([table_graph], className="table_graph"), fig_plot], className="container mainCont divContCenter")
])


@ app.callback(Output('fig_plot', 'children'),
               Input('fig_dropdown', 'value'),
               Input('aTrade', 'value'),
               Input('fig_dropdown', 'value'),
               Input('aCategory', 'value'),
               Input('aHead', 'value'),
               #   Input('aTrade', 'value'),
               Input('date1', 'date'),
               Input('date2', 'date'),
               Input('date3', 'date'),
               Input('input', 'value'),
               Input('table_graph', 'value'),
               #   Input('input1', 'value')
               )
def update_output(fig_name, aTrade, aCategory, aHead, date1, date2, date3, input2, input3):
    return name_to_figure(fig_name, aTrade, aCategory, aHead, date1, date2, date3, input2, input3)


def name_to_figure(fig_name, aTrade, aCategory, aHead, date1, date2, date3, input2, input3):
    mon = {1: 'Jan', 2: 'Feb', 3: 'March', 4: 'Apr', 5: 'May', 6: 'June',
           7: 'July', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    figure = go.Figure()
    figure1 = go.Figure()
    figure2 = go.Figure()
    figure3 = go.Figure()
    merg = df_trade
    if aTrade == 'Trade':
        inpt = 'Trade'
    elif aCategory == 'Category':
        inpt = 'Category'
        merg = df_trade
    elif aHead == 'Head':
        inpt = 'Customer'
        merg = df_item
    if fig_name == 'MTD':
        d1 = dt.date.fromisoformat(date1)
        s1 = mon[d1.month]+'-'+str(d1.year)
        x1, c1 = month_customer_trader_head(df_new, inpt, s1, 10, merg)
        total = changeP(c1['Amount'].sum())
        figure = go.Figure(data=[go.Table(header=dict(values=list(c1.columns)),
                                          cells=dict(values=[c1[k].tolist() for k in c1.columns]))])
        figure.update_layout(title='( '+str(d1.month)+'-'+str(d1.year)+' ) ' +
                             'Total Amount (Rs.) ' + total, paper_bgcolor="skyblue")
        figure1 = px.bar(x1, x='Month', y="Amount", color=inpt, text_auto=True,
                         width=900, height=700, hover_data=['Sale_Amount (%)'])
        figure1.update_layout(title='Month')
        figure2 = px.bar(c1, x=inpt, y='Sale_Amount (%)')
        figure2.update_layout(yaxis={'categoryorder': 'total descending'})
        figure2.update_traces(marker_color='skyblue')
        figure3 = go.Figure(data=[go.Table(header=dict(values=list(x1.columns)),
                                           cells=dict(values=[x1[k].tolist() for k in x1.columns]))])
    elif fig_name == 'Custom':
        d1 = dt.date.fromisoformat(date2)
        d2 = dt.date.fromisoformat(date3)
        s1 = str(d1.year)+'-'+str(d1.month)+'-'+str(d1.day)  # inegrate
        s2 = str(d2.year)+'-'+str(d2.month)+'-'+str(d2.day)  # inegrate
        x1, c1 = custom_customer_trader_head(df_new, inpt, s1, s2, 10, merg)
        total = changeP(c1['Amount'].sum())
        figure = go.Figure(data=[go.Table(header=dict(values=list(c1.columns)),
                                          cells=dict(values=[c1[k].tolist() for k in c1.columns]))])
        figure.update_layout(title='( '+s1+' )'+' to ' +
                             '( '+s2+' ) '+'Total Amount (Rs.)'+total)
        figure1 = px.bar(x1, x='Month', y="Amount", color=inpt, text_auto=True,
                         width=900, height=700, hover_data=['Sale_Amount (%)'])
        figure1.update_layout(title='Custom')
        figure2 = px.bar(c1, x=inpt, y='Sale_Amount (%)')
        figure2.update_layout(yaxis={'categoryorder': 'total descending'})
        figure2.update_traces(marker_color='skyblue')
        figure3 = go.Figure(data=[go.Table(header=dict(values=list(x1.columns)),
                                           cells=dict(values=[x1[k].tolist() for k in x1.columns]))])
    elif fig_name == 'Quarter':
        i1 = input2.split('-')
        x1, c1 = Quarter_customer_trader_head(
            df_new, inpt, i1[0], i1[-1], 10, merg)
        total = changeP(c1['Amount'].sum())
        figure = go.Figure(data=[go.Table(header=dict(values=list(c1.columns)),
                                          cells=dict(values=[c1[k].tolist() for k in c1.columns]))])
        figure.update_layout(title=str(input2) + ' Total Amount (Rs.) '+total)
        figure1 = px.bar(x1, x='Month', y="Amount", color=inpt, text_auto=True,
                         width=900, height=700, hover_data=['Sale_Amount (%)'])
        figure1.update_layout(barmode='stack', title='Quarter', height=500)
        figure2 = px.bar(c1, x=inpt, y='Sale_Amount (%)')
        figure2.update_layout(yaxis={'categoryorder': 'total descending'})
        figure2.update_traces(marker_color='skyblue')
        figure3 = go.Figure(data=[go.Table(header=dict(values=list(x1.columns)),
                                           cells=dict(values=[x1[k].tolist() for k in x1.columns]))])
    elif fig_name == 'Past 6 Month':
        x1, c1 = past_VI_XII_month(df_new, inpt, 6, 10, merg)
        total = round(c1['Amount'].sum(), 2)
        total = changeP(c1['Amount'].sum())
        figure = go.Figure(data=[go.Table(header=dict(values=list(c1.columns)),
                                          cells=dict(values=[c1[k].tolist() for k in c1.columns]))])
        figure.update_layout(title='Past 6 Month '+'Total Amount (Rs.) '+total)
        figure1 = px.bar(x1, x='Month', y="Amount", color=inpt, text_auto=True,
                         width=900, height=700, hover_data=['Sale_Amount (%)'])
        figure1.update_layout(title='Past 6 Month')
        figure2 = px.bar(c1, x=inpt, y='Sale_Amount (%)')
        figure2.update_layout(yaxis={'categoryorder': 'total descending'})
        figure2.update_traces(marker_color='skyblue')
        figure3 = go.Figure(data=[go.Table(header=dict(values=list(x1.columns)),
                                           cells=dict(values=[x1[k].tolist() for k in x1.columns]))])
    elif fig_name == 'Past 12 month':
        x1, c1 = past_VI_XII_month(df_new, inpt, 12, 10, merg)
        total = round(c1['Amount'].sum(), 2)
        total = changeP(c1['Amount'].sum())
        figure = go.Figure(data=[go.Table(header=dict(values=list(c1.columns)),
                                          cells=dict(values=[c1[k].tolist() for k in c1.columns]))])
        figure.update_layout(title='Past 12 month ' +
                             'Total Amount (Rs.) '+total)
        figure1 = px.bar(x1, x='Month', y="Amount", color=inpt, text_auto=True,
                         width=900, height=700, hover_data=['Sale_Amount (%)'])
        figure1.update_layout(title='Past 12 month')
        figure2 = px.bar(c1, x=inpt, y='Sale_Amount (%)')
        figure2.update_layout(yaxis={'categoryorder': 'total descending'})
        figure2.update_traces(marker_color='skyblue')
        figure3 = go.Figure(data=[go.Table(header=dict(values=list(x1.columns)),
                                           cells=dict(values=[x1[k].tolist() for k in x1.columns]))])
    if input3 == 'Relative':
        return dcc.Graph(figure=figure), dcc.Graph(figure=figure1)
    elif input3 == 'Absolute':
        return dcc.Graph(figure=figure2), dcc.Graph(figure=figure3)


# if __name__ == '__main__':
#     app.run_server(mode="external")

# dt.datetime.now().date()
#
# a = 'Q1-2021'
# i = a.split('-')
# i[0]
