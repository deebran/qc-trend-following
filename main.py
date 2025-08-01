from AlgorithmImports import *

class SentimentData(PythonData):
    def get_source(self, config, date, is_live):
        return SubscriptionDataSource("https://raw.githubusercontent.com/deebran/qc-trend-following/refs/heads/main/sentiment.csv",
                                        SubscriptionTransportMedium.REMOTE_FILE)

    def reader(self, config, line, date, is_live):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split(',')

        try:
            sentiment = SentimentData()
            sentiment.time = datetime.strptime(data[0], "%m/%d/%Y")
            sentiment.value = float(data[1])
            print("AAII data loaded.")
        except:
            print("Error loading data.")
            return None
        return sentiment
        
class TrendFollowingWithSentiment(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2019, 1, 1)
        self.set_end_date(2023, 12, 31)
        self.set_cash(1000000)
        
        self._symbol = self.add_equity("SPY", Resolution.DAILY).symbol
        self._sma50 = self.sma(self._symbol, 50)
        self._sma200 = self.sma(self._symbol, 200)
        
        self.sentiment_value = self.add_data()
        
        self.set_warm_up(200)
        
    def on_data(self, data):
        if not self._sma50.is_ready or not self._sma200.is_ready or self.sentiment_value is None:
            return

        price = self.securities[self._symbol].price
        holdings = self.portfolio[self._symbol].invested

        # Entry condition: strong trend + positive sentiment
        if price > self._sma50.current.value and self._sma50.current.value > self._sma200.current.value and self.sentiment_value > 0.4:
            if not holdings:
                self.portfolio[self._symbol].set_holdings(self.symbol, 1)
        
        # Exit condition: trend weakens or sentiment drops
        elif holdings and (price < self._sma50.current.value or self.sentiment_value < 0.4):
            self.liquidate(self._symbol)
