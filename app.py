import streamlit as st
from data_preprocessing import load_and_preprocess_data, filter_data
from data_visualization import plot_patient_summary, plot_nationality_and_gender, plot_cost_vs_hospital_box,plot_top_5_diagnosis_by_patients, plot_patients_by_year, plot_age_and_department, plot_cost_bubbles, plot_payment_method, display_growth_analysis, display_patient_trends_over_time,plot_patients_by_hospital

# Streamlit page configuration
st.set_page_config(page_title="Healthcare Data Analysis Dashboard",
                   page_icon=':bar_chart:', layout='wide')

# Load data
df = load_and_preprocess_data('data_healthcare.csv')

# Sidebar filters
st.sidebar.header("Filters")

genders = st.sidebar.multiselect("Gender", options=df['Sex'].unique(), default=[])
years = st.sidebar.multiselect("Year", options=sorted(df['Year'].unique()), default=[])
nationalities = st.sidebar.multiselect("Nationality", options=df['Nationality_Group'].unique(), default=[])

if not genders:
    genders = df['Sex'].unique()
if not years:
    years = df['Year'].unique()
if not nationalities:
    nationalities = df['Nationality_Group'].unique()

# Filter data
filtered_df = filter_data(df, genders, years, nationalities)


# Patient Summary Section
# Custom CSS to reduce the top margin
st.markdown("""
    <style>
    .css-18e3th9 {
        padding-top: 0rem;
    }
    .css-1d391kg {
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)


# Patient Summary Section
st.title(":bar_chart: :blue[__Exploratory Data Analysis - Healthcare Data__]")
plot_patient_summary(filtered_df)

# Demographics Section
plot_nationality_and_gender(filtered_df)

plot_patients_by_year(filtered_df)

# Age and Department Section
plot_age_and_department(filtered_df)

# Growth Analysis
display_growth_analysis(filtered_df)

# Display trend analysis over time
display_patient_trends_over_time(filtered_df)

# Display top 5 diagnosis by total patients
plot_top_5_diagnosis_by_patients(filtered_df)

# Cost Analysis Section
plot_cost_bubbles(filtered_df)

# Cost outliers
plot_cost_vs_hospital_box(filtered_df)

# Payment Method Analysis
plot_payment_method(filtered_df)

# Hospital capacity Analysis
plot_patients_by_hospital(filtered_df)