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
response_data = {}


def selection(start, btest_time, investement_type, i, sharpe_ratio, std, beta, treynor_ratio, choose):
    start_unix = time.mktime(
        (start - relativedelta(months=btest_time-i)).timetuple())
    end_unix = time.mktime(
        (start - relativedelta(days=+1, months=-i)).timetuple())

    if investement_type[0] == "不分類":
        data_df = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
                              con=engine, params=[start_unix, end_unix])
    elif investement_type[0] == "境內":
        data_df = pd.read_sql(sql='SELECT * FROM price WHERE EXISTS\
                (SELECT fund_id FROM domestic_information\
                WHERE investment_target == ? and price.date between ? and ?\
                and fund_id == price.fund_id)',
                              con=engine, params=[investement_type[1], start_unix, end_unix])
    else:
        data_df = pd.read_sql(sql='SELECT * FROM price WHERE EXISTS\
                    (SELECT fund_id FROM overseas_information\
                    WHERE subject_matter == ? and price.date between ? and ?\
                    and fund_id == price.fund_id)',
                              con=engine, params=[investement_type[1], start_unix, end_unix])

    if "0050 元大台灣50" not in data_df.fund_id.values:
        data_df = pd.concat([data_df, pd.read_sql(
            sql='select * from price where fund_id = "0050 元大台灣50" and date between ? and ? order by date asc',
            con=engine, params=[start_unix, end_unix])])

    data_df = data_df.pivot(index='date', columns='fund_id', values='nav')
    data_df = data_df.fillna(method="ffill")
    data_df = data_df.fillna(method="bfill")

    indicator_Rp = (data_df - data_df.iloc[0]) / data_df.iloc[0]
    indicator_σp = indicator_Rp.std(ddof=1)
    indicator_ρpm = indicator_Rp.corr()["0050 元大台灣50"]
    indicator_σm = indicator_σp["0050 元大台灣50"]
    indicator_βp = indicator_ρpm * indicator_σp / indicator_σm
    bl = data_df.iloc[0] > 0

    if sharpe_ratio != "":
        sharpe_ratio = float(sharpe_ratio)
        bl = bl & ((indicator_Rp.iloc[-1] - 0.01) /
                   indicator_σp > sharpe_ratio)

    if std != "":
        std = float(std)
        bl = bl & (data_df.std(ddof=1) < std)

    if beta != "":
        beta = float(beta)
        bl = bl & (indicator_βp < beta)

    if treynor_ratio != "":
        treynor_ratio = float(treynor_ratio)
        bl = bl & ((indicator_Rp.iloc[-1] - 0.01) /
                   indicator_βp > treynor_ratio)

    data_df = data_df.T[bl].T
    data_df = data_df.corr()
    data_df = 1 - data_df * 0.5 - 0.5

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


def profit_indicator(profit, start, end, choose_nav):
    d0050 = pd.read_sql(sql='select nav,date from price where fund_id = "0050 元大台灣50" and date between ? and ? order by date asc',
                        con=engine,
                        params=[time.mktime(start.timetuple()),
                                time.mktime(end.timetuple())],
                        index_col="date")
    d0050 = ((d0050 - d0050.iloc[0]) / d0050.iloc[0])

    indicator_σp = profit.std(ddof=1, axis=0)[0]
    indicator_ρpm = pd.concat([profit, d0050], axis=1).corr().iloc[0][1]
    indicator_σm = d0050.std(ddof=1)[0]
    indicator_βp = indicator_ρpm * indicator_σp / indicator_σm

    global response_data
    response_data['sharpe_ratio'] = ((profit.iloc[-1] - 0.01) / indicator_σp)[0]
    response_data['std'] = choose_nav.std().mean()
    response_data['beta'] = indicator_βp
    response_data['treynor_ratio'] = ((profit.iloc[-1] - 0.01) / indicator_βp)[0]

    # return {'sharpe_ratio': ((profit.iloc[-1] - 0.01) / indicator_σp)[0],
    #         "std": choose_nav.std().mean(),
    #         "beta": indicator_βp,
    #         "treynor_ratio": ((profit.iloc[-1] - 0.01) / indicator_βp)[0]}


def img(start, end, investement_type, sharpe_ratio, std, beta, treynor_ratio, btest_time, money, buy_ratio, strategy, frequency):
    choose = np.asarray([" ", " ", " ", " "], dtype='<U32')
    choose = selection(start, btest_time, investement_type, 0, sharpe_ratio, std,
                       beta, treynor_ratio, choose)
    profit = pd.DataFrame()
    choose_nav = pd.DataFrame()
    hold = np.zeros((4), dtype=np.float)
    # mds_img = {}
    global response_data
    # mean_similarity = 0
    response_data['mean_similarity'] = 0

    for i in range(12 * (end.year - start.year) + (end.month - start.month) + 1):
        start_unix = time.mktime((start + relativedelta(months=i)).timetuple())
        end_unix = time.mktime(
            (start + relativedelta(months=i+1, days=-1)).timetuple())
        data_df = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
                              con=engine, params=[start_unix, end_unix])
        data_df = data_df.pivot(index='date', columns='fund_id', values='nav')
        data_df = data_df.fillna(method="ffill")
        data_df = data_df.fillna(method="bfill")

        if strategy == 2:
            hold += (buy_ratio * money / data_df[choose].iloc[0].T).values
            profit = pd.concat(
                [profit, (data_df[choose] * hold).T.sum() / (money*(i+1))], axis=0)
        else:
            if i == 0:
                hold = (buy_ratio * money / data_df[choose].iloc[0].T).values
            elif strategy != 1 and i % frequency == frequency - 1:
                temp = (hold * data_df[choose].iloc[0]).sum()
                if strategy == 3:
                    choose = selection(start, btest_time, investement_type, i, sharpe_ratio,
                                       std, beta, treynor_ratio, choose)
                hold = (buy_ratio * temp /
                        data_df[choose].iloc[0].T).values
            profit = pd.concat(
                [profit, (data_df[choose] * hold).T.sum() / money], axis=0)

        choose_nav = pd.concat([choose_nav, data_df[choose]], sort=False)

        for j, ch in enumerate(choose):
            interest = pd.read_sql(sql='select sum(interest) from interest where date between ? and ? and fund_id == ? order by date asc',
                                   con=engine, params=[start_unix, end_unix, ch])
            hold[j] += (interest * hold[j] /
                        data_df[ch].iloc[-1]).fillna(0).loc[0][0]

        data_df = pd.concat([data_df[choose], data_df.T.sample(
            n=296).T], axis=1).T.drop_duplicates().T
        data_df = data_df.pct_change()
        data_df = data_df.corr()
        data_df = 1 - data_df * 0.5 - 0.5
        data_df = data_df.fillna(-1)
        response_data['mean_similarity'] += data_df[choose].T[choose].iloc[0].sum() / 3
        # mean_similarity += data_df[choose].T[choose].iloc[0].sum() / 3
        if i != 0:
            # mean_similarity /=2
            response_data['mean_similarity'] /=2
        
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
        p = figure(plot_width=1000, plot_height=1000, tooltips=TOOLTIPS,
                   title="MDS", toolbar_location=None, tools="")
        p.x_range = Range1d(-0.6, 0.6)
        p.y_range = Range1d(-0.6, 0.6)
        p.circle(x='x', y='y', color='color', size=6.5, source=source)
        script, div = components(p, CDN)
        response_data[(start + relativedelta(months=i)).strftime('%Y-%m')] = {'script': script, 'div': div}
        # mds_img[(start + relativedelta(months=i)
        #          ).strftime('%Y-%m')] = {'script': script, 'div': div}

    profit = profit.rename(columns={0: "profit"})
    profit["profit"] = (profit["profit"]-1) * 100
    profit.index.name = "date"
    
    # indicator = profit_indicator(profit, start, end, choose_nav)
    profit_indicator(profit, start, end, choose_nav)
    response_data['money'] = (hold * choose_nav.iloc[-1][choose]).sum()
    response_data['profit'] = profit.iloc[-1][0]

    # indicator['money'] = (hold * choose_nav.iloc[-1][choose]).sum()
    # indicator['profit'] = profit.iloc[-1][0]

    profit.index = profit.index + 28800
    profit.index = pd.to_datetime(profit.index, unit='s')

    p = figure(x_axis_type="datetime", plot_width=1500,
               plot_height=300, title="Profit", toolbar_location=None, tools="")
    p.line(x='date', y='profit', line_width=3, source=profit)
    p.add_tools(HoverTool(tooltips=[("date", "@date{%F}"), ("profit", "@profit%")],
                          formatters={'date': 'datetime', }, mode='vline'))
    script, div = components(p, CDN)
    response_data['profit_img'] = {'script': script, 'div': div}
    # profit_img = {'script': script, 'div': div}
    # return profit_img, mds_img, indicator, mean_similarity
    return response_data