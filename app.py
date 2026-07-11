import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="Premier League Market Values", page_icon="⚽", layout="wide")
st.title("⚽ Premier League Market Value Tracker")
st.markdown("This dashboard pulls live data from a MotherDuck cloud data warehouse.")

# --- Database Connection ---
# Streamlit caches this connection so it doesn't reconnect on every button click
@st.cache_resource
def get_db_connection():
    token = st.secrets["MOTHERDUCK_TOKEN"]
    # Connect to the MotherDuck database we created earlier
    return duckdb.connect(f'md:football_analytics?motherduck_token={token}')

con = get_db_connection()

# --- Data Fetching ---
@st.cache_data
def load_data():
    # Query the data directly from the cloud
    query = """
        SELECT * FROM stg_market_values 
        ORDER BY market_value_eur DESC
    """
    return con.execute(query).df()

df = load_data()

# --- Dashboard UI ---
# Sidebar for filtering
st.sidebar.header("Filter Options")
selected_club = st.sidebar.selectbox("Select a Club", ["All Clubs"] + sorted(df['club'].unique().tolist()))

# Filter the dataframe based on selection
if selected_club != "All Clubs":
    filtered_df = df[df['club'] == selected_club]
else:
    filtered_df = df

# Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Players Tracked", f"{len(filtered_df)}")
col2.metric("Total Value (Selected)", f"€{(filtered_df['market_value_eur'].sum() / 1_000_000_000):.2f} Billion")
col3.metric("Highest Valued Player", filtered_df.iloc[0]['player_name'] if not filtered_df.empty else "N/A")

st.divider()

# Layout with two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Top 10 Most Valuable Players")
    top_10 = filtered_df.head(10).sort_values(by="market_value_eur", ascending=True)
    fig = px.bar(top_10, x="market_value_eur", y="player_name", orientation='h', 
                 title=f"Top 10 Players in {selected_club}",
                 labels={"market_value_eur": "Market Value (€)", "player_name": ""})
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    if selected_club == "All Clubs":
        st.subheader("Total Squad Value by Club")
        club_values = df.groupby('club')['market_value_eur'].sum().reset_index()
        club_values = club_values.sort_values(by="market_value_eur", ascending=False)
        fig2 = px.bar(club_values, x="club", y="market_value_eur", 
                      title="Squad Values Across the League",
                      labels={"market_value_eur": "Total Value (€)", "club": ""})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.subheader("Market Value Distribution")
        # Histogram showing how many players fall into different value buckets
        fig2 = px.histogram(filtered_df, x="market_value_eur", nbins=15,
                            title=f"Value Distribution at {selected_club}",
                            labels={"market_value_eur": "Market Value (€)"})
        st.plotly_chart(fig2, use_container_width=True)

# Raw Data Expander
with st.expander("View Raw Data"):
    st.dataframe(filtered_df[['player_name', 'age', 'club', 'raw_value_string', 'market_value_eur', 'scrape_date']])