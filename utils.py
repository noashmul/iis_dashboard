import plotly.graph_objects as go
import plotly.express as px
import numpy as np


# create global arguments
options_map = [{'label': ' שינוי באחוזים מהדו"ח הקודם ', 'value': 0}, {'label': ' ערכי הדו"ח הנוכחי', 'value': 1}]
stat_zones_names_dict = {
    611: "הדר מערב - רח' אלמותנבי",
    612: 'גן הבהאים',
    613: "הדר מערב - רח' מסדה",
    621: 'הדר עליון -בי"ח בני ציון',
    622: "הדר עליון - רח' הפועל",
    623: "רמת הדר - רח' המיימוני",
    631: 'הדר מרכז - התיאטרון העירוני',
    632: "הדר מרכז - רח' הרצליה",
    633: 'הדר מרכז - בית העירייה',
    634: 'הדר מרכז - שוק תלפיות',
    641: 'הדר מזרח - רח\' יל"ג',
    642: 'הדר מזרח - גאולה',
    643: "רמת ויז'ניץ",
    644: 'מעונות גאולה'
}
statistic_area = {'הכל': 0,
                  "הדר מערב - רח' אלמותנבי": 611,
                  'גן הבהאים': 612,
                  "הדר מערב - רח' מסדה": 613,
                  'הדר עליון -בי"ח בני ציון': 621,
                  "הדר עליון - רח' הפועל": 622,
                  "רמת הדר - רח' המיימוני": 623,
                  'הדר מרכז - התיאטרון העירוני': 631,
                  "הדר מרכז - רח' הרצליה": 632,
                  'הדר מרכז - בית העירייה': 633,
                  'הדר מרכז - שוק תלפיות': 634,
                  'הדר מזרח - רח\' יל"ג': 641,
                  'הדר מזרח - גאולה': 642,
                  "רמת ויז'ניץ": 643,
                  'מעונות גאולה': 644}
options = list()
for key, value in statistic_area.items():
    if key != 'הכל':
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + 'כל האזורים הסטטיסטיים',
                        'value': value})

# \U000025B2 and \U000025BC are up and down arrows
def add_annotations_to_fig(fig, x, y, percentage_change_value, old_y):
    """
    Adds annotations in (x_i, y_i) points for the given figure (figure should be bar plot, adds the text above the bar)

    :param fig: plotly figure
    :param x: list of x values
    :param y: corresponding y values to given x values
    :param percentage_change_value: the text values to annotate
    :param old_y: list with old values of y (to show the change),
    if there is no old_y value for some values than the corresponding value should be np.nan
    """
    up, down = "\U000025B2", "\U000025BC"
    percentage_change_value = [round(val, 1) if not np.isnan(val) else val for val in percentage_change_value]
    text = [((f'{up} +{val}%' if val > 0 else f'{down} {val}%') if val != 0 else f'{val}%') if not np.isnan(val) else ""
            for val in percentage_change_value]

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="text",
        text=text,
        textposition="top center",
        textfont=dict(
            family="sans serif",
            size=18,
            color="black"
        ),
        name='',
        customdata=[f'{int(old_y_i)}→{int(y_i)}' if (not np.isnan(old_y_i) and not np.isnan(y_i)) else ''
                    for old_y_i, y_i in zip(old_y, y)],
        hovertemplate='%{customdata}'
    ))


def create_horizontal_bar_plot_with_annotations(numeric_vals,  # x
                                                old_numeric_vals,  # old x
                                                category_vals,  # y
                                                percentage_change_value,  # pay attention to order
                                                title_text,
                                                text_offset_to_the_right,
                                                y_label_data=None,
                                                text_color='#252E3F',
                                                bar_color='#252E3F',
                                                annotations_text_size=18,
                                                titlefont_size=18,
                                                tickfont_size=18,
                                                tickangle=45,
                                                is_safety=False
                                                ):
    if is_safety:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=numeric_vals,
                y=category_vals,
                marker=dict(color=bar_color),
                name='',
                orientation='h',
                customdata=[
                    f'{int(old_y_i)}→{int(y_i)}<br>{hover}' if (not np.isnan(old_y_i) and not np.isnan(y_i)) else ''
                    for old_y_i, y_i, hover in zip(old_numeric_vals, numeric_vals, y_label_data)],
                hovertemplate='%{customdata}<br>'
            )
        )
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=numeric_vals,
                y=category_vals,
                marker=dict(color=bar_color),
                name='',
                orientation='h',
                customdata=[f'{int(old_y_i)}→{int(y_i)}' if (not np.isnan(old_y_i) and not np.isnan(y_i)) else ''
                            for old_y_i, y_i in zip(old_numeric_vals, numeric_vals)],
                hovertemplate='%{customdata}<br>'
            )
        )

    up, down = "\U000025B2", "\U000025BC"
    percentage_change_value = [round(val, 1) if not np.isnan(val) else val for val in percentage_change_value]
    percentage_change_value = [((f'{up} +{val}%' if val > 0 else f'{down} {val}%') if val != 0 else f'{val}%') if \
                                   not np.isnan(val) else "" for val in percentage_change_value]

    annotations = []

    for num, cat, text in zip(numeric_vals, category_vals, percentage_change_value):
        annotations.append(dict(xref='x1', yref='y1',
                                y=cat, x=num + text_offset_to_the_right,
                                text=text,
                                font=dict(size=annotations_text_size, color=text_color),
                                showarrow=False))
    fig.update_layout(annotations=annotations)

    fig.update_layout(title_text=title_text, title_x=0.5,
                      yaxis=dict(
                          titlefont_size=titlefont_size,
                          tickfont_size=tickfont_size,
                      ),
                      xaxis=dict(
                          titlefont_size=titlefont_size,
                          tickfont_size=tickfont_size,
                      ), xaxis_showgrid=True, yaxis_showgrid=True,
                      template='simple_white',
                      )
    if is_safety:
        fig.update_layout(barmode='stack', yaxis={'categoryorder': 'total descending'})
    fig.update_xaxes(tickangle=tickangle)

    return fig


if __name__ == "__main__":
    """Test the annotation function `add_annotations_to_fig`"""
    df = px.data.gapminder().query("continent == 'Europe' and year == 2007 and pop > 2.e6")
    fig = px.bar(df, y='pop', x=list(range(len(df))))
    # TODO add old_y to add_annotations_to_fig (see crime.py)
    add_annotations_to_fig(fig=fig, x=list(range(len(df))), y=list(df['pop']),
                           percentage_change_value=[100 * np.random.randn() for i in range(len(df))],
                           old_y=list(df['pop'] * np.random.randn()))
    fig.show()

    """Test the horizontal bar plot funciton"""
    fig = create_horizontal_bar_plot_with_annotations(
        numeric_vals=[93453.919999999998, 81666.570000000007, 69889.619999999995,
                      78381.529999999999, 141395.29999999999, 92969.020000000004,
                      66090.179999999993, 122379.3],
        old_numeric_vals=np.array([93453.919999999998, 81666.570000000007, 69889.619999999995,
                                   78381.529999999999, 141395.29999999999, 92969.020000000004,
                                   66090.179999999993, 122379.3]) * np.random.randn(),
        category_vals=['Japan', 'United Kingdom', 'Canada', 'Netherlands',
                       'United States', 'Belgium', 'Sweden', 'Switzerland'],
        percentage_change_value=[val * np.random.randn() for val in list(range(9))],
        title_text="HELLLLLO",
        text_offset_to_the_right=3000)
    fig.show()
