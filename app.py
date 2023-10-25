from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import plotly.graph_objs as go

csv_file_path = "assets/timetracker2.csv"
df = pd.read_csv(csv_file_path)

app = Dash(__name__)

datelist = df['Date'].unique()

activity_descriptions = ' '.join(df['Activity Description'])

# Create the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(activity_descriptions)

# Save the word cloud as an image
wordcloud.to_file("wordcloud.png")

# Load the saved word cloud image
wordcloud_image = base64.b64encode(open("wordcloud.png", "rb").read()).decode("utf-8")

how_i_feel_counts = df["How I feel"].value_counts().reset_index()
how_i_feel_counts.columns = ["How I feel", "Count"]

# Create a bar chart
how_i_feel_fig = px.bar(
    how_i_feel_counts,
    x="How I feel",
    y="Count",
    color_discrete_sequence=['#b4befe']
)

# Add styling
how_i_feel_fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cdd6f4")
)

# Convert the "Duration" column to numeric values
df["Duration"] = df["Duration"].str.extract('(\d+)').astype(float)

# Calculate the average duration
average_duration = df["Duration"].mean()

# Create a bar chart for the average duration
average_duration_fig = px.bar(
    x=["Average Duration"],
    y=[average_duration],
    title="Average Activity Duration",
    color_discrete_sequence=["#89dceb"]
)

# Add styling
average_duration_fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cdd6f4")
)

def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Time Tracker Analytics", style={'font-family': 'UbuntuMonoNerdFont'}),
            html.H3("Welcome to the Time Tracker Analytics Dashboard", style={'font-family': 'UbuntuMonoNerdFont'}),
            html.Div(
                id="intro",
                children="Explore time tracker Analytics by selecting the date.",
                style={'font-family': 'UbuntuMonoNerdFont'}
            ),
        ],
    )

def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Date"),
            dcc.Dropdown(
                id="date-dropdown",
                options=[{'label': date, 'value': date} for date in datelist],
                value=datelist[0],
            ),
        ],
    )


def generate_bar_chart(selected_date):
    filtered_df = df[df['Date'] == selected_date]
    bar_fig = px.bar(
        filtered_df,
        x='Activity Description',
        y='Duration',
        color_discrete_sequence=['#f9e2af'],
        title=f'Activity Durations on {selected_date}',
    )
    return bar_fig

def generate_pie_chart(selected_date):
    filtered_df = df[df['Date'] == selected_date]
    pie_fig2 = px.pie(
        filtered_df,
        names='Value',
        color_discrete_sequence=['#f38ba8','#a6e3a1','#f9e2af','#fab387'],
        title=f'Activity Durations by Value on {selected_date}',
    )
    return pie_fig2

def generate_duration_vs_value(selected_date):
    filtered_df = df[df['Date'] == selected_date]
    scatter_fig = px.bar(
        filtered_df,
        x='Duration',
        y='Value',
        color_discrete_sequence=['#f5e0dc'],
        title=f'Bar Plot of Duration vs. Value on {selected_date}',
    )
    return scatter_fig

def generate_radar_chart(selected_date):
    filtered_df = df[df['Date'] == selected_date]

    categories = ["Unproductive", "Neutral", "Productive"]

    productivity_scores = []
    for category in categories:
        if category == "Unproductive":
            productivity_scores.append(filtered_df[filtered_df['Activity Description'] == "Leisure"]['Activity Description'].count())
        elif category == "Neutral":
            neutral_activities = ["Lunch", "Dinner", "Breakfast"]
            neutral_count = 0
            for activity in neutral_activities:
                neutral_count += filtered_df[filtered_df['Activity Description'] == activity]['Activity Description'].count()
            productivity_scores.append(neutral_count)
        else:
            productivity_scores.append(
                filtered_df[
                    ~filtered_df['Activity Description'].isin(["Leisure", "Lunch", "Dinner", "Breakfast"])
                ]['Activity Description'].count()
            )

    radar_fig = go.Figure()

    radar_fig.add_trace(go.Scatterpolar(
        r=productivity_scores,
        theta=categories,
        fill='toself',
        name='Productivity'
    ))

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df['Activity Description'].count()]  # Adjust the range based on your productivity score scale
            )
        ),
        showlegend=False
    )

    radar_fig.update_layout(
        title=f'Daily Productivity Radar Chart on {selected_date}',
        polar=dict(
            angularaxis=dict(
                rotation=90,
                direction="clockwise"
            )
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4")
    )

    return radar_fig


def update_activity_description_pie_chart(selected_date):
    filtered_df = df[df['Date'] == selected_date]
    activity_counts = filtered_df['Activity Description'].value_counts().reset_index()
    activity_counts.columns = ["Activity Description", "Count"]

    fig = px.pie(
        activity_counts,
        names="Activity Description",
        values="Count",
        title=f"Activity Description Distribution on {selected_date}",
        hole=0.3,
    )

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(showlegend=False)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4"),
        height=800
    )

    return fig 

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("icon.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(),generate_control_card()]
            + [
                html.Div(
                     ["initial child"], id="output-clientside", style={"display": "none"}           
                ),
                html.Div(
                    id="word-cloud-card",
                    children=[
                    html.Br(),
                    html.Br(),
                    html.Hr(),
                    html.B("Word Cloud of Activity Descriptions - All Time"),
                    html.Img(src=f"data:image/png;base64,{wordcloud_image}", width="100%", height="auto"),
                    ],
                ),
                html.Div(
                    id="how-i-feel-plot-card",
                    children=[
                    html.Br(),
                    html.Br(),
                    html.B("Count of Activities by 'How I feel'"),
                    html.Hr(),
                    dcc.Graph(figure=how_i_feel_fig),
                    ],
                ),
                html.Div(
                    id="average-duration-plot-card",
                    children=[
                    html.Br(),
                    html.Br(),
                    html.B("Average Activity Duration"),
                    html.Hr(),
                    dcc.Graph(figure=average_duration_fig),
                    ],
                ),
            ],
        ),


        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.Hr(),
                        dcc.Graph(id="pie-chart"),
                    ],
                ),
                html.Div(
                    id="activity_durations_card",
                    children=[
                        html.Hr(),
                        dcc.Graph(id="bar-chart"),
                    ],
                ),
                html.Div(
                    id="activity_durations_by_value_card",
                    children=[
                        html.Hr(),
                        dcc.Graph(id="pie-chart2"),
                    ],
                ),
                html.Div(
                   id="duration_vs_value_card",  
                    children=[
                    html.Hr(),
                    dcc.Graph(id="duration_vs_value_fig"),
                    ],
                ),
                html.Div(
                    id="radar-chart-card",
                    children=[
                    html.Hr(),
                    dcc.Graph(id="radar-chart"),
                    ],
                ),
                html.Div(
                    id="activity-description-pie-chart-card",
                    children=[
                    html.Hr(),
                    dcc.Graph(id="activity-description-pie-chart"),
                    ],
                ),
            ],
        ),
    ],
)

@app.callback(
    [Output('pie-chart', 'figure'), Output('bar-chart', 'figure'), Output('pie-chart2', 'figure'), Output("activity-description-pie-chart", "figure"), Output('duration_vs_value_fig', 'figure'), Output('radar-chart', 'figure')],
    Input('date-dropdown', 'value')
)
def update_plots(selected_date):
    filtered_df = df[df['Date'] == selected_date]

    pie_fig = px.pie(
        filtered_df,
        title=f'How I feel on {selected_date}',
        names='How I feel',
        color_discrete_sequence=['#f38ba8','#a6e3a1','#f9e2af','#fab387']
    )


    pie_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4")
    )
    pie_fig2 = generate_pie_chart(selected_date)
    bar_fig = generate_bar_chart(selected_date)
    duration_vs_value_fig = generate_duration_vs_value(selected_date)
    radar_fig = generate_radar_chart(selected_date)
    activity_fig = update_activity_description_pie_chart(selected_date)
    pie_fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4")
    )
    bar_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4")
    )
    duration_vs_value_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4")
    )

    radar_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 10]  # Set a custom range based on your data
        )
    ),
    showlegend=False
    )
    return pie_fig, pie_fig2, bar_fig, duration_vs_value_fig, radar_fig, activity_fig 



if __name__ == '__main__':
    app.run(debug=True)

