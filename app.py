import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Trekking in Nepal",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("nepal-trek-data.csv")
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif !important;
}

body {
    background-color: #f6f7fb;
}

/* Main container padding */
.block-container {
    padding-top: 2rem;
}

/* Sidebar spacing */
section[data-testid="stSidebar"] > div {
    padding: 20px;
}

.sidebar-space {
    margin-bottom: 20px;
}

/* KPI Cards */
.kpi-wrapper {
    background: white;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    transition: transform 0.2s ease;
    text-align: center;
}

.kpi-wrapper:hover {
    transform: translateY(-4px);
}

.kpi-title {
    font-size: 14px;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 32px;
    font-weight: 600;
    color: #111827;
}

/* Section cards */
.section-card {
    background: white;
   height: 1px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 35px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA CLEANING ----------------
df['Max Altitude'] = (
    df['Max Altitude']
    .astype(str)
    .str.extract(r'(\d{3,5})')
    .astype(float)
)

df['Days'] = (
    df['Time']
    .astype(str)
    .str.extract(r'(\d+)')
    .astype(float)
)

df['Cost (USD)'] = (
    df['Cost (USD)']
    .astype(str)
    .str.replace('\n', '', regex=False)
    .str.replace('USD', '', regex=False)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .str.strip()
    .astype(float)
)

grade_map = {
    'Light': 'Light',
    'Light+Moderate': 'Light',
    'Easy': 'Easy',
    'Easy To Moderate': 'Easy',
    'Easy-Moderate': 'Easy',
    'Moderate': 'Moderate',
    'Moderate+Demanding': 'Moderate',
    'Moderate-Hard': 'Moderate',
    'Strenuous': 'Strenuous',
    'Demanding': 'Demanding',
    'Demanding+Challenging': 'Demanding'
}
df['Trip Grade'] = df['Trip Grade'].map(grade_map)

accommodation_map = {
    'Hotel/Guesthouse': 'Hotel/Guesthouse',
    'Hotel/Guest Houses': 'Hotel/Guesthouse',
    'Hotel/Guesthouses': 'Hotel/Guesthouse',
    'Hotel/Teahouse': 'Hotel/Teahouse',
    'Hotel/Teahouses': 'Hotel/Teahouse',
    'Hotel/Luxury Lodges': 'Hotel/Luxury Lodge',
    'Hotel/Lodges': 'Hotel/Lodge',
    'Teahouses/Lodges': 'Teahouse/Lodge'
}
df['Accomodation'] = df['Accomodation'].map(accommodation_map)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Filters")

st.sidebar.markdown('<div class="sidebar-space"></div>', unsafe_allow_html=True)
grade_filter = st.sidebar.multiselect(
    "Trip Grade",
    options=df['Trip Grade'].unique(),
    default=df['Trip Grade'].unique()
)

st.sidebar.markdown('<div class="sidebar-space"></div>', unsafe_allow_html=True)
accommodation_filter = st.sidebar.multiselect(
    "Accommodation Type",
    options=df['Accomodation'].unique(),
    default=df['Accomodation'].unique()
)

st.sidebar.markdown('<div class="sidebar-space"></div>', unsafe_allow_html=True)
min_cost = int(df['Cost (USD)'].min())
max_cost = int(df['Cost (USD)'].max())

cost_range = st.sidebar.slider(
    "Cost Range (USD)",
    min_value=min_cost,
    max_value=max_cost,
    value=(min_cost, max_cost)
)

filtered_df = df[
    (df['Trip Grade'].isin(grade_filter)) &
    (df['Accomodation'].isin(accommodation_filter)) &
    (df['Cost (USD)'].between(cost_range[0], cost_range[1]))
]

# ---------------- TITLE ----------------
st.title("Trekking in Nepal")
st.markdown(
    "An interactive dashboard exploring trekking routes, difficulty levels, cost, altitude, and accommodation trends across Nepal."
)
st.markdown("---")

# ---------------- KPI SECTION ----------------
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="kpi-wrapper">
        <div class="kpi-title">Total Treks</div>
        <div class="kpi-value">{len(filtered_df)}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-wrapper">
        <div class="kpi-title">Average Cost (USD)</div>
        <div class="kpi-value">${int(filtered_df['Cost (USD)'].mean())}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-wrapper">
        <div class="kpi-title">Average Duration (Days)</div>
        <div class="kpi-value">{round(filtered_df['Days'].mean(), 1)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- VISUALIZATIONS ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Treks by Trip Grade")
fig, ax = plt.subplots()
sns.countplot(data=filtered_df, x='Trip Grade', ax=ax)
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Cost vs Duration")
fig, ax = plt.subplots()
sns.scatterplot(data=filtered_df, x='Days', y='Cost (USD)', ax=ax)
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Maximum Altitude by Trip Grade")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Trip Grade', y='Max Altitude', ax=ax)
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Cost by Accommodation Type")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Accomodation', y='Cost (USD)', ax=ax)
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)
