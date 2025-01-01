import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Load your data
df = pd.read_csv('data_healthcare.csv')

# Data preprocessing
df['Birthdate'] = pd.to_datetime(df['Birthdate'], errors='coerce')
df['Age'] = 2024 - df['Birthdate'].dt.year
df['Year'] = pd.to_datetime(df['Patient Visit Date'], format='%d-%m-%Y %H:%M').dt.year
df['Month'] = pd.to_datetime(df['Patient Visit Date'], format='%d-%m-%Y %H:%M').dt.month

# Create a new column 'Nationality_Group' using list comprehension
df['Nationality_Group'] = ['Kuwaiti' if nat == 'Kuwaiti' else 'Non-Kuwaiti' for nat in df['Nationality']]

st.set_page_config(page_title= "Exploratory Data Analysis", page_icon= ':bar_chart:', layout = 'wide')

# Streamlit layout
st.title(" :bar_chart: Healthcare Data Analysis Dashboard")
st.markdown('<style>.div.block-container{padding-top:1rem;}.</style>', unsafe_allow_html= True)

# Sidebar filters
st.sidebar.header("Filters")

# Filter by gender
genders = st.sidebar.multiselect(
    "Gender",
    options=df['Sex'].unique(),
    default=[]
)

# If no genders are selected, consider all genders selected
if not genders:
    genders = df['Sex'].unique()

# Filter by Year
years = st.sidebar.multiselect(
    "Year",
    options=sorted(df['Year'].unique()),
    default=[]
)

# If no year is selected, consider all years selected
if not years:
    years = df['Year'].unique()

# Filter by nationality
nationalities = st.sidebar.multiselect(
    "Nationality",
    options=df['Nationality_Group'].unique(),
    default=[]
)

# If no nationalities are selected, consider all nationalities selected
if not nationalities:
    nationalities = df['Nationality_Group'].unique()

# Filter the data based on the selections
filtered_df = df[df['Year'].isin(years) & df['Sex'].isin(genders) & df['Nationality_Group'].isin(nationalities)]

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-container {
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 18px;
        text-align: center;
        width: 100%;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .total-patients {
        background-color: #007bff;
    }
    .male-patients {
        background-color: #28a745;
    }
    .female-patients {
        background-color: #dc3545;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        padding: 10px 0;
        margin-top: 30px;
        color: #444;
        border-bottom: 2px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# Section 1: Patient Summary
st.markdown("<div class='section-title'>Patient Summary</div>", unsafe_allow_html=True)

total_patients = len(filtered_df)
total_male_patients = len(filtered_df[filtered_df['Sex'] == 'Male'])
total_female_patients = len(filtered_df[filtered_df['Sex'] == 'Female'])

male_percentage = (total_male_patients / total_patients * 100) if total_patients > 0 else 0
female_percentage = (total_female_patients / total_patients * 100) if total_patients > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="metric-container total-patients">Total Patients<br><h3>{total_patients}</h3></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-container male-patients">Male<br><h3>{total_male_patients}</h3><p>{male_percentage:.2f}% Male</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-container female-patients">Female<br><h3>{total_female_patients}</h3><p>{female_percentage:.2f}% Female</p></div>', unsafe_allow_html=True)

# Section 2: Nationality and Gender Charts
st.markdown("<div class='section-title'>Demographics Analysis</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    nationality_counts_filtered = filtered_df.groupby('Nationality')['patient_id'].count().reset_index().rename(columns={'patient_id': 'count'})
    nationality_bar = px.bar(nationality_counts_filtered, x='Nationality', y='count', color='Nationality', text='count',
                             title="Patient Count by Nationality", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(nationality_bar)

with col2:
    gender_counts_filtered = filtered_df.groupby('Sex')['patient_id'].count().reset_index().rename(columns={'patient_id': 'count'})
    gender_pie = px.pie(gender_counts_filtered, values='count', names='Sex',
                        title="Gender Distribution", hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(gender_pie)

# Section 3: Age Distribution and Department Analysis
st.markdown("<div class='section-title'>Age and Department Analysis</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    age_histogram = px.histogram(
        filtered_df, x='Age', nbins=15, title="Age Distribution of Patients", labels={'Age': 'Patient Age'},
        text_auto=True, color_discrete_sequence=px.colors.qualitative.Prism
    )
    age_histogram.update_layout(bargap=0.01)
    st.plotly_chart(age_histogram)

with col2:
    department_patient_counts_filtered = filtered_df.groupby('department')['patient_id'].count().reset_index().rename(columns={'patient_id': 'count'})
    department_patient_bar = px.bar(department_patient_counts_filtered, x='department', y='count', color='department', text='count',
                                    title="Number of Patients by Department", color_discrete_sequence=px.colors.qualitative.Vivid)
    st.plotly_chart(department_patient_bar)

# Section 4: Growth Analysis Table
st.markdown("<div class='section-title'>Yearly Growth Analysis</div>", unsafe_allow_html=True)

monthly_patient_count = filtered_df.groupby(['Year', 'Month']).agg({'patient_id': 'count'}).reset_index()
pivot_df = monthly_patient_count.pivot_table(index='Month', columns='Year', values='patient_id', aggfunc='sum')

# Calculate year-over-year growth
growth_df = pivot_df.pct_change(axis='columns') * 100
growth_columns = [f"Growth_{year}" for year in pivot_df.columns[1:]]
growth_df = growth_df.iloc[:, 1:]
growth_df.columns = growth_columns

# Combine the original pivot table with the growth table
final_df = pd.concat([pivot_df, growth_df], axis=1)

def highlight_growth(val):
    if pd.isna(val):
        return ''
    elif val < -20 or val > 20:
        return 'background-color: yellow'
    else:
        return ''

styled_df = final_df.style.applymap(highlight_growth, subset=growth_columns)
st.dataframe(styled_df.format("{:.2f}"), height=460, width=1000)

# Section 5: Trends Over Time
st.markdown("<div class='section-title'>Patient Trends Over Time</div>", unsafe_allow_html=True)

monthly_patient_count = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Patient_Count')
patient_trend_fig = px.line(monthly_patient_count, x='Month', y='Patient_Count', color='Year',
                            title="Number of Patients per Month for Different Years", labels={'Month': 'Month', 'Patient_Count': 'Number of Patients'})

patient_trend_fig.update_layout(xaxis=dict(showline=True, showgrid=False, showticklabels=True, linecolor='black', tickfont=dict(size=12, color='black')),
                                yaxis=dict(showline=True, showgrid=False, showticklabels=True, linecolor='black', tickfont=dict(size=12, color='black')))
st.plotly_chart(patient_trend_fig)


# Group by 'Hospital' and 'Year', and get the minimum cost
hospital_min_cost_df = filtered_df.groupby(['Hospital Name', 'Year']).agg(Minimum_Cost=('cost', 'min')).reset_index()



fig = px.scatter(hospital_min_cost_df,
                 x='Hospital Name',
                 y='Year',
                 size='Minimum_Cost',
                 color='Hospital Name',
                 title="Bubble Chart of Minimum Cost per Hospital for the Last 4 Years",
                 labels={'Minimum_Cost': 'Minimum Cost', 'Year': 'Year'},
                 hover_data={'Minimum_Cost': True},
                 size_max=60)

# Update layout for text styling and appearance
fig.update_traces(
    textposition='middle center',  # Position the text in the middle of the bubbles
    textfont=dict(size=12, color='black')  # Set font size and color for visibility
)

# Display the plot in Streamlit
st.plotly_chart(fig)

hospital_max_cost_df = filtered_df.groupby(['Hospital Name', 'Year']).agg(Maximum_Cost=('cost', 'max')).reset_index()

fig = px.scatter(hospital_max_cost_df,
                 x='Hospital Name',
                 y='Year',
                 size='Maximum_Cost',
                 color='Hospital Name',
                 title="Bubble Chart of Maximum Cost per Hospital for the Last 4 Years",
                 labels={'Maximum_Cost': 'Maximum Cost', 'Year': 'Year'},
                 hover_data={'Maximum_Cost': True},
                 size_max=60)

# Update layout for text styling and appearance
fig.update_traces(
    textposition='middle center',  # Position the text in the middle of the bubbles
    textfont=dict(size=12, color='black')  # Set font size and color for visibility
)

# Display the plot in Streamlit
st.plotly_chart(fig)

# # Group by payment method and count the number of patients
# payment_method_counts = filtered_df.groupby('payment_method')['patient_id'].count().reset_index()
# payment_method_counts.rename(columns={'patient_id': 'Total Patients'}, inplace=True)
#
# # Create a bar chart using Plotly Express
# payment_method_bar = px.bar(
#     payment_method_counts,
#     x='payment_method',
#     y='Total Patients',
#     color='payment_method',
#     text='Total Patients',
#     title="Total Patients by Payment Method",
#     color_discrete_sequence=px.colors.qualitative.Vivid
# )
#
# # Show the chart in Streamlit
# st.plotly_chart(payment_method_bar)

# Group by payment method and count the number of patients
payment_method_counts = filtered_df.groupby('payment_method')['patient_id'].count().reset_index()
payment_method_counts.rename(columns={'patient_id': 'Total Patients'}, inplace=True)

# Calculate the percentage of patients for each payment method
payment_method_counts['Percentage'] = (payment_method_counts['Total Patients'] / payment_method_counts['Total Patients'].sum()) * 100

# Create a new column for the text to display inside the bars (count and percentage)
payment_method_counts['Display_Text'] = payment_method_counts.apply(
    lambda row: f"{row['Total Patients']} ({row['Percentage']:.2f}%)", axis=1)

# Create a bar chart using Plotly Express
payment_method_bar = px.bar(
    payment_method_counts,
    x='payment_method',
    y='Total Patients',
    color='payment_method',
    text='Display_Text',  # Use the combined count and percentage as the text inside the bars
    title="Total Patients by Payment Method",
    color_discrete_sequence=px.colors.qualitative.Vivid
)

# Customize the layout for better readability
payment_method_bar.update_traces(texttemplate='%{text}', textposition='inside')
payment_method_bar.update_layout(
    uniformtext_minsize=10,
    uniformtext_mode='hide',  # Hide text if it doesn't fit
    xaxis_title='Payment Method',
    yaxis_title='Total Patients',
    title_x=0,
    showlegend=False
)

# Show the chart in Streamlit
st.plotly_chart(payment_method_bar)