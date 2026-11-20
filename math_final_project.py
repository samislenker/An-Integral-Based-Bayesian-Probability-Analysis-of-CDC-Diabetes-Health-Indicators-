# Import libraries
import pandas as pd

# Load csv as data frame
df_1 = pd.read_csv('diabetes_binary_health_indicators_BRFSS2015.csv')

# Create dataframe with the categories we are interested in 
df_sub = df_1[['Diabetes_binary', 'BMI', 'Age', 'HighBP', 'HighChol', 'Sex']]

# Group by age
def age_group(age):
    if 1 <= age <= 5:
        return 'Young Adult'
    elif 6 <= age <= 9:
        return 'Middle-Aged Adult'
    elif 10 <= age <= 13:
        return 'Older Adult'

# Create AgeGroup category
df_sub['AgeGroup'] = df_sub['Age'].apply(age_group)

# Group by BMI
def bmi_group(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi <= 24.9:
        return 'Healthy'
    elif 25 <= bmi <= 29.9:
        return 'Overweight'
    else:
        return 'Obese'


# Create BMIGroup category
df_sub['BMIGroup'] = df_sub['BMI'].apply(bmi_group)

OBSERVATIONS = df_sub.shape[0]
DIABETES = df_sub['Diabetes_binary'].mean()

# Create DataFrames
bmi_df = (
    df_sub.groupby('BMIGroup')['Diabetes_binary']
    .mean()
    .reset_index(name='Probability')
)

age_df = (
    df_sub.groupby('AgeGroup')['Diabetes_binary']
    .mean()
    .reset_index(name='Probability')
)

sex_df = (
    df_sub.groupby('Sex')['Diabetes_binary']
    .mean()
    .reset_index(name='Probability')
)

bp_df = (
    df_sub.groupby('HighBP')['Diabetes_binary']
    .mean()
    .reset_index(name='Probability')
)

chol_df = (
    df_sub.groupby('HighChol')['Diabetes_binary']
    .mean()
    .reset_index(name='Probability')
)


age_bmi_df = (
    df_sub.groupby(['AgeGroup', 'BMIGroup'])['Diabetes_binary']
    .mean()
    .unstack()
)

age_bmi_bp_df = (
    df_sub.groupby(['AgeGroup', 'BMIGroup', 'HighBP'])['Diabetes_binary']
    .mean()
    .unstack()
)

age_bmi_bp_chol_df = (
    df_sub.groupby(['AgeGroup', 'BMIGroup', 'HighBP', 'HighChol'])['Diabetes_binary']
    .mean()
    .unstack()
)


# Export
with pd.ExcelWriter('diabetes_probabilities_2.xlsx', engine='openpyxl') as writer:
    bmi_df.to_excel(writer, sheet_name='BMI Group', index=False)
    age_df.to_excel(writer, sheet_name='Age Group', index=False)
    sex_df.to_excel(writer, sheet_name='Sex', index=False)
    bp_df.to_excel(writer, sheet_name='Blood Pressure', index=False)
    chol_df.to_excel(writer, sheet_name='Cholesterol', index=False)
    age_bmi_df.to_excel(writer, sheet_name='Age x BMI')
    age_bmi_bp_df.to_excel(writer, sheet_name='Age x BMI x BP')
    age_bmi_bp_chol_df.to_excel(writer, sheet_name='Age x BMI x BP x CHOL')



