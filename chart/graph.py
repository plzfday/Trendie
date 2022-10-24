import base64
import datetime
import io

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import yfinance as yf
from dateutil.relativedelta import relativedelta
from pytrends.request import TrendReq


def get_stock_data(ticker, duration, topics):
    mpl.use("Agg")
    today = datetime.date.today()
    start = calc_start_date(today, duration)

    company_name = yf.Ticker(ticker).info["shortName"]
    name = f"{ticker} ({company_name})"

    # Google Trends search
    kw_list = topics
    timeframe = start.strftime("%Y-%m-%d") + " " + today.strftime("%Y-%m-%d")
    pytrends = TrendReq()
    pytrends.build_payload(kw_list, timeframe=timeframe)

    trend = pytrends.interest_over_time()

    trend_ma = trend.rolling(window=10).mean()
    trend_ma_yoy = (trend_ma - trend_ma.shift(52)) / trend_ma * 100

    record = web.DataReader(ticker, "yahoo", start, today)
    record = (record - record.min()) / (record.max() - record.min()) * 100

    graphs = list()
    names = list()

    for i in range(len(kw_list)):
        data = {"record": record,
                "trend_ma_yoy": trend_ma_yoy.iloc[:, i],
                "trend_ma": trend_ma.iloc[:, i],
                "trend": trend.iloc[:, i]}
        graphs.append(plot(data))
        names.append(f"{name} / {kw_list[i]}")

    return graphs, names


def calc_start_date(today, duration):
    start = None
    if duration == "5Y":
        start = today + relativedelta(years=-5)
    elif duration == "1.5Y":
        start = today + relativedelta(years=-1, months=-6)
    elif duration == "VS19":
        pass
    elif duration == "9M":
        start = today + relativedelta(months=-9)

    return start


def plot(data):
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(data["trend"].index, data["trend"], color="mediumslateblue")
    ax.plot(data["trend_ma"].index, data["trend_ma"], color="red")
    ax.plot(data["record"].index, data["record"]["Adj Close"], color="black")

    ax.set_ylim(0, 100)
    ax.grid(axis='both')

    ax2 = ax.twinx()
    ax2.plot(data["trend_ma_yoy"].index, data["trend_ma_yoy"], color="gold")

    ax2.set_ylim(data["trend_ma_yoy"].min() - abs(data["trend_ma_yoy"].min()) * .1,
                 data["trend_ma_yoy"].max() + abs(data["trend_ma_yoy"].max()) * .1)
    plt.tight_layout()

    fig_file = io.BytesIO()
    fig.savefig(fig_file, format="png")

    graph = base64.b64encode(fig_file.getvalue()).decode()

    return graph
