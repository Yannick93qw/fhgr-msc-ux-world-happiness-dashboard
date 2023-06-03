import math
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from sklearn.datasets import make_blobs

def update_cluster_number(number_of_clusters):
    color_list = ["red", "blue", "grey", "cyan", "yellow", "purple", "black", "magenta", "pink", "darkgrey"]
    colors = {str(index): color for (index, color) in zip(range(number_of_clusters), color_list)}
    x, y = make_blobs(n_samples=100, centers=number_of_clusters, n_features=2, random_state=0)
    cluster_df = pd.DataFrame(data=x, columns=["X", "Y"])
    cluster_df['cluster'] = [str(i) for i in y]
    order_list = [str(i) for i in range(number_of_clusters)]
    return (colors, x, y, cluster_df, order_list)


# new: more than one plot in a callback
# new: one plot as an input for another plot
# new: plotly go object

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.DataFrame({'y': np.random.normal(loc=0, scale=10, size=1000),
                   'x': np.random.normal(loc=10, scale=2, size=1000)})

MIN_CLUSTERS = 3
MAX_CLUSTERS = 10 

app.layout = html.Div([html.Div([html.H1("Dashboard 4")], className="header"), html.Div([dcc.Tabs(id="tabs", children=[
                 dcc.Tab(label='Tab One', id="tab_1_graphs", children=[html.Div([
                      dbc.Row([dbc.Col([dcc.Dropdown(options=['red','green','blue'], value='red', id='color', multi=False)], width=6),
                               dbc.Col([dcc.Slider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), id="min_value")], width=6)]),
                      dbc.Row([dbc.Col([dcc.Graph(id="graph_1")], width=6),
                               dbc.Col([dcc.Graph(id="graph_2")], width=6)])], className="tab_content"),]),
                 dcc.Tab(label='Tab Two', id="tab_2_graphs", children=[html.Div([
                      dbc.Row([dbc.Col([dcc.Slider(min=MIN_CLUSTERS, max=MAX_CLUSTERS, step=1, id="number_of_clusters")], width=8)]),
                      dbc.Row([dbc.Col([dcc.Graph(id="scatter")], width=8),
                               dbc.Col([dcc.Graph(id="bar")], width=4)]),
                      dbc.Row([dbc.Col([dcc.Graph(id="selected_scatter")], width=12)])], className="tab_content")]),])], className="content")])



@app.callback(Output("graph_1", "figure"), Input("color", "value"))
def update_graph_1(dropdown_value_color):
    fig = px.histogram(df, x="y", color_discrete_sequence=[dropdown_value_color])
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("graph_2", "figure"), Input("min_value", "value"))
def update_graph_2(min_value):
    if min_value:
        dff = df[df['y'] > min_value]
    else:
        dff = df
    fig = px.scatter(dff, x='x', y='y')
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("scatter", "figure"), Output("selected_scatter", "figure"), Output("bar", "figure"), Input("scatter", "relayoutData"), Input("number_of_clusters", "value"))
def update_linked_charts(selected_data, number_of_clusters):
    clusters = MIN_CLUSTERS if number_of_clusters is None else number_of_clusters
    COLORS, X, y, cluster_df, order_list = update_cluster_number(clusters)
    if selected_data is None or (isinstance(selected_data, dict) and 'xaxis.range[0]' not in selected_data):
        cluster_dff = cluster_df
    else:
        cluster_dff = cluster_df[(cluster_df['X'] >= selected_data.get('xaxis.range[0]')) &
                                 (cluster_df['X'] <= selected_data.get('xaxis.range[1]')) &
                                 (cluster_df['Y'] >= selected_data.get('yaxis.range[0]')) &
                                 (cluster_df['Y'] <= selected_data.get('yaxis.range[1]'))]

    scatter = px.scatter(cluster_dff, x="X", y="Y", color="cluster", color_discrete_map=COLORS, category_orders={"cluster": order_list}, height=750)
    scatter.update_layout(template="plotly_white", coloraxis_showscale=False)
    scatter.update_traces(marker=dict(size=8))

    selected_scatter = px.scatter(cluster_dff, x="X", y="Y", color="cluster", color_discrete_map=COLORS, category_orders={"cluster": order_list}, height=750)
    selected_scatter.update_layout(template="plotly_white", coloraxis_showscale=False, title="<b>Selected Scatter Points</b>", title_font_size=25)
    selected_scatter.update_traces(marker=dict(size=8))

    group_counts = cluster_dff[['cluster', 'X']].groupby('cluster').count()

    bar = go.Figure(data=[go.Bar(x=group_counts.index, y=group_counts['X'], marker_color= [COLORS.get(i) for i in group_counts.index])])
    bar.update_layout(height=750, template="plotly_white", title="<b>Counts per cluster</b>", xaxis_title="cluster", title_font_size= 25)
    return scatter, selected_scatter, bar 

if __name__ == '__main__':
    app.run_server(debug=True, port=8012)
