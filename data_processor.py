import pandas as pd

class DataProcessor:
    def __init__(self, price_data, news_data):
        self.price_data = price_data
        self.news_data = news_data

    def merge_data(self):
        print("Merging price and news data into a single DataFrame...\n")
        
        # Ensure the price index has no timezone/time data for a clean merge
        self.price_data.index = self.price_data.index.normalize()
        
        if self.news_data.empty:
            self.price_data['Title'] = "No News"
            return self.price_data

        # Group multiple news articles on the same day into a single string
        grouped_news = self.news_data.groupby('Date').agg({
            'Title': lambda titles: ' | '.join(titles),
            'Publisher': lambda publishers: ' | '.join(publishers)
        }).reset_index()
        
        grouped_news.set_index('Date', inplace=True)
        
        # Merge the left table (Prices) with the right table (News) based on the Date
        merged_df = self.price_data.join(grouped_news, how='left')
        
        # Fill missing values for days where the market was open but no news was published
        merged_df['Title'] = merged_df['Title'].fillna("No News")
        merged_df['Publisher'] = merged_df['Publisher'].fillna("None")
        
        return merged_df