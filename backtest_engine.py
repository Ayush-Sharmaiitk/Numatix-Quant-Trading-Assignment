from backtesting import Strategy
import pandas as pd

from indicators import add_indicators_15m, add_indicators_1h
from strategy import MultiTimeframeStrategy


class BacktestStrategy(Strategy):

    def init(self):
        # Single source of truth
        self.logic = MultiTimeframeStrategy()

        # Prepare full dataframe once
        df = self.data.df.copy()

        # 15m indicators
        self.df_15m = add_indicators_15m(df)

        # 1h resample + indicators
        df_1h = df.resample("1H").last().dropna()
        self.df_1h = add_indicators_1h(df_1h)

    def next(self):
        # Slice data up to current index
        current_time = self.data.index[-1]

        df_15m_slice = self.df_15m.loc[:current_time]
        df_1h_slice = self.df_1h.loc[:current_time]

        # Determine position state
        in_position = bool(self.position)

        # Ask strategy for signal
        signal = self.logic.generate_signal(
            df_15m_slice,
            df_1h_slice,
            in_position
        )

        # Execute signal
        if signal == "BUY":
            self.buy(size=0.9)

        elif signal == "SELL" and self.position:
            self.position.close()
