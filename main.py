import finnhub
import dash
import os
import pandas as pd


EXCHANGE = 'ME'
if not os.path.exists("images"):
    os.mkdir("images")


API_KEY = "c62iqiaad3iad17mv92g"
finnhub_client = finnhub.Client(API_KEY)
pairs = {}
dict = {}
app = dash.Dash(__name__)

# print('enter a ticker and metrics')
# usrinput = list(map(str, input().split()))

company = 'gazprom'
ticker = 'GAZP'
fromdate = "2022-01-01"
todate = "2022-01-01"


def symbol_lookup(user_input):

    df = pd.DataFrame(columns=['description', 'symbol'])

    stocks = finnhub_client.symbol_lookup(user_input)['result']

    if stocks:
        col = 0
        for stock in stocks:
            description = stock['description']

            symbol = stock['symbol'].split('.')[0]


            df.loc[col] = [description, symbol]
            col += 1

        return df


def get_available_stocks(SE):
    available_stocks = finnhub_client.stock_symbols(SE)

    df = pd.DataFrame(columns=['description', 'displaySymbol', 'symbol', 'type'])
    col = 0

    for stock in available_stocks:

        description = stock['description']
        display_symbol = stock['displaySymbol']
        symbol = stock['symbol']
        type = stock['type']

        df.loc[col] = [description, display_symbol, symbol, type]
        col += 1
    df_file_name = f"stocksavailable{SE}.html"
    df.to_html(df_file_name)

    return df_file_name


def get_news(ticker, fromdate, todate):
    news = finnhub_client.company_news(ticker, _from=fromdate, to=todate)
    for item in news:
        headline = item['headline']
        image = item['image']
        summary = item['summary']
        url = item['url']


def get_basic_financials(ticker):
    financials = finnhub_client.company_basic_financials(ticker, 'all')
    if financials['metric']:
        df = pd.DataFrame.from_dict(financials['metric'], orient='index')
        df.columns = ['value']
        df_file_name = f"{ticker.upper()}metrics.html"
        df.to_html(df_file_name)
        return df_file_name
    else:
        return False


def main(user_input=None):
    pass
    # get_available_stocks(EXCHANGE)
    print(symbol_lookup('FXCN'))
    # print(get_basic_financials('GAZP.ME'))


if __name__ == '__main__':
    main()

