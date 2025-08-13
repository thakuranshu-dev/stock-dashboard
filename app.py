import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import os
from dotenv import load_dotenv

st.title("Stock Dashboard")
ticker = st.sidebar.text_input("Ticker",placeholder="Enter Ticker: ").upper()
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

if not ticker:
    st.warning("Please provide valid ticker symbol and duration.")
else:
    data = yf.download(ticker, start=start_date, end=end_date,auto_adjust=False)
    fig = px.line(data_frame=data, x=data.index, y=data['Adj Close'][ticker], title=ticker, labels={'x': 'Date', 'y': 'Close'})
    st.plotly_chart(fig)


    pricing_data, fundamental_data, news =st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

    with pricing_data:
        st.header("Price")
        data2 = data
        # If columns are a MultiIndex, flatten them
        if isinstance(data.columns, pd.MultiIndex):
            data2.columns = data2.columns.get_level_values(0)
        data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
        data2.dropna(inplace=True)
        st.write(data2)
        
        annual_return = data2['% Change'].mean() * 252 * 100
        st.write("Annual return: ", annual_return, " %")
        # st.write(f"Annual Return: {annual_return:.2f}%")

        stdev = np.std(data2['% Change']) * np.sqrt(252)
        st.write("Standard Deviation: ", stdev*100, " %")
        st.write('Risk Adjusted Return: ', annual_return / (stdev*100))

    from alpha_vantage.fundamentaldata import FundamentalData
    with fundamental_data:
        load_dotenv()
        key = os.getenv("API_KEY")

        fd = FundamentalData(key, output_format='pandas')
        st.subheader("Balance Sheet")
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)
        st.subheader("Income Statement")
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is_ = income_statement.T[2:]
        is_.columns = list(income_statement.T.iloc[0])
        st.write(is_)
        st.subheader("Cash Flow Statement")
        cash_flow_statement = fd.get_cash_flow_annual(ticker)[0]
        cfs = cash_flow_statement.T[2:]
        cfs.columns = list(cash_flow_statement.T.iloc[0])
        st.write(cfs)
        st.header("Fundamental Data")

    from stocknews import StockNews
    with news:
        st.header(f"News of {ticker}")
        news = StockNews(ticker, save_news=False)
        df_news = news.read_rss()
        if df_news.empty:
            st.write("No news available for this ticker.")
        else:
            for i in range(10):
                st.subheader(f'News {i+1}')
                st.write(df_news['published'][i])
                st.write(df_news['title'][i])
                st.write(df_news['summary'][i])
                st.write(f"Title Sentiment {df_news['sentiment_title'][i]}")
                st.write(f"News Sentiment {df_news['sentiment_title'][i]}")


## TODO: handle api limit error
