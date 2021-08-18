import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

##### RUN DATA ANALYSIS #####

# creates an empty dictionary
states_numbered = {}

# list of state abbreviations sorted alphabetically by full state name
states_abrev = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

# list of states sorted alphabetically
states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
          "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
          "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
          "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
          "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
          "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
          "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
          "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
          "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
          "Wisconsin", "Wyoming"]

# fills the empty dictionary, states_numbered,
# so that it has the number a state appears alphabetically as the key
# and a list of the abbreviation and full name as the value
for i in range(50):
    states_numbered[i + 1] = [states_abrev[i], states[i]]

# define a function that will take the state name or abbreviation and return
# the resulting key that holds the number in which it appears alphabetically
def get_key(val):
    for key, value in states_numbered.items():
         if val in value:
             return key

# import minimum wage data from csv file
minwagedf = pd.read_csv("Minimum_Wage_Data.csv", encoding='cp1252')

# restrict minimum wage data so that the year is between 2005 and 2019
# because the data in the suicide rate data frame only holds those years
minwagedf = minwagedf[(minwagedf['Year'] >= 2005) & (minwagedf['Year'] <= 2019)]

# drop column that holds unnecessary data
minwagedf = minwagedf.drop('Footnote', axis= 1)

# import suicide rate data from csv
sratedf = pd.read_csv("csv.csv")

# drop column that holds unnecessary data
sratedf = sratedf.drop('URL',axis=1)

# drop last row of sratedf because it holds only nan
sratedf = sratedf[:-1]

# convert YEAR from float to int so that it can be worked with accordingly
sratedf.YEAR = sratedf.YEAR.astype(int)

# within minwagedf dataframe, for each row, if the State is not a valid state
# then remove that row from the dataset
for i in minwagedf['State']:
    if i not in states:
        minwagedf = minwagedf.drop(index = minwagedf[minwagedf['State']== i].index.values)

# Check if any state not found in typical state list
# if a state is found that is not valid, it will be printed out in the list useless_states
useless_states = []
for i in minwagedf['State'].to_list():
    if i not in states_abrev and i not in states:
        if i not in useless_states:
            useless_states.append(i)
print(useless_states)

# within sratedf dataframe, for each row, if the State is not a valid state
# then remove that row from the dataset
for i in sratedf['STATE']:
    if i not in states_abrev:
        sratedf = sratedf.drop(index = sratedf[sratedf['STATE']== i].index.values)

#Check if any states not found in typical state list
# if a state is found that is not valid, it will be printed out in the list useless_states
useless_states = []
for i in sratedf['STATE'].to_list():
    if i not in states_abrev and i not in states:
        if i not in useless_states:
            useless_states.append(i)
print(useless_states)

# adds unique ID based on year and state number to minwagedf
minwagedf['state_num'] = minwagedf.apply(lambda row: get_key(row.State), axis=1)
minwagedf['unique_id'] = minwagedf.apply(lambda row: str(get_key(row.State)) + str(row.Year), axis=1)

# adds unique ID based on year and state number to sratedf
sratedf['state_num'] = sratedf.apply(lambda row: get_key(row.STATE), axis=1)
sratedf['unique_id'] = sratedf.apply(lambda row: str(get_key(row.STATE)) + str(row.YEAR), axis=1)

# merge together minwagedf and sratedf into df_merged
# use an inner merge because we want to look at the relationship between wages
# and suicide, and do not care as much for when the data does not coincide
df_merged = pd.merge(minwagedf, sratedf, left_on='unique_id', right_on='unique_id', how='inner')

# Checking For na values - will print out the name of each row
# and T/F whether na exists in the row
print(df_merged.isna().any())
# result is that it prints out all Falses, meaning that there are no nan in the data

# get df_merged down to only the columns that we are interested in
df_merged = df_merged[['unique_id', 'Year','STATE','Effective.Minimum.Wage', 'Effective.Minimum.Wage.2020.Dollars','Federal.Minimum.Wage', 'Federal.Minimum.Wage.2020.Dollars','CPI.Average','RATE','DEATHS']]

# change DEATHS from an object to a float so that it can be worked with and analyzed
df_merged['DEATHS'] = df_merged['DEATHS'].str.replace(',', '').astype(float)

# variables we are interested in
important = ['Effective.Minimum.Wage', 'Effective.Minimum.Wage.2020.Dollars','Federal.Minimum.Wage', 'Federal.Minimum.Wage.2020.Dollars','CPI.Average','RATE','DEATHS']

# create a heatmap of the variables we are interested in
# from mimum wage and suicide rate data
sns.heatmap(df_merged[important].corr(),
annot = True, fmt = '.2g', vmin=-1, vmax=1,center=0,linewidths=2, cmap = 'cool',
mask = np.triu(df_merged[important].corr()))
plt.xticks(rotation=81)
plt.grid(axis='both', alpha = 0.1)
plt.title("Federal Minimum Wage & Suicide Rates")

# the rows labelled RATE and DEATHS that come from the suicide rates data
# do not have strong correlation factors with the other data points, therefore
# the map reveals that minimum wage and suicide rates were not very correlated

# create scatter matrix of the variables we are interested in
# from mimum wage and suicide rate data
matrix = pd.plotting.scatter_matrix(df_merged[important],
figsize=(9.5,8), diagonal='kde')
for ax in matrix.flatten():
    ax.xaxis.label.set_rotation(81)
    ax.yaxis.label.set_rotation(0)
    ax.yaxis.label.set_ha('right')
plt.suptitle('scatter-matrix')
# this also shows that the suicide rate data was not particularly correlated
# with minimum wage data

#### DEFINE CODE FOR STREAMLIT #####

# create an introduction to our project
def introduction():
    st.title("MA 346 Final Project")
    st.write('--------------')
    st.header("**Introduction to the data sets:**")
    st.write("**Purpose**: Perform data anaylsis on minimum wage and suicide data.")
    st.write("**Group Members:** *Cassie Butch & Kevin Troncoso*")
    st.write("**Table Contents:** ")
    st.write("*1.) CPI.Average* - average consumer price index for country - a measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services")
    st.write("*2.) DEATHS* - suicide-related deaths in a state")
    st.write("*3.) Effective.Minimum.Wage* - the minimum wage in place in a state")
    st.write("*4.) Effective.Minimum.Wage.2020.Dollars* - the minimum wage in place in a state trended for inflation to 2020 dollars")
    st.write("*5.) Federal.Minimum.Wage* - the federally mandated minimum wage")
    st.write("*6.) Federal.Minimum.Wage* - the federally mandated minimum wage trended for inflation to 2020 dollars")
    st.write("*7.) RATE* - suicide rate for a state")
    st.write("*8.) Year* - year of data")

# create slider for selecting year
def slider():
    year = st.sidebar.slider("Input desired year range", 2005, 2019, value=[2005, 2019])
    year_1 = year[0]
    year_2 = year[1]
    return year_1, year_2

# create sidebar
def Options():
    st.sidebar.header("Correlation Plot")
    x_sel = st.sidebar.selectbox('Input desired x-value from minimum wage data', ['Effective.Minimum.Wage', 'Effective.Minimum.Wage.2020.Dollars','Federal.Minimum.Wage', 'Federal.Minimum.Wage.2020.Dollars','CPI.Average'])
    y_sel = st.sidebar.selectbox('Input desired y-value from suicide data', ['RATE', 'DEATHS'])
    st.sidebar.write('--------------')
    st.sidebar.header("Selected Dataset")
    State = st.sidebar.selectbox('Input desired state', states_abrev)
    Year_1, Year_2 = slider()
    # return each of the outputs that come from the selections of the slider
    return x_sel, y_sel, State, Year_1, Year_2

def main():
    # call necessary defined functions
    introduction()
    st.write('--------------')
    x_sel, y_sel, State, Year_1, Year_2 = Options()

    st.header("**Complete Dataset:**")
    st.write(df_merged.pivot_table(index='unique_id'))

    st.subheader("Summary")
    st.write(df_merged.describe())

    # create a figure that uses x_sel and y_sel to graph a plot of the selected variables
    # can be used to show their correlations
    st.write('--------------')
    st.header("**Selected Correlation Plot**")
    sns.set()
    fig1,ax = plt.subplots()
    ax.plot(df_merged[x_sel], df_merged[y_sel], "o")
    x = np.array(df_merged[x_sel].tolist())
    y = np.array(df_merged[y_sel].tolist())
    m, b = np.polyfit(x, y, 1)
    ax.plot(x, x*m + b, label=f"y = {m:.2f}x + {b:.2f}")
    ax.set_ylabel(y_sel)
    ax.set_xlabel(x_sel)
    ax.set_title(y_sel+" vs. "+x_sel)
    st.pyplot(fig1)

    st.write('--------------')

    # display the data based on selections
    st.header("**Selected Dataset Suicide Rate vs Effective Minimum Wage:**")
    selected = df_merged[df_merged['STATE']==State]
    st.write("For "+State+" from "+str(Year_1)+" to "+str(Year_2)+":")
    selected_w_yr = selected[(selected['Year']>=Year_1) & (selected['Year']<=Year_2)]
    st.set_option('deprecation.showPyplotGlobalUse', False)
    if selected_w_yr.empty:
        st.write("No valid data for selected range. Please select years again.")
    else:
        st.write(selected_w_yr.pivot_table(index='unique_id'))
        sns.set()
        selected_w_yr.pivot_table(index=['Year'], values=['RATE', 'Effective.Minimum.Wage']).plot(
            kind='line')
        plt.legend(['Suicide Rate','Effective Minimum Wage'])
        st.pyplot()
        plt.xlabel("Year")
    st.set_option('deprecation.showPyplotGlobalUse', False)

# call main streamlit function
main()
