from data_fetcher import MarketDataFetcher

kardemir=MarketDataFetcher("KARCL.IS")
apple=MarketDataFetcher("AAPL")

kardemir_data=kardemir.fetch_data()
apple_data = apple.fetch_data(interval="5d")

print(kardemir_data.head())
print(apple_data.head())