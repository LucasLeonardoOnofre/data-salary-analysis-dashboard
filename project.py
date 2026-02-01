import streamlit as st
import pandas as pd
import plotly.express as px

# streamlit run .venv/project.py
# Command to run the Streamlit app from the terminal

# ======================================================
# PAGE CONFIGURATION
# ======================================================
# st.set_page_config must be called before any other Streamlit command.
# It defines global settings such as title, icon, and layout.
st.set_page_config(
    page_title="Data Salaries Dashboard",
    page_icon="📊",
    layout="wide",  # Uses the full browser width
)

# ======================================================
# DATA LOADING
# ======================================================
# Reads a CSV file directly from a GitHub repository URL
df = pd.read_csv(
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
)

# ======================================================
# SIDEBAR (FILTERS)
# ======================================================
# st.sidebar creates a fixed sidebar on the left side of the app
st.sidebar.header("🔍 Filters")

# Year filter (multiselect allows multiple choices)
available_years = sorted(df['ano'].unique())
selected_years = st.sidebar.multiselect(
    "Year",
    available_years,
    default=available_years
)

# Seniority filter
available_seniorities = sorted(df['senioridade'].unique())
selected_seniorities = st.sidebar.multiselect(
    "Seniority",
    available_seniorities,
    default=available_seniorities
)

# Contract type filter
available_contract_types = sorted(df['contrato'].unique())
selected_contract_types = st.sidebar.multiselect(
    "Contract Type",
    available_contract_types,
    default=available_contract_types
)

# Company size filter
available_company_sizes = sorted(df['tamanho_empresa'].unique())
selected_company_sizes = st.sidebar.multiselect(
    "Company Size",
    available_company_sizes,
    default=available_company_sizes
)

# ======================================================
# DATA FILTERING
# ======================================================
# The main DataFrame is filtered according to the sidebar selections.
filtered_df = df[
    (df['ano'].isin(selected_years)) &
    (df['senioridade'].isin(selected_seniorities)) &
    (df['contrato'].isin(selected_contract_types)) &
    (df['tamanho_empresa'].isin(selected_company_sizes))
]

# ======================================================
# MAIN PAGE CONTENT
# ======================================================
st.title("🎲 Data Salaries Analysis Dashboard")
st.markdown(
    "Explore salary data in the data field over recent years. "
    "Use the filters on the left to refine your analysis."
)

# ======================================================
# KPI METRICS
# ======================================================
# KPIs are high-level numeric indicators shown at the top of the dashboard
st.subheader("General metrics (Annual salary in USD)")

if not filtered_df.empty:
    average_salary = filtered_df['usd'].mean()
    maximum_salary = filtered_df['usd'].max()
    total_records = filtered_df.shape[0]
    most_frequent_role = filtered_df['cargo'].mode()[0]
else:
    average_salary = 0
    maximum_salary = 0
    total_records = 0
    most_frequent_role = ""

# st.columns creates a responsive grid layout
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average salary", f"${average_salary:,.0f}")
col2.metric("Maximum salary", f"${maximum_salary:,.0f}")
col3.metric("Total records", f"{total_records:,}")
col4.metric("Most frequent role", most_frequent_role)

st.markdown("---")  # Horizontal divider

# ======================================================
# VISUAL ANALYSIS (PLOTLY CHARTS)
# ======================================================
st.subheader("Charts")

# First row of charts
col_chart_1, col_chart_2 = st.columns(2)

with col_chart_1:
    if not filtered_df.empty:
        top_roles = (
            filtered_df
            .groupby('cargo')['usd']
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        roles_bar_chart = px.bar(
            top_roles,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 roles by average salary",
            labels={
                'usd': 'Average annual salary (USD)',
                'cargo': ''
            }
        )

        roles_bar_chart.update_layout(
            title_x=0.1,
            yaxis={'categoryorder': 'total ascending'}
        )

        # st.plotly_chart renders Plotly figures inside Streamlit
        st.plotly_chart(roles_bar_chart, use_container_width=True)
    else:
        st.warning("No data available to display the roles chart.")

with col_chart_2:
    if not filtered_df.empty:
        salary_histogram = px.histogram(
            filtered_df,
            x='usd',
            nbins=30,
            title="Annual salary distribution",
            labels={
                'usd': 'Salary range (USD)',
                'count': ''
            }
        )

        salary_histogram.update_layout(title_x=0.1)
        st.plotly_chart(salary_histogram, use_container_width=True)
    else:
        st.warning("No data available to display the salary distribution chart.")

# Second row of charts
col_chart_3, col_chart_4 = st.columns(2)

with col_chart_3:
    if not filtered_df.empty:
        work_type_counts = filtered_df['remoto'].value_counts().reset_index()
        work_type_counts.columns = ['work_type', 'count']

        work_type_pie_chart = px.pie(
            work_type_counts,
            names='work_type',
            values='count',
            title="Proportion of work types",
            hole=0.5  # Donut chart
        )

        work_type_pie_chart.update_traces(textinfo='percent+label')
        work_type_pie_chart.update_layout(title_x=0.1)
        st.plotly_chart(work_type_pie_chart, use_container_width=True)
    else:
        st.warning("No data available to display the work types chart.")

with col_chart_4:
    if not filtered_df.empty:
        data_scientists_df = filtered_df[filtered_df['cargo'] == 'Data Scientist']

        average_salary_by_country = (
            data_scientists_df
            .groupby('residencia_iso3')['usd']
            .mean()
            .reset_index()
        )

        country_choropleth = px.choropleth(
            average_salary_by_country,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title="Average Data Scientist salary by country",
            labels={
                'usd': 'Average salary (USD)',
                'residencia_iso3': 'Country'
            }
        )

        country_choropleth.update_layout(title_x=0.1)
        st.plotly_chart(country_choropleth, use_container_width=True)
    else:
        st.warning("No data available to display the country chart.")

# ======================================================
# DETAILED DATA TABLE
# ======================================================
# st.dataframe renders an interactive, scrollable table
st.subheader("Detailed Data")
st.dataframe(filtered_df)
