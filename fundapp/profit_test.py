import pandas as pd
import numpy as np
import time

from sklearn.manifold import MDS
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy import create_engine
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bokeh.embed import components
from bokeh.models import HoverTool, Range1d
from bokeh.plotting import ColumnDataSource, figure
from bokeh.resources import CDN

engine = create_engine('sqlite:///fund.db')


def selection(start, investement_type, i, sharpe_ratio, std, beta, treynor_ratio, choose):
    start_unix = time.mktime(
        (datetime.strptime(start, '%Y-%m') - relativedelta(years=+1, months=-i)).timetuple())
    end_unix = time.mktime(
        (datetime.strptime(start, '%Y-%m') - relativedelta(days=+1, months=-i)).timetuple())
    
    if investement_type[0] == "不分類":
        data_df = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
                con=engine, params=[start_unix, end_unix])
    elif investement_type[0] == "境內":
        data_df = pd.read_sql(sql='SELECT * FROM price WHERE EXISTS\
                (SELECT fund_id FROM domestic_information\
                WHERE investment_target == ? and price.date between ? and ?\
                and fund_id == price.fund_id)', con=engine, params=[investement_type[1], start_unix, end_unix])
    else:
        data_df = pd.read_sql(sql='SELECT * FROM price WHERE EXISTS\
                    (SELECT fund_id FROM overseas_information\
                    WHERE subject_matter == ? and price.date between ? and ?\
                    and fund_id == price.fund_id)', con=engine, params=[investement_type[1], start_unix, end_unix])


    # data_df = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
    #                       con=engine, params=[start_unix, end_unix])
    data_df = data_df.pivot(index='date', columns='fund_id', values='nav')
    data_df = data_df.fillna(method="ffill")
    data_df = data_df.fillna(method="bfill")

    data_df = data_df.T[(((data_df.iloc[-1] - data_df.iloc[0]) /
                          data_df.iloc[0]) - 0.01) / data_df.std(ddof=1) > sharpe_ratio].T
    data_df = data_df.T[data_df.std(ddof=1) < std].T

    if "0050 元大台灣50" not in data_df.columns:
        data_df.insert(0, "0050 元大台灣50",
                       pd.read_sql(sql='select nav,date from price where fund_id = "0050 元大台灣50" and date between ? and ? order by date asc',
                                   con=engine, params=[start_unix, end_unix], index_col="date"))
    data_df = data_df.T[(((data_df.iloc[-1] - data_df.iloc[0]) / data_df.iloc[0]) - 0.01) / (
        data_df.pct_change().corr()["0050 元大台灣50"] * data_df.std() / data_df.std()[0]) > treynor_ratio].T

    if "0050 元大台灣50" not in data_df.columns:
        data_df.insert(0, "0050 元大台灣50",
                       pd.read_sql(sql='select nav,date from price where fund_id = "0050 元大台灣50" and date between ? and ? order by date asc',
                                   con=engine, params=[start_unix, end_unix], index_col="date"))

    data_df = data_df.pct_change()
    data_df = data_df.T[data_df.corr()["0050 元大台灣50"] *
                        data_df.std() / data_df.std()[0] < beta].T
    data_df = data_df.corr()

    camp = pd.DataFrame(AgglomerativeClustering(n_clusters=4).fit(
        data_df).labels_, index=data_df.index, columns=['label'])
    for i, ch in enumerate(choose):
        if ch in camp.index:
            camp = camp.drop(
                camp[camp.label == camp.loc[ch].label].index, axis=0)
        else:
            temp = camp.sample(n=1)
            camp = camp.drop(camp[camp.label == temp.label[0]].index, axis=0)
            choose[i] = temp.index[0]
    return choose


def img(start, end, investement_type, sharpe_ratio, std, beta, treynor_ratio, money, buy_ratio, strategy, frequency):
    choose = np.asarray([" ", " ", " ", " "], dtype='<U32')
    choose = selection(start, investement_type, 0, sharpe_ratio, std,
                       beta, treynor_ratio, choose)
    profit = pd.DataFrame()
    hold = np.zeros([4], dtype=np.float)
    mds_img = {}

    for i in range((datetime.strptime("2017-12", "%Y-%m").month - datetime.strptime("2017-01", "%Y-%m").month)+1):
        start_unix = time.mktime(
            (datetime.strptime(start, '%Y-%m') + relativedelta(months=i)).timetuple())
        end_unix = time.mktime((datetime.strptime(
            start, '%Y-%m') + relativedelta(months=i+1, days=-1)).timetuple())
        data_df = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
                              con=engine, params=[start_unix, end_unix])
        data_df = data_df.pivot(index='date', columns='fund_id', values='nav')
        data_df = data_df.fillna(method="ffill")
        data_df = data_df.fillna(method="bfill")

        if strategy == "regular saving plan":
            hold += (buy_ratio * money / data_df[choose].iloc[0].T).values
            profit = pd.concat(
                [profit, (data_df[choose] * hold).T.sum() / (money*(i+1))], axis=0)
        else:
            if i == 0:
                hold = (buy_ratio * money / data_df[choose].iloc[0].T).values
            if strategy == "constant mix strategy" or strategy == "dynamic asset allocation strategy":
                if i % frequency == frequency - 1:
                    temp = (hold * data_df[choose].iloc[0]).sum()
                    if strategy == "dynamic asset allocation strategy":
                        choose = selection(start, investement_type, i, sharpe_ratio,
                                           std, beta, treynor_ratio, choose)
                    hold = (buy_ratio * temp /
                            data_df[choose].iloc[0].T).values
            profit = pd.concat(
                [profit, (data_df[choose] * hold).T.sum() / money], axis=0)

        data_df = pd.concat([data_df[choose], data_df.T.sample(
            n=296).T], axis=1).T.drop_duplicates().T

        data_df = data_df.pct_change()
        data_df = data_df.corr()
        data_df = 1 - data_df * 0.5 - 0.5
        data_df = data_df.fillna(-1)

        color = np.asarray(["yellow" for i in range(len(data_df))])
        color[0:4] = "purple"
        mds = MDS(n_components=2, dissimilarity='precomputed').fit(
            data_df).embedding_
        source = ColumnDataSource(data=dict(x=mds[:, 0],
                                            y=mds[:, 1],
                                            name=data_df.index,
                                            color=color,
                                            ))
        TOOLTIPS = [
            ("fund_id", "@name"),
        ]
        p = figure(plot_width=700, plot_height=700, tooltips=TOOLTIPS,
                   title="MDS", toolbar_location=None, tools="")
        p.x_range = Range1d(-0.6, 0.6)
        p.y_range = Range1d(-0.6, 0.6)
        p.circle(x='x', y='y', color='color', size=6.5, source=source)
        script, div = components(p, CDN)
        mds_img[(datetime.strptime(start, '%Y-%m') + relativedelta(months=i)
                 ).strftime('%Y-%m')] = {'script': script, 'div': div}

    profit = profit.rename(columns={0: "profit"})
    profit["profit"] = (profit["profit"]-1) * 100
    profit.index.name = "date"
    profit.index = profit.index + 28800
    profit.index = pd.to_datetime(profit.index, unit='s')

    p = figure(x_axis_type="datetime", plot_width=1500,
               plot_height=500, title="Profit", toolbar_location=None, tools="")
    p.line(x='date', y='profit', line_width=3, source=profit)
    p.add_tools(HoverTool(tooltips=[("date", "@date{%F}"), ("profit", "@profit%")],
                          formatters={'date': 'datetime', }, mode='vline'))
    script, div = components(p, CDN)
    profit_img = {'script': script, 'div': div}
    return profit_img, mds_img
