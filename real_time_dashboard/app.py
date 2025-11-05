# app.py
"""
🌐 Real-Time Global Insights Dashboard
-------------------------------------
Includes live:
- Stock Prices
- COVID-19 Stats
- Weather
- Cryptocurrency Tracker
- Global Market Leaders
- Tech News Feed

Built with Dash 3+, Plotly, and Public APIs.
Author: Nitika Niti
"""

import requests
import pandas as pd
import yfinance as yf
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

# ---------------------- Helper Functions ---------------------- #

def fetch_stock_data(ticker):
    """Fetch live stock data from Yahoo Finance"""
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="1d", interval="5m")
        df = df.reset_index()
        return df
    except Exception:
        return pd.DataFrame()

def fetch_covid_data(country):
    """Fetch COVID-19 stats by country"""
    try:
        url = f"https://disease.sh/v3/covid-19/countries/{country}?strict=true"
        data = requests.get(url).json()
        return data
    except Exception:
        return None

def fetch_weather(city):
    """Fetch live weather info by city"""
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()
        return weather["current_weather"]
    except Exception:
        return None

def fetch_crypto_data():
    """Fetch top crypto prices"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "ids": "bitcoin,ethereum,solana,dogecoin"}
        data = requests.get(url, params=params).json()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

def fetch_market_caps():
    """Static global market caps for big tech companies"""
    companies = {
        "Apple": 3.1, "Microsoft": 2.8, "Amazon": 1.9, "Google": 2.0,
        "NVIDIA": 2.3, "Meta": 1.3, "Tesla": 0.9, "Samsung": 0.6
    }
    df = pd.DataFrame(list(companies.items()), columns=["Company", "MarketCap"])
    return df.sort_values("MarketCap", ascending=False)

def fetch_tech_news():
    """Fetch latest tech news headlines"""
    try:
        url = "https://hn.algolia.com/api/v1/search?query=technology&tags=story&hitsPerPage=5"
        data = requests.get(url).json()
        return [(item["title"], item["url"]) for item in data["hits"]]
    except Exception:
        return []

# ---------------------- App Setup ---------------------- #

app = Dash(__name__, title="🌐 Real-Time Dashboard", suppress_callback_exceptions=True)

app.layout = html.Div(className="main-container", children=[

    html.H1("🌐 Real-Time Global Insights Dashboard", className="main-title"),
    html.P("Stay updated with live stocks, crypto, weather, and more — beautifully visualized.", className="subtitle"),

    # Stock Section
    html.Div(className="card glass", children=[
        html.H2("📈 Live Stock Prices", className="card-title"),
        html.Div(className="input-row", children=[
            dcc.Input(id="stock-ticker", type="text", value="AAPL", placeholder="Enter Stock Symbol", className="input-box"),
            html.Button("Load", id="load-stock", className="button"),
        ]),
        dcc.Loading(dcc.Graph(id="stock-graph"), type="circle", color="#00ffff"),
        html.Div(id="stock-info", className="info-text"),
        dcc.Interval(id="stock-interval", interval=60000, n_intervals=0)
    ]),

    # COVID Section
    html.Div(className="card glass", children=[
        html.H2("🦠 COVID-19 Stats", className="card-title"),
        html.Div(className="input-row", children=[
            dcc.Input(id="country", type="text", value="India", placeholder="Enter Country", className="input-box"),
            html.Button("Fetch", id="load-covid", className="button"),
        ]),
        dcc.Loading(html.Div(id="covid-info", className="info-text"), type="circle", color="#00ffff"),
        dcc.Interval(id="covid-interval", interval=120000, n_intervals=0)
    ]),

    # Weather Section
    html.Div(className="card glass", children=[
        html.H2("🌤 Weather Updates", className="card-title"),
        html.Div(className="input-row", children=[
            dcc.Input(id="city", type="text", value="New Delhi", placeholder="Enter City", className="input-box"),
            html.Button("Check", id="load-weather", className="button"),
        ]),
        dcc.Loading(html.Div(id="weather-info", className="info-text"), type="circle", color="#00ffff"),
        dcc.Interval(id="weather-interval", interval=180000, n_intervals=0)
    ]),

    # Crypto Section
    html.Div(className="card glass", children=[
        html.H2("💰 Cryptocurrency Tracker", className="card-title"),
        dcc.Loading(dcc.Graph(id="crypto-graph"), type="circle", color="#00ffff"),
        dcc.Interval(id="crypto-interval", interval=60000, n_intervals=0)
    ]),

    # Market Cap Section
    html.Div(className="card glass", children=[
        html.H2("🏦 Global Tech Company Market Caps (Trillions USD)", className="card-title"),
        dcc.Graph(id="marketcap-graph"),
    ]),

    # News Feed
    html.Div(className="card glass", children=[
        html.H2("📰 Latest Tech News", className="card-title"),
        html.Div(id="news-feed", className="news-section"),
        dcc.Interval(id="news-interval", interval=300000, n_intervals=0)
    ]),

    html.Footer("© 2025 Real-Time Dashboard by Nitika Niti", className="footer")
])

# ---------------------- Callbacks ---------------------- #

@app.callback(
    Output("stock-graph", "figure"),
    Output("stock-info", "children"),
    Input("load-stock", "n_clicks"),
    Input("stock-interval", "n_intervals"),
    State("stock-ticker", "value"),
    prevent_initial_call=False
)
def update_stock(n_clicks, n_intervals, ticker):
    df = fetch_stock_data(ticker)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No Stock Data Found", template="plotly_dark")
        return fig, f"No data for {ticker}"
    fig = px.line(df, x="Datetime", y="Close", title=f"{ticker} Live Price", template="plotly_dark", markers=True)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    latest = df.iloc[-1]
    return fig, f"Last Updated: {latest['Datetime']} | Price: ${latest['Close']:.2f}"

@app.callback(
    Output("covid-info", "children"),
    Input("load-covid", "n_clicks"),
    Input("covid-interval", "n_intervals"),
    State("country", "value"),
    prevent_initial_call=False
)
def update_covid(n_clicks, n_intervals, country):
    data = fetch_covid_data(country)
    if not data:
        return html.P("⚠️ No data available.", className="warning")
    return html.Div([
        html.P(f"Country: {data['country']}"),
        html.P(f"Cases: {data['cases']:,}"),
        html.P(f"Active: {data['active']:,}"),
        html.P(f"Recovered: {data['recovered']:,}"),
        html.P(f"Deaths: {data['deaths']:,}")
    ])

@app.callback(
    Output("weather-info", "children"),
    Input("load-weather", "n_clicks"),
    Input("weather-interval", "n_intervals"),
    State("city", "value"),
    prevent_initial_call=False
)
def update_weather(n_clicks, n_intervals, city):
    data = fetch_weather(city)
    if not data:
        return html.P("⚠️ No weather data available.", className="warning")
    return html.Div([
        html.P(f"Temperature: {data['temperature']}°C"),
        html.P(f"Windspeed: {data['windspeed']} m/s"),
        html.P(f"Time: {data['time']}")
    ])

@app.callback(
    Output("crypto-graph", "figure"),
    Input("crypto-interval", "n_intervals"),
    prevent_initial_call=False
)
def update_crypto(n):
    df = fetch_crypto_data()
    if df.empty:
        return go.Figure()
    fig = px.bar(df, x="name", y="current_price", color="name",
                 title="Top Cryptos (USD)", text="current_price", template="plotly_dark")
    fig.update_traces(texttemplate="$%{text}", textposition="outside")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

@app.callback(
    Output("marketcap-graph", "figure"),
    Input("crypto-interval", "n_intervals")
)
def update_marketcap(n):
    df = fetch_market_caps()
    fig = px.bar(df, x="Company", y="MarketCap", color="Company", template="plotly_dark")
    fig.update_traces(marker_line_color="#00ffff", marker_line_width=1.5)
    return fig

@app.callback(
    Output("news-feed", "children"),
    Input("news-interval", "n_intervals"),
    prevent_initial_call=False
)
def update_news(n):
    news = fetch_tech_news()
    if not news:
        return html.P("⚠️ No latest news available.", className="warning")
    return [
        html.Div(className="news-item", children=[
            html.A(title, href=link, target="_blank", className="news-link")
        ]) for title, link in news
    ]

# ---------------------- Run Server ---------------------- #
if __name__ == "__main__":
    app.run(debug=True)
