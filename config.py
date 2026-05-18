# ============================================================
# EXIT RULES - OPTIMIZED FOR HIGHER WIN RATE
# ============================================================

EXIT_RULES = {
    # Stop loss - WIDER to avoid being stopped out by noise
    "stop_loss_atr_mult": 2.0,      # Was 1.5 - now 2.0x ATR

    # Targets - More realistic
    "target_1_atr_mult": 3.0,       # First target at 3x ATR (2:1 R:R)
    "target_2_atr_mult": 5.0,       # Second target at 5x ATR

    # Time exit - Give trades more time
    "max_hold_days": 15,            # Was 10 - now 15 days

    # Trailing stop
    "trailing_stop_atr_mult": 2.5,  # Wider trailing stop

    # Partial exit
    "partial_exit_pct": 0.5,        # Sell 50% at Target 1
}

# ============================================================
# SCREENING CRITERIA - STRICTER
# ============================================================

SCREENING_CRITERIA = {
    "min_market_cap": 2_000_000_000,  # $2B minimum
    "min_avg_volume": 500_000,         # Higher volume requirement
    "min_price": 15,                   # Higher min price
    "max_price": 1500,
    "min_atr_pct": 1.5,               # Minimum volatility
    "max_atr_pct": 8.0,               # Maximum volatility (was 10)
    "min_rsi": 30,                    # Not oversold
    "max_rsi": 65,                    # Not overbought (was 80)
    "min_rel_volume": 0.8,            # Decent volume
    "min_adx": 20,                    # Minimum trend strength
}
