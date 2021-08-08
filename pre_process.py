import pandas as pd


def percentage_change(a, b):
    return round(100 * (b - a) / a, 2)


def add_row_to_main_dash(df_main_dash, Subject: str, Description: str, t0_total, t1_total):
    crime_sample = pd.Series([Subject, Description,
                              t1_total, percentage_change(t0_total, t1_total)], index=df_main_dash.columns)
    df_main_dash = df_main_dash.append(crime_sample, ignore_index=True)
    return df_main_dash


def create_df_main_dash(d: dict):
    """
    Create a table for the main tab of the dashboard
    :param d: dfs_dict
    """
    df_main_dash = pd.DataFrame(columns=['נושא', 'תיאור', 'ערך', 'אחוז שינוי מהדו"ח הקודם'])

    # Crime || Total Crimes
    d['df_crime_t0']['total_crimes'] = d['df_crime_t0'].drop(columns=['StatZone', 'Year']).sum(axis=1)
    d['df_crime_t1']['total_crimes'] = d['df_crime_t1'].drop(columns=['StatZone', 'Year']).sum(axis=1)
    df_main_dash = add_row_to_main_dash(df_main_dash, 'פשיעה', 'סה"כ מספר פשעים בשכונה',
                                        d['df_crime_t0']['total_crimes'].sum(), d['df_crime_t1']['total_crimes'].sum())

    # Population || Total Population
    df_main_dash = add_row_to_main_dash(df_main_dash, 'דמוגרפיה', 'גודל אוכלוסיה כוללת',
                                        int(d['df_salaries_t0']['ResNum'].sum()),
                                        int(d['df_salaries_t1']['ResNum'].sum()))

    # Population || Total Haredim
    df_main_dash = add_row_to_main_dash(df_main_dash, 'דמוגרפיה', 'גודל אוכלוסיה חרדית',
                                        int(d['df_haredim_t0']['TotHaredim'].sum()),
                                        int(d['df_haredim_t1']['TotHaredim'].sum()))

    # Income || Average Salary (Weighted sum of the five categories)
    Average_Salary_list = [0, 0]

    for i, df_salaries in enumerate([d['df_salaries_t0'], d['df_salaries_t1']]):
        df_salaries['ResNum_Salary'] = df_salaries['SalNoHKResNum'] + df_salaries['SalHKResNum'] + \
                                       df_salaries['SalPenResNum'] + df_salaries['SalSHNoBTLResNum'] + df_salaries[
                                           'IncSelfResNum']
        df_salaries['weighted_salary'] = df_salaries.apply(
            lambda x: int((x.SalNoHKResNum / x.ResNum_Salary) * x.SalNoHKAve +
                          (x.SalHKResNum / x.ResNum_Salary) * x.SalHKAve +
                          (x.SalPenResNum / x.ResNum_Salary) * x.SalPenAve +
                          (x.SalSHNoBTLResNum / x.ResNum_Salary) * x.SalSHNoBTLAve +
                          (x.IncSelfResNum / x.ResNum_Salary) * x.IncSelfAve), axis=1)

        for ResNum, Salary in zip(df_salaries['ResNum_Salary'], df_salaries['weighted_salary']):
            Average_Salary_list[i] += (ResNum / (df_salaries['ResNum_Salary'].sum())) * Salary

    df_main_dash = add_row_to_main_dash(df_main_dash, 'הכנסה', 'שכר ממוצע', int(Average_Salary_list[0]),
                                        int(Average_Salary_list[1]))

    # Elderly || Senior Citizens || len(df_seniors)
    df_main_dash = add_row_to_main_dash(df_main_dash, 'קשישים', 'סה"כ אזרחים ותיקים', len(d['df_seniors_t0']),
                                        len(d['df_seniors_t0']))

    # Elderly || Lone Senior Citizens
    df_main_dash = add_row_to_main_dash(df_main_dash, 'קשישים', 'סה"כ אזרחים ותיקים בודדים',
                                        d['df_seniors_t0']['SeniorAlone'].sum(),
                                        d['df_seniors_t1']['SeniorAlone'].sum())

    # Elderly || Senior Citizens That Recieve Food ||
    df_main_dash = add_row_to_main_dash(df_main_dash, 'קשישים', 'סה"כ אזרחים ותיקים מקבלי מזון',
                                        d['df_seniors_t0']['SeniorRecivFood'].sum(),
                                        d['df_seniors_t1']['SeniorRecivFood'].sum())

    # Elderly || Holocaust Srvivors
    df_main_dash = add_row_to_main_dash(df_main_dash, 'קשישים', 'סה"כ ניצולי שואה',
                                        len(d['df_holocaust_t0']), len(d['df_holocaust_t1']))

    # Elderly || Unrecognized Holocaust Survivors ||
    df_main_dash = add_row_to_main_dash(df_main_dash, 'קשישים', 'סה"כ ניצולי שואה לא מוכרים',
                                        sum(d['df_holocaust_t0']['HoloSurvKnwn'] == "לא מוכר"),
                                        sum(d['df_holocaust_t1']['HoloSurvKnwn'] == "לא מוכר"))

    return df_main_dash


def create_dfs_dict():
    df_crime_t0 = pd.read_csv('data/df_crime_t0.csv')
    df_crime_t1 = pd.read_csv('data/df_crime_t1.csv')
    df_crimes_cases_t0 = pd.read_csv('data/df_crimes_cases_t0.csv')
    df_crimes_cases_t1 = pd.read_csv('data/df_crimes_cases_t1.csv')
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

    df_106_t0 = pd.read_csv('data/df_106_t0.csv')
    df_106_t1 = pd.read_csv('data/df_106_t1.csv')

    df_cameras_t0 = pd.read_csv('data/df_cameras_t0.csv')
    df_cameras_t1 = pd.read_csv('data/df_cameras_t1.csv')

    df_aband_t0 = pd.read_csv('data/df_aband_t0.csv')
    df_aband_t1 = pd.read_csv('data/df_aband_t1.csv')

    dfs_dict = {'df_crime_t0': df_crime_t0, 'df_crime_t1': df_crime_t1,
                'df_crimes_cases_t0': df_crimes_cases_t0, 'df_crimes_cases_t1': df_crimes_cases_t1,
                'df_conflicts_t0': df_conflicts_t0, 'df_conflicts_t1': df_conflicts_t1,
                'df_salaries_t0': df_salaries_t0, 'df_salaries_t1': df_salaries_t1,
                'df_haredim_t0': df_haredim_t0, 'df_haredim_t1': df_haredim_t1,
                'df_seniors_t0': df_seniors_t0, 'df_seniors_t1': df_seniors_t1,
                'df_holocaust_t0': df_holocaust_t0, 'df_holocaust_t1': df_holocaust_t1,
                'df_106_t0': df_106_t0, 'df_106_t1': df_106_t1,
                'df_cameras_t0': df_cameras_t0, 'df_cameras_t1': df_cameras_t1,
                'df_aband_t0': df_aband_t0, 'df_aband_t1': df_aband_t1}

    dfs_dict = add_row_to_missing_stat_zones(dfs_dict)
    return dfs_dict


def add_row_to_missing_stat_zones(dfs_dict):
    for df in ['df_holocaust_t0', 'df_holocaust_t1']:
        set_of_zones = list(set(dfs_dict[df].StatZone))
        for statzone in list(set(dfs_dict['df_salaries_t0'].StatZone)):
            if statzone not in set_of_zones:
                new_row = dfs_dict[df].sample(n=1)
                new_row['StatZone'] = statzone
                dfs_dict[df] = dfs_dict[df].append(new_row)

    if df in ['df_holocaust_t0', 'df_holocaust_t1']:
        for statzone in list(set(dfs_dict[df].StatZone)):
            set_of_helps = dfs_dict[df][dfs_dict[df]['StatZone'] == statzone]['HoloSurvNdDesc']
            while len(set_of_helps) == set_of_helps.isna().sum():
                new_row = dfs_dict[df].sample(n=1)
                new_row['StatZone'] = statzone
                dfs_dict[df] = dfs_dict[df].append(new_row)
                set_of_helps = dfs_dict[df][dfs_dict[df]['StatZone'] == statzone]['HoloSurvNdDesc']
    return dfs_dict


def main():
    dfs_dict = create_dfs_dict()


global dfs_dict
dfs_dict = create_dfs_dict()

if __name__ == "__main__":
    main()
