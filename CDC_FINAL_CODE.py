"""
Applied Math for Data Science - CDC Diabetes Project
Analysis of middle-aged adults (45-64) and BMI-related risk factors for diabetes.
"""

import csv
import math
import pandas as pd

#############################################################################
# CONSTANTS
#############################################################################
FILENAME = 'diabetes_binary_in_use.csv'
BMI_THRESHOLD = 30
summary_results = []

# -----------------------------
#############################################################################
# 1. CATEGORIZE AGE
#############################################################################
def categorize_age(age):
    age = int(float(age))

    if 1 <= age <= 5:
        return 1
    elif 6 <= age <= 9:
        return 2
    elif 10 <= age <= 13:
        return 3
    else:
        return None


#############################################################################
# 2. CREATE AGE GROUP CSV
#############################################################################

with open(FILENAME, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    with open('diabetes_age_groups.csv', 'w', newline='', encoding='utf-8') as output:
        fieldnames = ['BMI', 'Age', 'Age_Group', 'Diabetes_binary',
                      'HighBP', 'HighChol']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row['Age_Group'] = categorize_age(row['Age'])
            if row['Age_Group'] is not None and float(row['BMI']) > 0:
                writer.writerow({name: row[name] for name in fieldnames})

print('Age groups created successfully!')

#############################################################################
# 3. AGE GROUP ANALYSIS
#############################################################################
age_groups = {1: [], 2: [], 3: []}

with open('diabetes_age_groups.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        group = int(float(row['Age_Group']))
        age_groups[group].append(row)

age_details = []

for group, people in age_groups.items():
    total = len(people)
    if total == 0:
        continue

    bmi_values = pd.Series([float(person['BMI']) for person in people])
    average_bmi = bmi_values.mean()
    std_bmi = bmi_values.std()
    variance_bmi = bmi_values.var()
    diabetes_count = sum(int(float(person['Diabetes_binary'])) for person in people)
    percentage = (diabetes_count / total) * 100

    summary_results.append([
        'Age', group, total, round(average_bmi, 2),
        round(std_bmi, 2), round(variance_bmi, 2), diabetes_count, round(percentage, 2)
    ])
    age_details.append([
        group, total, round(average_bmi, 4), round(std_bmi, 4),
        round(variance_bmi, 4), diabetes_count, round(percentage, 4)
    ])

#############################################################################
# 4. CATEGORIZE BMI
#############################################################################
def categorize_bmi(bmi):
    bmi = float(bmi)

    if 0 <= bmi < 18.5:
        return 'underweight'
    elif bmi < 25:
        return 'healthy'
    elif bmi < 30:
        return 'overweight'
    else:
        return 'obese'


#############################################################################
# 5. BMI GROUP ANALYSIS
#############################################################################
bmi_groups = {
    'underweight': [], 'healthy': [], 'overweight': [], 'obese': []
}

with open('diabetes_age_groups.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        group = categorize_bmi(row['BMI'])
        bmi_groups[group].append(row)

for group, people in bmi_groups.items():
    total = len(people)
    if total == 0:
        continue

    bmi_values = pd.Series([float(person['BMI']) for person in people])
    average_bmi = bmi_values.mean()
    std_bmi = bmi_values.std()
    diabetes_count = sum(int(float(person['Diabetes_binary'])) for person in people)
    percentage = (diabetes_count / total) * 100

    summary_results.append([
        'BMI', group, total, round(average_bmi, 2),
        round(std_bmi, 2), round(bmi_values.var(), 2), diabetes_count, round(percentage, 2)
    ])

#############################################################################
# 6. CREATE ORIGINAL FINAL CSV
#############################################################################
category_map = {1: '18-44', 2: '45-64', 3: '65 or older'}

FEATUREMAP = {
    'Category': 'Group Name',
    'Total_Participants': 'Number of Participants',
    'Average_BMI': 'Mean BMI',
    'Standard_Deviation': 'BMI Standard Deviation',
    'Diabetes_Count': 'Diabetes Count',
    'Diabetes_Percentage': 'Positive Diabetes Percentage'
}

with open('diabetes_summary_renamed.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        FEATUREMAP['Category'], FEATUREMAP['Total_Participants'],
        FEATUREMAP['Average_BMI'], FEATUREMAP['Standard_Deviation'],
        FEATUREMAP['Diabetes_Count'], FEATUREMAP['Diabetes_Percentage']
    ])
    for row in summary_results:
        category = category_map.get(row[1], row[1])
        writer.writerow([category, row[2], row[3], row[4], row[5], row[6]])

#############################################################################
# 7. TOTAL GROUPS SUMMARY
#############################################################################
print('\nSummary successfully saved!')
print('Total groups saved:', len(summary_results))

#############################################################################
# 8. AGE GROUP STATISTICS (MEAN, SD, VARIANCE)
#############################################################################
with open('age_group_statistics.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Age Group', 'Participants', 'Mean BMI',
                     'BMI Standard Deviation', 'BMI Variance',
                     'Diabetes Count', 'Diabetes Percentage'])
    for row in age_details:
        writer.writerow([category_map[row[0]]] + row[1:])

#############################################################################
# 9. INTEGRAL / OBESITY PROBABILITY ANALYSIS
#############################################################################
'''
The normal tail calculation evaluates the normal-density integral from BMI = 30 to infinity using the standard normal distribution.
**math.erfc gives the upper-tail probability without needing scipy**
'''

with open('obesity_integral_results.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Age Group', 'Participants', 'Mean BMI', 'BMI SD',
                     'BMI Variance', 'Obese Count', 'Observed Obesity %',
                     'Normal Z Score', 'Normal Model Obesity %',
                     'Mean ln(BMI)', 'SD ln(BMI)', 'Log Normal Z Score',
                     'Log Normal Model Obesity %'])

    for group, people in age_groups.items():
        if len(people) < 2:
            continue
        bmi_values = pd.Series([float(person['BMI']) for person in people])
        mean_bmi = bmi_values.mean()
        std_bmi = bmi_values.std()
        variance_bmi = bmi_values.var()
        obese_count = sum(1 for bmi in bmi_values if bmi >= BMI_THRESHOLD)
        observed = obese_count / len(bmi_values) * 100

        z = (BMI_THRESHOLD - mean_bmi) / std_bmi
        normal_probability = 0.5 * math.erfc(z / math.sqrt(2)) * 100

        log_values = pd.Series([math.log(bmi) for bmi in bmi_values])
        log_mean = log_values.mean()
        log_std = log_values.std()
        log_z = (math.log(BMI_THRESHOLD) - log_mean) / log_std
        lognormal_probability = 0.5 * math.erfc(log_z / math.sqrt(2)) * 100

        writer.writerow([
            category_map[group], len(people), round(mean_bmi, 4),
            round(std_bmi, 4), round(variance_bmi, 4), obese_count,
            round(observed, 4), round(z, 6), round(normal_probability, 4),
            round(log_mean, 6), round(log_std, 6), round(log_z, 6),
            round(lognormal_probability, 4)
        ])
        print(f'Group {group}: observed obesity {observed:.2f}%, '
              f'normal {normal_probability:.2f}%, '
              f'log-normal {lognormal_probability:.2f}%')
        
#############################################################################
# 10. AGE + BMI DIABETES PREVALENCE 
#############################################################################
with open('diabetes_by_age_and_bmi.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Age Group', 'BMI Group', 'Participants',
                     'Diabetes Count', 'Diabetes Percentage'])
    for group, people in age_groups.items():
        for bmi_group in bmi_groups:
            selected = [person for person in people
                        if categorize_bmi(person['BMI']) == bmi_group]
            if len(selected) == 0:
                continue
            positive = sum(int(float(person['Diabetes_binary'])) for person in selected)
            writer.writerow([category_map[group], bmi_group, len(selected),
                             positive, round(positive / len(selected) * 100, 4)])

#############################################################################
# 11. MIDDLE-AGED (GROUP 2) ADULTS PARTICIPANTS (CSV)
#############################################################################
middle_age = age_groups[2]
with open('middle_age_participants.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['BMI', 'Age', 'Age_Group', 'Diabetes_binary',
                  'HighBP', 'HighChol']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for person in middle_age:
        writer.writerow(person)

#############################################################################
# 12. MIDDLE-AGED (GROUP 2) ADULT RISK-FACTOR GROUPS
#############################################################################
'''Each row represents one combination of blood pressure and cholesterol. The BMI model is fitted separately within each combination.'''

with open('middle_age_risk_factors.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Age Group', 'HighBP', 'HighChol', 'Participants',
                     'Mean BMI', 'BMI SD', 'BMI Variance',
                     'Obese Count', 'Observed Obesity %',
                     'Normal Model Obesity %', 'Log Normal Model Obesity %',
                     'Diabetes Count', 'Diabetes Percentage'])

    for bp in [0, 1]:
        for chol in [0, 1]:
            selected = [person for person in middle_age
                        if int(float(person['HighBP'])) == bp
                        and int(float(person['HighChol'])) == chol]
            if len(selected) < 2:
                continue

            bmi_values = pd.Series([float(person['BMI']) for person in selected])
            mean_bmi = bmi_values.mean()
            std_bmi = bmi_values.std()
            variance_bmi = bmi_values.var()
            obese_count = sum(1 for bmi in bmi_values if bmi >= BMI_THRESHOLD)
            observed = obese_count / len(selected) * 100
            z = (BMI_THRESHOLD - mean_bmi) / std_bmi
            normal = 0.5 * math.erfc(z / math.sqrt(2)) * 100

            log_values = pd.Series([math.log(bmi) for bmi in bmi_values])
            log_mean = log_values.mean()
            log_std = log_values.std()
            log_z = (math.log(BMI_THRESHOLD) - log_mean) / log_std
            lognormal = 0.5 * math.erfc(log_z / math.sqrt(2)) * 100
            diabetes_count = sum(int(float(person['Diabetes_binary']))
                                 for person in selected)

            writer.writerow([
                '45-64', bp, chol, len(selected), round(mean_bmi, 4),
                round(std_bmi, 4), round(variance_bmi, 4), obese_count,
                round(observed, 4), round(normal, 4), round(lognormal, 4),
                diabetes_count, round(diabetes_count / len(selected) * 100, 4)
            ])

#############################################################################
# 13. DIABETES PREVALENCE FOR OBESE MIDDLE-AGED ADULTS (GROUP 2)
#############################################################################

with open('middle_age_obese_diabetes_risk.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Age Group', 'BMI Group', 'HighBP', 'HighChol',
                     'Participants', 'Diabetes Count',
                     'Diabetes Percentage'])

    for bp in [0, 1]:
        for chol in [0, 1]:
            selected = [person for person in middle_age
                        if float(person['BMI']) >= BMI_THRESHOLD
                        and int(float(person['HighBP'])) == bp
                        and int(float(person['HighChol'])) == chol]
            if len(selected) == 0:
                continue
            positive = sum(int(float(person['Diabetes_binary']))
                           for person in selected)
            writer.writerow(['45-64', 'obese', bp, chol, len(selected),
                             positive, round(positive / len(selected) * 100, 4)])

#############################################################################
# 14. BAYES' THEOREM INPUTS FOR MIDDLE-AGED (GROUP 2) ADULTS 
#############################################################################
'''Observed probabilities are calculated from the survey counts where P(D | obese) = P(obese | D) * P(D) / P(obese)'''

with open('middle_age_bayes_inputs.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['HighBP', 'HighChol', 'Participants',
                     'Diabetes Count', 'Obese Count', 'Obese and Diabetes Count',
                     'P(D)', 'P(Obese)', 'P(Obese given D)',
                     'P(D given Obese) - Bayes', 'Observed P(D given Obese)'])

    for bp in [0, 1]:
        for chol in [0, 1]:
            selected = [person for person in middle_age
                        if int(float(person['HighBP'])) == bp
                        and int(float(person['HighChol'])) == chol]
            total = len(selected)
            if total == 0:
                continue
            positive = sum(int(float(p['Diabetes_binary'])) for p in selected)
            obese = sum(1 for p in selected if float(p['BMI']) >= BMI_THRESHOLD)
            both = sum(1 for p in selected
                       if float(p['BMI']) >= BMI_THRESHOLD
                       and int(float(p['Diabetes_binary'])) == 1)
            prior = positive / total
            p_obese = obese / total
            likelihood = both / positive if positive > 0 else 0
            bayes = likelihood * prior / p_obese if p_obese > 0 else 0
            observed = both / obese if obese > 0 else 0
            writer.writerow([bp, chol, total, positive, obese, both,
                             round(prior, 6), round(p_obese, 6),
                             round(likelihood, 6), round(bayes, 6),
                             round(observed, 6)])

print('\nAll CSV files created successfully!')
