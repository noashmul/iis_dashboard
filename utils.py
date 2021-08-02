import plotly.graph_objects as go
import plotly.express as px
import numpy as np


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
    text = [(f'{up} +{val}%' if val > 0 else f'{down} {val}%') if not np.isnan(val) else ""
            for val in percentage_change_value]

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="text",
        text=text,
        textposition="top center",
        textfont=dict(
            family="sans serif",
            size=18,  # TODO make sure this is good to all the graphs
            color="black"
        ),
        name='',
        customdata=[f'{int(old_y_i)}>>{int(y_i)}' if (not np.isnan(old_y_i) and not np.isnan(y_i)) else ''
                    for old_y_i, y_i in zip(old_y, y)],
        hovertemplate='%{customdata}'
    ))


if __name__ == "__main__":
    """Test the annotation function"""
    df = px.data.gapminder().query("continent == 'Europe' and year == 2007 and pop > 2.e6")
    fig = px.bar(df, y='pop', x=list(range(len(df))))
    # TODO add old_y to add_annotations_to_fig (see crime.py)
    add_annotations_to_fig(fig=fig, x=list(range(len(df))), y=list(df['pop']),
                           percentage_change_value=[100 * np.random.randn() for i in range(len(df))])
    fig.show()
