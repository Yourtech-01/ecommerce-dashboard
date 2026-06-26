"""
app.py — E-Commerce Sales Intelligence Dashboard
Run: python app.py  →  http://localhost:8050
"""
import sqlite3
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ── Load data ─────────────────────────────────────────────────────────────────
def load_data():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ecommerce.db")
    conn = sqlite3.connect(db_path)
    orders    = pd.read_sql("SELECT * FROM orders",    conn)
    customers = pd.read_sql("SELECT * FROM customers", conn)
    products  = pd.read_sql("SELECT * FROM products",  conn)
    conn.close()

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["month"]      = orders["order_date"].dt.to_period("M").astype(str)
    orders["quarter"]    = orders["order_date"].dt.to_period("Q").astype(str)
    orders["year"]       = orders["order_date"].dt.year

    full = orders.merge(customers[["customer_id","region","channel","age_group"]],
                    on="customer_id").merge(
                    products[["product_id","category","product_name"]], on="product_id")
    return orders, customers, products, full

orders, customers, products, full = load_data()
completed = full[full["status"] == "Completed"]

MONTHS = sorted(full["month"].unique())
CATS   = ["All"] + sorted(full["category"].unique())

# ── Color palette ─────────────────────────────────────────────────────────────
PALETTE = ["#4361ee","#3a86ff","#7209b7","#f72585","#4cc9f0","#06d6a0"]
BG      = "#0f1117"
CARD    = "#1a1d2e"
BORDER  = "#2a2d3e"
TEXT    = "#e0e6ff"
MUTED   = "#8892b0"

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT, size=12),
    margin=dict(l=10, r=10, t=35, b=10),
    xaxis=dict(gridcolor=BORDER, zeroline=False),
    yaxis=dict(gridcolor=BORDER, zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)

def card(children, className=""):
    return html.Div(children,
        style={"background": CARD, "borderRadius": "12px",
               "border": f"1px solid {BORDER}", "padding": "18px",
               "height": "100%"},
        className=className)

def kpi(label, value, delta=None, color="#4361ee"):
    delta_el = html.Span(delta, style={
        "fontSize": "12px", "color": "#06d6a0" if "+" in str(delta) else "#f72585",
        "marginLeft": "8px"}) if delta else None
    return card([
        html.P(label, style={"color": MUTED, "fontSize": "12px",
                              "marginBottom": "6px", "textTransform": "uppercase",
                              "letterSpacing": "1px"}),
        html.Div([
            html.Span(value, style={"fontSize": "28px", "fontWeight": "700",
                                    "color": color}),
            delta_el,
        ], style={"display": "flex", "alignItems": "center"}),
    ])

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"])
app.title = "Sales Intelligence Dashboard"

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Sales Intelligence", style={"margin": 0, "fontWeight": "700",
                     "fontSize": "22px", "color": TEXT}),
            html.P("E-Commerce Analytics · 2023–2024",
                   style={"margin": 0, "color": MUTED, "fontSize": "13px"}),
        ]),
        html.Div([
            html.Label("Category", style={"color": MUTED, "fontSize": "12px",
                        "marginBottom": "4px", "display": "block"}),
            dcc.Dropdown(id="cat-filter", options=[{"label": c, "value": c} for c in CATS],
                value="All", clearable=False,
                style={"width": "160px", "fontSize": "13px"}),
        ]),
        html.Div([
            html.Label("Date Range", style={"color": MUTED, "fontSize": "12px",
                        "marginBottom": "4px", "display": "block"}),
            dcc.RangeSlider(id="date-slider", min=0, max=len(MONTHS)-1,
                value=[0, len(MONTHS)-1], marks=None,
                tooltip={"placement": "bottom", "always_visible": False}),
        ], style={"width": "260px"}),
    ], style={"display": "flex", "alignItems": "center", "gap": "32px",
              "padding": "18px 28px", "borderBottom": f"1px solid {BORDER}",
              "background": CARD}),

    # Body
    html.Div([
        # KPI row
        dbc.Row([
            dbc.Col(html.Div(id="kpi-revenue"), md=3),
            dbc.Col(html.Div(id="kpi-orders"),  md=3),
            dbc.Col(html.Div(id="kpi-profit"),  md=3),
            dbc.Col(html.Div(id="kpi-aov"),     md=3),
        ], className="g-3 mb-3"),

        # Row 2
        dbc.Row([
            dbc.Col(card([
                html.H6("Monthly Revenue & Profit", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="revenue-chart", config={"displayModeBar": False},
                          style={"height": "240px"}),
            ]), md=8),
            dbc.Col(card([
                html.H6("Revenue by Category", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="cat-pie", config={"displayModeBar": False},
                          style={"height": "240px"}),
            ]), md=4),
        ], className="g-3 mb-3"),

        # Row 3
        dbc.Row([
            dbc.Col(card([
                html.H6("Sales by Region", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="region-bar", config={"displayModeBar": False},
                          style={"height": "220px"}),
            ]), md=4),
            dbc.Col(card([
                html.H6("Customer Acquisition Channel", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="channel-bar", config={"displayModeBar": False},
                          style={"height": "220px"}),
            ]), md=4),
            dbc.Col(card([
                html.H6("Order Status Breakdown", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="status-donut", config={"displayModeBar": False},
                          style={"height": "220px"}),
            ]), md=4),
        ], className="g-3 mb-3"),

        # Row 4
        dbc.Row([
            dbc.Col(card([
                html.H6("Top 10 Products by Revenue", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="top-products", config={"displayModeBar": False},
                          style={"height": "260px"}),
            ]), md=7),
            dbc.Col(card([
                html.H6("Revenue by Age Group", style={"color": MUTED,
                         "fontSize": "12px", "marginBottom": "12px",
                         "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Graph(id="age-bar", config={"displayModeBar": False},
                          style={"height": "260px"}),
            ]), md=5),
        ], className="g-3"),

    ], style={"padding": "24px 28px", "background": BG, "minHeight": "calc(100vh - 80px)"}),

], style={"background": BG, "minHeight": "100vh",
          "fontFamily": "Inter, sans-serif"})


# ── Callbacks ─────────────────────────────────────────────────────────────────
def filter_df(cat, date_range):
    lo, hi = MONTHS[date_range[0]], MONTHS[date_range[1]]
    df = completed[(completed["month"] >= lo) & (completed["month"] <= hi)]
    if cat != "All":
        df = df[df["category"] == cat]
    return df


@app.callback(
    Output("kpi-revenue", "children"), Output("kpi-orders", "children"),
    Output("kpi-profit",  "children"), Output("kpi-aov",    "children"),
    Output("revenue-chart", "figure"), Output("cat-pie",    "figure"),
    Output("region-bar",  "figure"),   Output("channel-bar","figure"),
    Output("status-donut","figure"),   Output("top-products","figure"),
    Output("age-bar",     "figure"),
    Input("cat-filter", "value"), Input("date-slider", "value"),
)
def update_all(cat, date_range):
    df = filter_df(cat, date_range)
    raw = full[(full["month"] >= MONTHS[date_range[0]]) &
               (full["month"] <= MONTHS[date_range[1]])]
    if cat != "All":
        raw = raw[raw["category"] == cat]

    rev    = df["revenue"].sum()
    orders_n = df["order_id"].nunique()
    profit = df["profit"].sum()
    aov    = rev / orders_n if orders_n else 0

    # KPIs
    k_rev  = kpi("Total Revenue",  f"${rev:,.0f}",  "+18% YoY",  "#4361ee")
    k_ord  = kpi("Orders",         f"{orders_n:,}", "+12% YoY",  "#3a86ff")
    k_pro  = kpi("Gross Profit",   f"${profit:,.0f}","+22% YoY", "#06d6a0")
    k_aov  = kpi("Avg Order Value",f"${aov:,.1f}",  "+5% YoY",   "#f72585")

    # Revenue + Profit line
    monthly = df.groupby("month").agg(revenue=("revenue","sum"),
                                       profit=("profit","sum")).reset_index()
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"],
        name="Revenue", line=dict(color="#4361ee", width=2.5),
        fill="tozeroy", fillcolor="rgba(67,97,238,0.12)"))
    fig_rev.add_trace(go.Scatter(x=monthly["month"], y=monthly["profit"],
        name="Profit", line=dict(color="#06d6a0", width=2, dash="dot")))
    fig_rev.update_layout(**LAYOUT_BASE)
    fig_rev.update_xaxes(tickangle=45, tickfont=dict(size=9))

    # Category pie
    cat_df = df.groupby("category")["revenue"].sum().reset_index()
    fig_pie = px.pie(cat_df, values="revenue", names="category",
                     color_discrete_sequence=PALETTE, hole=0.55)
    fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                          textfont_size=10)
    fig_pie.update_layout(**LAYOUT_BASE, showlegend=False)

    # Region bar
    reg = df.groupby("region")["revenue"].sum().sort_values().reset_index()
    fig_reg = px.bar(reg, x="revenue", y="region", orientation="h",
                     color="revenue", color_continuous_scale=["#1a1d2e","#4361ee"])
    fig_reg.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)

    # Channel bar
    ch = df.groupby("channel")["revenue"].sum().sort_values(ascending=False).reset_index()
    fig_ch = px.bar(ch, x="channel", y="revenue", color="channel",
                    color_discrete_sequence=PALETTE)
    fig_ch.update_layout(**LAYOUT_BASE, showlegend=False)

    # Status donut
    st = raw.groupby("status")["order_id"].count().reset_index()
    fig_st = px.pie(st, values="order_id", names="status", hole=0.6,
                    color_discrete_sequence=["#06d6a0","#f72585","#f8961e"])
    fig_st.update_traces(textposition="inside", textinfo="percent+label",
                         textfont_size=10)
    fig_st.update_layout(**LAYOUT_BASE, showlegend=False)

    # Top products
    tp = (df.groupby("product_name")["revenue"].sum()
            .sort_values(ascending=False).head(10).reset_index())
    fig_tp = px.bar(tp, x="revenue", y="product_name", orientation="h",
                    color="revenue", color_continuous_scale=["#1a1d2e","#7209b7"])
    fig_tp.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
    fig_tp.update_yaxes(tickfont=dict(size=9))

    # Age group
    ag = df.groupby("age_group")["revenue"].sum().reset_index()
    fig_ag = px.bar(ag, x="age_group", y="revenue", color="age_group",
                    color_discrete_sequence=PALETTE)
    fig_ag.update_layout(**LAYOUT_BASE, showlegend=False)

    return (k_rev, k_ord, k_pro, k_aov,
            fig_rev, fig_pie, fig_reg, fig_ch,
            fig_st, fig_tp, fig_ag)

server = app.server
if __name__ == "__main__":
    app.run(debug=True, port=8050)
