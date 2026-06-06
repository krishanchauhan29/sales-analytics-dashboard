import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Config ---
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('data/superstore_processed.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=80)
st.sidebar.title("🔍 Filters")

years = sorted(df['Order Year'].unique())
selected_years = st.sidebar.multiselect("Select Year", years, default=years)

regions = sorted(df['Region'].unique())
selected_regions = st.sidebar.multiselect("Select Region", regions, default=regions)

categories = sorted(df['Category'].unique())
selected_categories = st.sidebar.multiselect("Select Category", categories, default=categories)

# --- Filter Data ---
filtered = df[
    (df['Order Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Category'].isin(selected_categories))
]

# --- Header ---
st.title("📊 Superstore Sales Analytics Dashboard")
st.markdown("**Interactive business intelligence dashboard for sales performance analysis**")
st.markdown("---")

# --- KPI Cards ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue", f"${filtered['Sales'].sum():,.0f}")
col2.metric("📈 Total Profit", f"${filtered['Profit'].sum():,.0f}")
col3.metric("🛒 Total Orders", f"{filtered['Order ID'].nunique():,}")
col4.metric("👥 Customers", f"{filtered['Customer ID'].nunique():,}")
col5.metric("📦 Avg Ship Days", f"{filtered['Shipping Days'].mean():.1f} days")

st.markdown("---")

# --- Row 1: Yearly Trend + Category Sales ---
col1, col2 = st.columns(2)

with col1:
    yearly = filtered.groupby('Order Year').agg(
        Sales=('Sales','sum'), Profit=('Profit','sum')
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=yearly['Order Year'], y=yearly['Sales'],
                         name='Sales', marker_color='#2196F3'), secondary_y=False)
    fig.add_trace(go.Scatter(x=yearly['Order Year'], y=yearly['Profit'],
                             name='Profit', line=dict(color='red', width=2.5),
                             mode='lines+markers'), secondary_y=True)
    fig.update_layout(title='📅 Yearly Sales & Profit Trend', height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cat = filtered.groupby('Category')['Sales'].sum().reset_index()
    fig = px.pie(cat, values='Sales', names='Category',
                 title='🏷️ Sales by Category',
                 color_discrete_sequence=['#2196F3','#4CAF50','#FF9800'],
                 hole=0.4)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- Row 2: Regional Performance + Monthly Heatmap ---
col1, col2 = st.columns(2)

with col1:
    region = filtered.groupby('Region').agg(
        Sales=('Sales','sum'), Profit=('Profit','sum')
    ).reset_index().sort_values('Sales', ascending=False)
    fig = px.bar(region, x='Region', y=['Sales','Profit'],
                 title='🗺️ Regional Performance',
                 barmode='group',
                 color_discrete_sequence=['#1565C0','#43A047'])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    monthly = filtered.groupby(['Order Month', 'Order Month Name'])['Sales'].sum().reset_index()
    monthly = monthly.sort_values('Order Month')
    fig = px.bar(monthly, x='Order Month Name', y='Sales',
                 title='📆 Monthly Sales Pattern',
                 color='Sales',
                 color_continuous_scale='Blues')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- Row 3: Top Products + Discount Impact ---
col1, col2 = st.columns(2)

with col1:
    top_prod = filtered.groupby('Sub-Category')['Profit'].sum().reset_index()
    top_prod = top_prod.sort_values('Profit', ascending=True)
    colors = ['#E53935' if x < 0 else '#43A047' for x in top_prod['Profit']]
    fig = go.Figure(go.Bar(
        x=top_prod['Profit'], y=top_prod['Sub-Category'],
        orientation='h', marker_color=colors
    ))
    fig.update_layout(title='💹 Profit by Sub-Category (Red = Loss)', height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(filtered, x='Discount', y='Profit',
                     color='Category', opacity=0.5,
                     title='🎯 Discount vs Profit Analysis',
                     color_discrete_sequence=['#2196F3','#FF9800','#E91E63'])
    fig.add_hline(y=0, line_dash='dash', line_color='black')
    fig.add_vline(x=0.2, line_dash='dash', line_color='orange',
                  annotation_text='20% threshold')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("**📌 Key Insights:** West region leads in profit | Central region needs attention (-10.4% margin) | Discounts >20% cause losses | Technology drives highest revenue")
st.caption("Dashboard by Krishan Kumar Chauhan | M.Tech Data Science, GBU")