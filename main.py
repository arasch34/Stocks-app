import requests
from twilio.rest import Client
import os

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "FMAYIOLF2NJ0GPUP"
NEWS_API_KEY = "451b59b962df40e89d337d902b25e91f"
TWILIO_SID = "AC7a83e6e7597d979c5cdeccad642232ba"
TWILIO_AUTH_TOKEN = "42561089ffad410aaa22beb90a3e98e6"
TWILIO_VERIFIED_NUMBER = os.environ["VERIFIED_NUMBER"]

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
data = response.json()["Time Series (Daily)"]

# Get yesterday's closing stock price
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

# Get day before yesterday's closing stock price
day_before_yesterday = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday["4. close"]

# percent difference
difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
updown = None
if difference > 5:
    updown = "🔺"
else:
    updown = "🔻"

diff_percent = round((difference / float(yesterday_closing_price)) * 100)

# if percentage is greater than 5, get news articles
if abs(diff_percent) > 0:
    news_params = {
        "apiKey": NEWS_API_KEY, +
        "qInTitle": COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    # first 3 news pieces for company
    three_articles = articles[:3]

    # send a message with each article's title and description to your phone number.
    formatted_articles = [f"{STOCK_NAME}: {updown}{diff_percent}%\nHeadline: {article['title']}. "
                          f"\nBrief: {article['description']}" for article in three_articles]

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_="+16106326185",
            to=TWILIO_VERIFIED_NUMBER
        )
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
