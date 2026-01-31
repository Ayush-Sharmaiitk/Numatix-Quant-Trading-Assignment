class MultiTimeframeStrategy:
    """
    Stateless strategy.
    Makes decisions only.
    No order placement.
    No position tracking.
    """

    def generate_signal(self, df_15m, df_1h, in_position: bool):
        """
        Returns:
            "BUY", "SELL", or None
        """

        # Safety checks
        if len(df_15m) < 20 or len(df_1h) < 50:
            return None

        rsi_15m = df_15m["RSI_14"].iloc[-1]
        sma_50_1h = df_1h["SMA_50"].iloc[-1]
        close_1h = df_1h["Close"].iloc[-1]

        # ENTRY LOGIC
        if not in_position:
            if close_1h > sma_50_1h and rsi_15m < 45:
                return "BUY"

        # EXIT LOGIC
        if in_position:
            if rsi_15m > 70:
                return "SELL"

        return None
