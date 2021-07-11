import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import urllib.request as urllib
#from urllib.request import urlopen
import pandas as pd
# import plotly.graph_objs as go
# import statsmodels.api as sm
import plotly.figure_factory as ff
import numpy as np
import gdown
import zipfile


url = 'https://drive.google.com/uc?id=1-s1881dNo8ksiRsBa_V18eEr6I4ckTdf'
path_to_zip_file = 'allfiles.zip'
gdown.download(url, path_to_zip_file, quiet=False)

with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
    zip_ref.extractall("data")

df_crime_t0 = pd.read_csv('data/df_crime_t0.csv').drop(columns=['StatZone','Year'])
df_crime_t1 = pd.read_csv('data/df_crime_t1.csv').drop(columns=['StatZone','Year'])
df_crime_2010_to_2015 = pd.read_csv('data/df_crime_2010_to_2015.csv')
df_conflicts_t0 = pd.read_csv('data/df_conflicts_t0.csv')
df_conflicts_t1 = pd.read_csv('data/df_conflicts_t1.csv')

df_salaries_t0 = pd.read_csv('data/df_salaries_t0.csv')
df_salaries_t1 = pd.read_csv('data/df_salaries_t1.csv')
df_haredim_t0 = pd.read_csv('data/df_haredim_t0.csv')
df_haredim_t1 = pd.read_csv('data/df_haredim_t1.csv')

df_seniors_t0 = pd.read_csv('data/df_seniors_t0.csv')
df_seniors_t1 = pd.read_csv('data/df_seniors_t1.csv')
df_holocaust_t0 = pd.read_csv('data/df_holocaust_t0.csv')
df_holocaust_t1 = pd.read_csv('data/df_holocaust_t1.csv')

df_main_dash = pd.DataFrame(columns=['Subject', 'Description', 'Value', 'Percent_comparison'])


def percentage_change(a, b):
    return round(100 * (b - a) / a, 2)


def add_row_to_main_dash(Subject: str, Description: str, t0_total, t1_total):
    global df_main_dash
    crime_sample = pd.Series([Subject, Description,
                              t1_total, percentage_change(t0_total, t1_total)], index=df_main_dash.columns)
    df_main_dash = df_main_dash.append(crime_sample, ignore_index=True)


def create_df_main_dash():
    # Crime || Total Crimes
    df_crime_t0['total_crimes'] = df_crime_t0.sum(axis=1)
    df_crime_t1['total_crimes'] = df_crime_t1.sum(axis=1)
    add_row_to_main_dash('Crime', 'Total Crimes in Current Semi-Year',
                         df_crime_t0['total_crimes'].sum(), df_crime_t1['total_crimes'].sum())

    # Population || Total Population
    add_row_to_main_dash('Demographics', 'Total Population',
                         int(df_salaries_t0['ResNum'].sum()), int(df_salaries_t1['ResNum'].sum()))

    # Population || Total Haredim
    add_row_to_main_dash('Demographics', 'Total Haredi Population',
                         int(df_haredim_t0['TotHaredim'].sum()), int(df_haredim_t1['TotHaredim'].sum()))

    # Income || Average Salary (Weighted sum of the five categories)
    Average_Salary_list = [0, 0]

    for i, df_salaries in enumerate([df_salaries_t0, df_salaries_t1]):
        df_salaries['ResNum_Salary'] = df_salaries['SalNoHKResNum'] + df_salaries['SalHKResNum'] + df_salaries[
            'SalPenResNum'] + df_salaries['SalSHNoBTLResNum'] + df_salaries['IncSelfResNum']
        df_salaries['weighted_salary'] = df_salaries.apply(
            lambda x: int((x.SalNoHKResNum / x.ResNum_Salary) * x.SalNoHKAve +
                          (x.SalHKResNum / x.ResNum_Salary) * x.SalHKAve +
                          (x.SalPenResNum / x.ResNum_Salary) * x.SalPenAve +
                          (x.SalSHNoBTLResNum / x.ResNum_Salary) * x.SalSHNoBTLAve +
                          (x.IncSelfResNum / x.ResNum_Salary) * x.IncSelfAve), axis=1)

        for ResNum, Salary in zip(df_salaries['ResNum_Salary'], df_salaries['weighted_salary']):
            Average_Salary_list[i] += (ResNum / (df_salaries['ResNum_Salary'].sum())) * Salary

    add_row_to_main_dash('Demographics', 'Average Salary', int(Average_Salary_list[0]), int(Average_Salary_list[1]))

    # Elderly || Senior Citizens || len(df_seniors)
    add_row_to_main_dash('Elderly', 'Number of Senior Citizens', len(df_seniors_t0), len(df_seniors_t0))

    # Elderly || Lone Senior Citizens
    add_row_to_main_dash('Elderly', 'Number of Lone Senior Citizens',
                         df_seniors_t0['SeniorAlone'].sum(), df_seniors_t1['SeniorAlone'].sum())

    # Elderly || Senior Citizens That Recieve Food ||
    add_row_to_main_dash('Elderly', 'Number of Recieving Food Senior Citizens',
                         df_seniors_t0['SeniorRecivFood'].sum(), df_seniors_t1['SeniorRecivFood'].sum())

    # Elderly || Holocaust Srvivors
    add_row_to_main_dash('Elderly', 'Number of Holocaust Srvivors', len(df_holocaust_t0), len(df_holocaust_t1))

    # Elderly || Unrecognized Holocaust Survivors ||
    add_row_to_main_dash('Elderly', 'Number of Unrecognized Holocaust Srvivors',
                         sum(df_holocaust_t0['HoloSurvKnwn'] == "לא מוכר"),
                         sum(df_holocaust_t1['HoloSurvKnwn'] == "לא מוכר"))


def main():
    create_df_main_dash()
    print('hi')


if __name__ == "__main__":
    main()
