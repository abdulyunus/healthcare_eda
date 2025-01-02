import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def plot_patient_summary(filtered_df):
    total_patients = len(filtered_df)
    total_male_patients = len(filtered_df[filtered_df['Sex'] == 'Male'])
    total_female_patients = len(filtered_df[filtered_df['Sex'] == 'Female'])

    male_percentage = (total_male_patients / total_patients * 100) if total_patients > 0 else 0
    female_percentage = (total_female_patients / total_patients * 100) if total_patients > 0 else 0

    # Custom CSS for metric boxes with colors
    st.markdown("""
        <style>
        .metric-container {
            padding: 2px;
            border-radius: 10px;
            color: white;
            font-size: 15px;
            text-align: center;
            width: 90%;
            height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .total-patients {
            background-color: #6495ED;  /* Blue for total patients - #007bff */ 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .male-patients {
            background-color:  #45b39d;  /* Green for male patients */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .female-patients {
            background-color:  #7f8c8d;  /* Red for female patients */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Creating columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="metric-container total-patients">Total Patients<br><h3>{total_patients}</h3></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="metric-container male-patients">Male<br><h3>{total_male_patients}</h3><p>{male_percentage:.2f}% Male</p></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="metric-container female-patients">Female<br><h3>{total_female_patients}</h3><p>{female_percentage:.2f}% Female</p></div>', unsafe_allow_html=True)


def plot_nationality_and_gender(filtered_df):
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


def plot_age_and_department(filtered_df):
    col1, col2 = st.columns(2)

    with col1:
        age_histogram = px.histogram(
            filtered_df, x='Age', nbins=15, title="Age Distribution of Patients", labels={'Age': 'Patient Age'},
            text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel
        )
        age_histogram.update_layout(bargap=0.01)
        st.plotly_chart(age_histogram)

    with col2:
        department_patient_counts_filtered = filtered_df.groupby('department')['patient_id'].count().reset_index().rename(columns={'patient_id': 'count'})
        department_patient_bar = px.bar(department_patient_counts_filtered, x='department', y='count', color='department', text='count',
                                        title="Number of Patients by Department", color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(department_patient_bar)




def display_growth_analysis(filtered_df):
    """
    Displays the Yearly Growth Analysis Table with color highlighting.

    Parameters:
    filtered_df (pd.DataFrame): The filtered DataFrame containing patient data.
    """
    #st.markdown("<div class='section-title'><b>Yearly Growth Analysis</b></div>", unsafe_allow_html=True)
    st.markdown("##### Yearly Growth Analysis")

    # Group by year and month, and count patients per month
    monthly_patient_count = filtered_df.groupby(['Year', 'Month']).agg({'patient_id': 'count'}).reset_index()

    # Create a pivot table with 'Month' as rows, 'Year' as columns, and patient count as values
    pivot_df = monthly_patient_count.pivot_table(index='Month', columns='Year', values='patient_id', aggfunc='sum')

    # Calculate year-over-year growth percentage
    growth_df = pivot_df.pct_change(axis='columns') * 100
    growth_columns = [f"Growth_{year}" for year in pivot_df.columns[1:]]
    growth_df = growth_df.iloc[:, 1:]
    growth_df.columns = growth_columns

    # Combine the original pivot table and growth table
    final_df = pd.concat([pivot_df, growth_df], axis=1)

    # Highlight growth changes
    def highlight_growth(val):
        if pd.isna(val):
            return ''
        elif val < -20 or val > 20:
            return 'background-color: yellow'
        else:
            return ''

    # Apply styling and display table
    styled_df = final_df.style.applymap(highlight_growth, subset=growth_columns)
    st.dataframe(styled_df.format("{:.2f}"), height=460, width=1000)


def display_patient_trends_over_time(filtered_df):
    """
    Displays the trends of patient count over time using a line plot.

    Parameters:
    filtered_df (pd.DataFrame): The filtered DataFrame containing patient data.
    """
   # st.markdown("<div class='section-title'><b>Patient Trends Over Time</b></div>", unsafe_allow_html=True)

    # Group data by year and month, count number of patients
    monthly_patient_count = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Patient_Count')

    # Create line plot using Plotly
    patient_trend_fig = px.line(monthly_patient_count, x='Month', y='Patient_Count', color='Year',
                                title="Number of Patients per Month for Different Years",
                                labels={'Month': 'Month', 'Patient_Count': 'Number of Patients'})

    # Customize axis and plot appearance
    patient_trend_fig.update_layout(
        xaxis=dict(showline=True, showgrid=False, showticklabels=True, linecolor='black',
                   tickfont=dict(size=12, color='black')),
        yaxis=dict(showline=True, showgrid=False, showticklabels=True, linecolor='black',
                   tickfont=dict(size=12, color='black'))
    )

    # Display the line plot
    st.plotly_chart(patient_trend_fig)


def plot_cost_bubbles(filtered_df):
    hospital_min_cost_df = filtered_df.groupby(['Hospital Name', 'Year']).agg(Minimum_Cost=('cost', 'min')).reset_index()
    fig_min = px.scatter(hospital_min_cost_df,
                         x='Hospital Name', y='Year', size='Minimum_Cost', color='Hospital Name',
                         title="Bubble Chart of Minimum Cost per Hospital",
                         labels={'Minimum_Cost': 'Minimum Cost', 'Year': 'Year'}, size_max=60)
    st.plotly_chart(fig_min)

    hospital_max_cost_df = filtered_df.groupby(['Hospital Name', 'Year']).agg(Maximum_Cost=('cost', 'max')).reset_index()
    fig_max = px.scatter(hospital_max_cost_df,
                         x='Hospital Name', y='Year', size='Maximum_Cost', color='Hospital Name',
                         title="Bubble Chart of Maximum Cost per Hospital",
                         labels={'Maximum_Cost': 'Maximum Cost', 'Year': 'Year'}, size_max=60)
    st.plotly_chart(fig_max)


def plot_payment_method(filtered_df):
    payment_method_counts = filtered_df.groupby('payment_method')['patient_id'].count().reset_index()
    payment_method_counts.rename(columns={'patient_id': 'Total Patients'}, inplace=True)
    payment_method_counts['Percentage'] = (payment_method_counts['Total Patients'] / payment_method_counts['Total Patients'].sum()) * 100
    payment_method_counts['Display_Text'] = payment_method_counts.apply(lambda row: f"{row['Total Patients']} ({row['Percentage']:.2f}%)", axis=1)

    payment_method_bar = px.bar(payment_method_counts,
                                x='payment_method', y='Total Patients', color='payment_method', text='Display_Text',
                                title="Total Patients by Payment Method", color_discrete_sequence=px.colors.qualitative.Vivid)
    payment_method_bar.update_traces(texttemplate='%{text}', textposition='inside')
    payment_method_bar.update_layout(xaxis_title='Payment Method', yaxis_title='Total Patients', title_x=0, showlegend=False)
    st.plotly_chart(payment_method_bar)


def plot_patients_by_hospital(filtered_df):
    """
    Plots a bar chart showing the number of patients by Hospital Name along with total counts and percentages.

    Parameters:
    filtered_df (DataFrame): Filtered healthcare data
    """
    # Group by hospital name and count the number of patients
    hospital_patient_count = filtered_df.groupby('Hospital Name')['patient_id'].count().reset_index()

    # Rename columns for clarity
    hospital_patient_count.columns = ['Hospital Name', 'Patient Count']

    # Calculate percentage for each hospital
    total_patients = hospital_patient_count['Patient Count'].sum()
    hospital_patient_count['Percentage'] = (hospital_patient_count['Patient Count'] / total_patients) * 100

    # Plot the bar chart using Plotly Express with multi-colors
    fig = px.bar(hospital_patient_count,
                 x='Hospital Name',
                 y='Patient Count',
                 title='Number of Patients by Hospital',
                 labels={'Hospital Name': 'Hospital Name', 'Patient Count': 'Number of Patients'},
                 color='Hospital Name',  # For multi-color bars
                 text='Patient Count',  # Show the patient count on the bars
                 color_discrete_sequence=px.colors.qualitative.Vivid)

    # Add percentage as annotation on top of each bar
    for i, row in hospital_patient_count.iterrows():
        fig.add_annotation(
            x=row['Hospital Name'],
            y=row['Patient Count'],
            text=f"{row['Percentage']:.2f}%",  # Percentage with two decimal places
            showarrow=False,
            yshift=10,  # Move the text above the bar
            font=dict(color="black", size=12)
        )

    # Customize the layout
    fig.update_layout(
        xaxis_title="Hospital Name",
        yaxis_title="Number of Patients",
        xaxis_tickangle=-45,  # Rotate x-axis labels
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        uniformtext_minsize=8,  # Adjust text size for consistency
        uniformtext_mode='hide',  # Hide text if it doesn't fit
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)


def plot_patients_by_year(filtered_df):
    """
    Plots a bar chart showing the total number of patients each year, with a trend line.
    Each bar will have a different color.

    Parameters:
    filtered_df (DataFrame): Filtered healthcare data
    """
    # Group by year and count the number of patients
    yearly_patient_count = filtered_df.groupby('Year')['patient_id'].count().reset_index()

    # Rename columns for clarity
    yearly_patient_count.columns = ['Year', 'Patient Count']

    # Create the bar plot using Plotly Express with different colors for each bar
    fig = px.bar(yearly_patient_count,
                 x='Year',
                 y='Patient Count',
                 title='Total Number of Patients Each Year',
                 labels={'Year': 'Year', 'Patient Count': 'Number of Patients'},
                 text='Patient Count',  # Display patient count on top of bars
                 color='Year',  # Color based on year to get unique color for each bar
                 color_discrete_sequence=px.colors.qualitative.Pastel)  # Multi-color bars

    # Add the trend line (using Plotly Go for a linear regression line)
    fig.add_trace(
        go.Scatter(
            x=yearly_patient_count['Year'],
            y=yearly_patient_count['Patient Count'],
            mode='lines+markers',
            line=dict(color='firebrick', width=2),
            name='Trend Line'
        )
    )

    # Customize the layout to show text and adjust background colors
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Patients",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        uniformtext_minsize=8,  # Adjust text size for consistency
        uniformtext_mode='hide',  # Hide text if it doesn't fit
        showlegend=True  # Show the trend line in the legend
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)


def plot_top_5_diagnosis_by_patients(filtered_df):
    """
    Plots a bar chart showing the top 5 Diagnosis Names by total number of patients.

    Parameters:
    filtered_df (DataFrame): Filtered healthcare data
    """
    # Group by Diagnosis_Name and count the number of patients
    diagnosis_patient_count = filtered_df.groupby('Diagnosis_Name')['patient_id'].count().reset_index()

    # Rename columns for clarity
    diagnosis_patient_count.columns = ['Diagnosis_Name', 'Patient Count']

    # Sort the data to get the top 5 Diagnosis Names by patient count
    top_5_diagnoses = diagnosis_patient_count.nlargest(5, 'Patient Count')

    # Plot the bar chart using Plotly Express
    fig = px.bar(top_5_diagnoses,
                 x='Diagnosis_Name',
                 y='Patient Count',
                 title='Top 5 Diagnosis Names by Total Patients',
                 labels={'Diagnosis_Name': 'Diagnosis Name', 'Patient Count': 'Number of Patients'},
                 text='Patient Count',  # Display patient count on top of bars
                 color='Diagnosis_Name',  # Use different colors for each bar
                 color_discrete_sequence=px.colors.qualitative.Vivid)  # Multi-color bars

    # Customize the layout
    fig.update_layout(
        xaxis_title="Diagnosis Name",
        yaxis_title="Number of Patients",
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        showlegend=False  # Hide the legend (not necessary for a bar chart with 5 items)
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)



def plot_cost_vs_hospital_box(filtered_df):
    """
    Plots a box plot showing the distribution of cost across different hospital names.

    Parameters:
    filtered_df (DataFrame): Filtered healthcare data
    """
    # Ensure that the required columns are present in the DataFrame
    if 'Hospital Name' in filtered_df.columns and 'cost' in filtered_df.columns:
        # Plot the box plot using Plotly Express
        fig = px.box(filtered_df,
                     x='Hospital Name',
                     y='cost',
                     title='Cost Distribution Across Hospitals',
                     color='Hospital Name',  # Different colors for each hospital
                     color_discrete_sequence=px.colors.qualitative.Vivid,  # Use a vivid color palette
                     points="all")  # Show all points for more granular detail

        # Customize the layout
        fig.update_layout(
            xaxis_title="Hospital Name",
            yaxis_title="Cost",
            xaxis_tickangle=-45,  # Rotate x-axis labels for readability
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            showlegend=False  # Hide the legend (not needed for this plot)
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig)
    else:
        st.error("Required columns 'Hospital Name' and 'cost' are not available in the dataset.")
