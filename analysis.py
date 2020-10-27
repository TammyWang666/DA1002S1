import pandas as pd
from numpy import nan as NA
# dataset 1
population = pd.read_csv('D1_population_by_lga.csv')
# dataset 2
aged_percentage = pd.read_csv('D2_Age_Summary_by_lga.csv')
# dataset 3
confirmed_cases = pd.read_csv('D3_confirmed_cases_by_lga_postcode.csv')
# print(population.size)
# print(aged_percentage.size)
# print(aged_percentage.size)

# select target attributes from dataset 1, regional population
density_df = population.iloc[:,[-1,0,1,-2]]
density_df.columns = ['State', 'LGA code', 'Local Government Area', 'Population Density']
# Check and remove null values for dataset 1, State value cannot be null and density cannot be 0
density_df = density_df[density_df['State'] == 'NSW']
density_df = density_df[density_df['Population Density'] != 0]
density_df.dropna()
print("Check if dataset 1 have nulls", density_df.isnull().any())
#print(density_df)

# select target attributes from dataset 2, age summary of regional population 
aged_df = aged_percentage.iloc[:,[1,2,3,-1]]
# Unify names as different datasets may have different column names for the same attribute
# Unify representations while dataset 2 use for form for state 'New South Wales' while dataset 1 uses 'NSW'
aged_df.columns = ['State', 'LGA code', 'Local Government Area', 'Percentage of The Aged']
# Transform data formats
aged_df["State"].replace({"New South Wales": "NSW"}, inplace=True)
# Check and remove null values for dataset 1, State value cannot be null and density cannot be 0
aged_df = aged_df[aged_df['State'] == 'NSW']
aged_df.dropna()
print("Check if dataset 2 have nulls", aged_df.isnull().any())
#print(aged_df)

# select target attributes from dataset 3, confirmed cases by date and location
cases_df = confirmed_cases.iloc[:,[0,1,-2,-1]]
# Unify names as different datasets may have different column names for the same attribute
# for instance, dataset 3 use 'lga_name19' for the 'Local Government Area' attribute in dataset 1
cases_df.columns = ['Date', 'Post Code', 'LGA code','Local Government Area']
# Check and remove null values for rows that are meaningless
cases_df.dropna(how = 'any')
# fill in missing values and transform data formats
cases_df["Post Code"].replace({NA: "Unknown"}, inplace=True)
cases_df["LGA code"].replace({NA: "Unknown"}, inplace=True)
cases_df['Local Government Area'].replace({NA: "Unknown"}, inplace=True)
print("Check if dataset 3 have nulls",cases_df.isnull().any())
#print(cases_df)


# Merge dataset by Local Government Area
cases_density_df = pd.merge(cases_df, density_df, on = 'Local Government Area', how = 'outer')
result_df = pd.merge(cases_density_df, aged_df, on = 'Local Government Area', how = 'outer')


# Remove duplicates if there is any
result_df = result_df.iloc[:,[0,1,8,3,4,6,9]]
result_df.columns = ['Date', 'Post Code', 'LGA code', 'Local Government Area','State', 'Population Density', 'Percentage of The Aged']
print("Check if result dataset have nulls in LGA", result_df['Local Government Area'].isnull().any())
# fill in missing values for areas in NSW but without state value
result_df['State'].replace({NA: "NSW"}, inplace=True)
result_df["Post Code"].replace({NA: "Unknown"}, inplace=True)
result_df["LGA code"].replace({NA: "Unknown"}, inplace=True)
result_df["Date"].replace({NA: "Unknown"}, inplace=True)
# Remove null values for computation
result_df = result_df[result_df['Population Density'] != NA]
result_df = result_df[result_df['Percentage of The Aged'] != NA]
# Transform data formats
result_df['Population Density'] = result_df['Population Density'].astype(float)
result_df['Percentage of The Aged'] = result_df['Percentage of The Aged'].astype(float)
# Checking for quality verification
print("Check if result dataset have nulls after filling missing values", result_df.isnull().any())
#print(result_df)
# Output clean data
# print(population.head())
# print(aged_percentage.head())
# print(confirmed_cases.head())
# print(result_df.head())
result_df.to_csv('result.csv')

# number of cases, Group by Local Government Area
counts_by_LGA = result_df.groupby(by = 'Local Government Area').size().to_dict()
print("========== The number of cases grouped by Local Government Area are: ==========")
for k in counts_by_LGA:
    print(k, counts_by_LGA[k])
print()

# highest number of cases, Group by Local Government Area, excluding unknown cases
df = result_df[result_df['Local Government Area'] != 'Unknown']
cases_by_LGA_without_unknown = df.groupby(by = 'Local Government Area').size().to_dict()
largest = None
area_with_most_cases = None
for LGA in cases_by_LGA_without_unknown:
    if largest is None or largest < cases_by_LGA_without_unknown[LGA]:
        area_with_most_cases = LGA
        largest = cases_by_LGA_without_unknown[LGA]
print("The Local Government Area with highest number of cases is:")
print(area_with_most_cases, largest)
print()

# Average number of cases, which are Grouped by density and Local Government Area
# denstity is splitted into 3 groups, excluding unknown cases
highestD = df['Population Density'].max()
lowestD = df['Population Density'].min()
crowed_density = lowestD + (highestD - lowestD)*0.6667
safe_density = lowestD + (highestD - lowestD)*0.3333
cases_in_most_crowed = df[df['Population Density'] > crowed_density].groupby(by = 'Local Government Area').size().mean()
cases_in_crowed = df[df['Population Density'] <= crowed_density]
cases_in_moderately_crowed = cases_in_crowed[cases_in_crowed['Population Density'] >= safe_density].groupby(by = 'Local Government Area').size().mean()
cases_in_less_crowed_area = cases_in_crowed[cases_in_crowed['Population Density'] < safe_density].groupby(by = 'Local Government Area').size().mean()
print('========== Average number of cases, grouped by density and Local Government Area are: ==========')
print('The most crowed area have an average cases of',cases_in_most_crowed)
print('The moderately crowed area have an average cases of',cases_in_moderately_crowed)
print('The less crowed area have an average cases of',cases_in_less_crowed_area)
print()

# Local Government Area that needs special care using Number of cases and aging population percentage
# Average number of cases, are Grouped by percentage of the olderly and Local Government Area
# Aging percentage is splitted into 3 groups, excluding unknown cases
highestP = df['Percentage of The Aged'].max()
lowestP = df['Percentage of The Aged'].min()
dangerous = lowestP + (highestP - lowestP)*0.75
relatively_dangerous = lowestP + (highestD - lowestD)*0.5
relatively_safe = lowestP + (highestD - lowestD)*0.25

cases_in_danger_by_LGA = df[df['Percentage of The Aged'] > dangerous].groupby(by = 'Local Government Area').size().to_dict()
print('The areas that needs special are to the elderly are:')
for k in cases_in_danger_by_LGA:
    print(k, cases_in_danger_by_LGA[k])
print()
cases_in_q1 = df[df['Percentage of The Aged'] > dangerous].groupby(by = 'Local Government Area').size().mean()
cases_in_q234 = df[df['Percentage of The Aged'] <= crowed_density]
cases_in_q2 = cases_in_q234[cases_in_q234['Population Density'] > relatively_dangerous].groupby(by = 'Local Government Area').size().mean()
cases_in_q34 = result_df[result_df['Percentage of The Aged'] <= relatively_dangerous]
cases_in_q3 = cases_in_q34[cases_in_q34['Population Density'] > relatively_safe].groupby(by = 'Local Government Area').size().mean()
cases_in_q4 = df[df['Percentage of The Aged'] < relatively_safe].groupby(by = 'Local Government Area').size().mean()
print('========== Average number of cases, grouped by percentage of the elderly and Local Government Area are: ==========')
print('The areas with most aging population have an average cases of', cases_in_q1)
print('The areas with moderately aging population have an average cases of', cases_in_q2)
print('The areas with moderately less aging population have an average cases of', cases_in_q3)
print('The areas with less aging population have an average cases of', cases_in_q4)
print()
# Month with highest Number of cases, using Group by month, including unknown cases
# number of cases, Group by month
cases_df = result_df[result_df['Date'] != 'Unknown']
month_df = cases_df.iloc[:,[0,3]]
month_df['Date'] = cases_df['Date'].apply(lambda x : x.split('-')[1])
counts_by_month = month_df.groupby('Date').size().to_dict()
print("========== The number of cases grouped by month are: ==========")
for k in counts_by_month:
    print(k, counts_by_month[k])

largest = None
month_with_most_cases = None
for month in counts_by_month:
    if largest is None or largest < counts_by_month[month]:
        month_with_most_cases = month
        largest = counts_by_month[month]
print("========== The month with highest number of cases is: ===========")
print('Month', month_with_most_cases, 'with number of cases as',largest)
print()