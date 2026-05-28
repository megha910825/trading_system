import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ============================================================
# SWING TRADING SYSTEM - 4% MONTHLY TARGET
# Aggressive Growth Strategy for High-Volume Quality Stocks
# ============================================================

# Get the current directory or use Desktop
# Change this path to wherever you want to save the file
OUTPUT_DIR = os.path.expanduser("~")  # This saves to your home directory
# Alternative: OUTPUT_DIR = os.path.expanduser("~/Desktop")  # Saves to Desktop
# Alternative: OUTPUT_DIR = os.getcwd()  # Saves to current directory

# Create the output file path
output_file = os.path.join(OUTPUT_DIR, 'Swing_Trading_4PCT_Monthly_System.xlsx')

print(f"File will be saved to: {output_file}")
print("Creating your trading system...")

# Create Excel writer
writer = pd.ExcelWriter(output_file, engine='openpyxl')

# ============================================================
# SHEET 1: SYSTEM OVERVIEW & TARGETS
# ============================================================

overview_data = {
    'Category': [
        '=== MONTHLY TARGET ===',
        'Target Monthly Return',
        'Target Annual Return (Compounded)',
        'Account Size',
        'Monthly Dollar Target',
        '',
        '=== TRADING PARAMETERS ===',
        'Trades Per Month',
        'Required Win Rate',
        'Average Winner Target',
        'Average Loser Limit',
        'Risk Per Trade',
        'Max Concurrent Positions',
        'Position Size (% of Account)',
        '',
        '=== STOCK CRITERIA (AGGRESSIVE) ===',
        'ATR Range',
        'Beta Range',
        'Minimum Volume',
        'Market Cap',
        '',
        '=== MATHEMATICAL EXPECTANCY ===',
        'Expected Wins/Month',
        'Expected Losses/Month',
        'Gross Win Amount',
        'Gross Loss Amount',
        'Net Monthly Return',
        'Margin of Safety'
    ],
    'Value': [
        '',
        '4.0%',
        '60.1%',
        '$50,000',
        '$2,000',
        '',
        '',
        '12',
        '58%+',
        '5-7%',
        '2.5-3%',
        '1.5%',
        '6-8',
        '20-30%',
        '',
        '',
        '2.5% - 5.0%',
        '1.0 - 1.8',
        '> 2 Million',
        '> $5 Billion',
        '',
        '',
        '7 (58% of 12)',
        '5 (42% of 12)',
        '7 × 5.5% × 25% = 9.6%',
        '5 × 2.75% × 25% = 3.4%',
        '9.6% - 3.4% = 6.2%',
        '6.2% vs 4% target = 55% buffer'
    ],
    'Notes': [
        '',
        'Aggressive but achievable with discipline',
        'Compound growth over 12 months',
        'Adjust based on your capital',
        'This is your monthly profit goal',
        '',
        '',
        'More active trading required',
        'Higher selectivity needed',
        'Look for 5-8% moves',
        'Strict risk management',
        'Slightly higher to capture larger moves',
        'More diversification for higher activity',
        'Balance between concentration and diversification',
        '',
        '',
        'Need volatile stocks for bigger moves',
        'Moderate-high volatility stocks',
        'Higher liquidity for faster entries/exits',
        'Larger caps for reliability',
        '',
        '',
        'Based on 58% win rate',
        'Acceptable loss frequency',
        'Using 25% position size',
        'Controlled losses',
        'EXCEEDS 4% target',
        'Room for some bad months'
    ]
}

df_overview = pd.DataFrame(overview_data)
df_overview.to_excel(writer, sheet_name='System_Overview', index=False)
print("✓ Sheet 1: System Overview created")

# ============================================================
# SHEET 2: AGGRESSIVE STOCK SCREENER
# ============================================================

screener_data = {
    'Symbol': ['NVDA', 'TSLA', 'AMD', 'META', 'NFLX', 'GOOGL', 'AMZN', 'MSFT', 'AAPL', 'CRM',
               'ADBE', 'NOW', 'SHOP', 'SQ', 'COIN', 'MELI', 'SE', 'ROKU', 'SNOW', 'DDOG',
               'CRWD', 'ZS', 'PANW', 'FTNT', 'NET', 'MDB', 'TEAM', 'OKTA', 'TWLO', 'U'],
    'Company': ['NVIDIA Corp', 'Tesla Inc', 'AMD', 'Meta Platforms', 'Netflix',
                'Alphabet', 'Amazon', 'Microsoft', 'Apple', 'Salesforce',
                'Adobe', 'ServiceNow', 'Shopify', 'Block Inc', 'Coinbase',
                'MercadoLibre', 'Sea Limited', 'Roku', 'Snowflake', 'Datadog',
                'CrowdStrike', 'Zscaler', 'Palo Alto', 'Fortinet', 'Cloudflare',
                'MongoDB', 'Atlassian', 'Okta', 'Twilio', 'Unity Software'],
    'Sector': ['Tech-Semi', 'Auto-EV', 'Tech-Semi', 'Tech-Social', 'Entertainment',
               'Tech-Internet', 'E-Commerce', 'Tech-Software', 'Tech-Hardware', 'Tech-Cloud',
               'Tech-Software', 'Tech-Cloud', 'E-Commerce', 'Fintech', 'Crypto',
               'E-Commerce', 'E-Commerce', 'Entertainment', 'Tech-Cloud', 'Tech-Cloud',
               'Cybersecurity', 'Cybersecurity', 'Cybersecurity', 'Cybersecurity', 'Tech-Cloud',
               'Tech-Database', 'Tech-Software', 'Cybersecurity', 'Tech-Cloud', 'Tech-Gaming'],
    'Price': [875.50, 248.30, 165.80, 505.75, 485.90, 141.80, 178.90, 378.25, 178.50, 265.40,
              578.30, 785.40, 78.50, 82.30, 225.60, 1685.00, 45.80, 68.50, 185.60, 125.80,
              325.40, 225.60, 315.80, 75.60, 98.50, 425.60, 245.80, 98.50, 68.90, 38.50],
    'Market_Cap_B': [2160, 790, 268, 1300, 215, 1780, 1850, 2810, 2800, 255,
                    258, 162, 98, 48, 52, 85, 28, 52, 62, 42,
                    78, 32, 98, 58, 32, 28, 62, 15, 12, 15],
    'Avg_Volume_M': [42.5, 95.6, 45.2, 15.2, 5.8, 22.1, 35.8, 18.5, 52.3, 4.5,
                    3.2, 1.2, 12.5, 8.5, 15.2, 0.8, 8.5, 12.5, 3.2, 2.8,
                    3.5, 1.8, 2.5, 3.2, 8.5, 1.2, 0.8, 5.2, 3.8, 8.5],
    'ATR_Pct': [3.5, 4.2, 3.8, 2.5, 2.8, 1.8, 2.2, 1.5, 2.1, 2.2,
                1.8, 2.2, 4.5, 4.2, 5.8, 3.2, 5.5, 5.2, 4.2, 3.5,
                3.2, 3.8, 2.5, 2.8, 3.8, 4.2, 2.8, 4.5, 4.8, 5.2],
    'Beta': [1.72, 2.05, 1.85, 1.25, 1.35, 1.05, 1.18, 0.92, 1.28, 1.22,
             1.15, 1.12, 1.85, 1.95, 2.85, 1.45, 1.92, 1.88, 1.52, 1.45,
             1.38, 1.52, 1.18, 1.12, 1.65, 1.55, 1.25, 1.75, 1.82, 1.92],
    'RSI_14': [55, 48, 52, 58, 62, 54, 56, 51, 53, 49,
               47, 55, 42, 45, 38, 52, 35, 40, 48, 51,
               58, 52, 61, 55, 48, 45, 52, 42, 38, 35],
    'Above_50_EMA': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes',
                    'Yes', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No', 'Yes', 'Yes',
                    'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'Yes', 'No', 'No', 'No'],
    'Rel_Volume': [1.8, 2.2, 1.5, 1.3, 1.1, 1.2, 1.4, 1.1, 1.2, 1.5,
                   0.9, 1.3, 1.8, 2.1, 2.5, 0.8, 1.9, 1.7, 1.2, 1.4,
                   1.6, 1.3, 1.1, 1.2, 1.5, 1.8, 0.9, 1.6, 1.4, 1.2],
    'Earnings_Trend': ['Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Up',
                       'Up', 'Up', 'Down', 'Flat', 'Down', 'Up', 'Down', 'Down', 'Up', 'Up',
                       'Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Up', 'Down', 'Down', 'Down']
}

df_screener = pd.DataFrame(screener_data)

# Aggressive screening criteria for 4% target
df_screener['Pass_MarketCap'] = df_screener['Market_Cap_B'] >= 5
df_screener['Pass_Volume'] = df_screener['Avg_Volume_M'] >= 2
df_screener['Pass_ATR'] = (df_screener['ATR_Pct'] >= 2.5) & (df_screener['ATR_Pct'] <= 6.0)
df_screener['Pass_Beta'] = (df_screener['Beta'] >= 1.0) & (df_screener['Beta'] <= 2.5)
df_screener['Pass_Trend'] = df_screener['Above_50_EMA'] == 'Yes'
df_screener['Pass_RelVol'] = df_screener['Rel_Volume'] >= 1.0
df_screener['Pass_Earnings'] = df_screener['Earnings_Trend'] == 'Up'
df_screener['Pass_RSI'] = (df_screener['RSI_14'] >= 35) & (df_screener['RSI_14'] <= 65)

df_screener['Criteria_Passed'] = (
    df_screener['Pass_MarketCap'].astype(int) +
    df_screener['Pass_Volume'].astype(int) +
    df_screener['Pass_ATR'].astype(int) +
    df_screener['Pass_Beta'].astype(int) +
    df_screener['Pass_Trend'].astype(int) +
    df_screener['Pass_RelVol'].astype(int) +
    df_screener['Pass_Earnings'].astype(int) +
    df_screener['Pass_RSI'].astype(int)
)

df_screener['Qualified'] = df_screener['Criteria_Passed'] >= 7
df_screener['Score'] = df_screener['Criteria_Passed'] * 12.5

df_screener.to_excel(writer, sheet_name='Stock_Screener_4PCT', index=False)
print("✓ Sheet 2: Stock Screener created")

# ============================================================
# SHEET 3: TECHNICAL ANALYSIS - AGGRESSIVE LEVELS
# ============================================================

qualified_stocks = df_screener[df_screener['Qualified'] == True].head(12)

technical_data = []
for _, row in qualified_stocks.iterrows():
    symbol = row['Symbol']
    price = row['Price']
    atr_pct = row['ATR_Pct']
    atr = price * (atr_pct / 100)
    rsi = row['RSI_14']
    beta = row['Beta']

    # Technical levels
    ema_10 = price * (1 + random.uniform(-0.015, 0.015))
    ema_20 = price * (1 + random.uniform(-0.025, 0.01))
    ema_50 = price * (1 + random.uniform(-0.06, -0.02))
    support = price * (1 - random.uniform(0.025, 0.05))
    resistance = price * (1 + random.uniform(0.06, 0.12))

    # AGGRESSIVE entry/exit for 4% target
    entry_zone_low = max(support, ema_20 * 0.99)
    entry_zone_high = ema_20 * 1.01
    ideal_entry = (entry_zone_low + entry_zone_high) / 2

    # Wider stops, larger targets for 4% monthly
    stop_loss = ideal_entry - (1.75 * atr)
    target_1 = ideal_entry + (2.5 * atr)
    target_2 = ideal_entry + (4 * atr)

    risk = ideal_entry - stop_loss
    reward = target_1 - ideal_entry
    rr_ratio = reward / risk if risk > 0 else 0

    # Aggressive scoring
    score = 0
    if rsi > 40 and rsi < 60: score += 20
    if price > ema_50: score += 15
    if abs(price - ema_20) / price < 0.03: score += 25
    if rr_ratio >= 2: score += 20
    if atr_pct >= 2.5: score += 10
    if beta >= 1.2: score += 10

    setup = 'PULLBACK' if abs(price - ema_20) / price < 0.02 else ('BREAKOUT' if price > resistance * 0.98 else 'MOMENTUM')

    expected_move_5d = atr * 2.5
    expected_pct_5d = (expected_move_5d / ideal_entry) * 100

    technical_data.append({
        'Symbol': symbol,
        'Current_Price': round(price, 2),
        'EMA_10': round(ema_10, 2),
        'EMA_20': round(ema_20, 2),
        'EMA_50': round(ema_50, 2),
        'RSI_14': round(rsi, 1),
        'Beta': round(beta, 2),
        'ATR_14': round(atr, 2),
        'ATR_Pct': round(atr_pct, 2),
        'Support': round(support, 2),
        'Resistance': round(resistance, 2),
        'Setup_Type': setup,
        'Entry_Zone_Low': round(entry_zone_low, 2),
        'Entry_Zone_High': round(entry_zone_high, 2),
        'Ideal_Entry': round(ideal_entry, 2),
        'Stop_Loss': round(stop_loss, 2),
        'Stop_Pct': round((ideal_entry - stop_loss) / ideal_entry * 100, 2),
        'Target_1': round(target_1, 2),
        'Target_1_Pct': round((target_1 - ideal_entry) / ideal_entry * 100, 2),
        'Target_2': round(target_2, 2),
        'Target_2_Pct': round((target_2 - ideal_entry) / ideal_entry * 100, 2),
        'Risk_Per_Share': round(risk, 2),
        'Reward_Per_Share': round(reward, 2),
        'Risk_Reward_Ratio': round(rr_ratio, 2),
        'Expected_5D_Move_Pct': round(expected_pct_5d, 2),
        'Signal_Score': score,
        'Signal_Status': 'STRONG BUY' if score >= 70 else ('BUY' if score >= 55 else 'WATCH')
    })

df_technical = pd.DataFrame(technical_data)
df_technical.to_excel(writer, sheet_name='Technical_Analysis_4PCT', index=False)
print("✓ Sheet 3: Technical Analysis created")

# ============================================================
# SHEET 4: POSITION SIZING FOR 4% TARGET
# ============================================================

position_calc = {
    'Parameter': [
        '=== ACCOUNT SETTINGS ===',
        'Account Size ($)',
        'Monthly Target (%)',
        'Monthly Target ($)',
        '',
        '=== AGGRESSIVE RISK PARAMETERS ===',
        'Risk Per Trade (%)',
        'Risk Per Trade ($)',
        'Max Positions',
        'Max Position Size (%)',
        'Max Position Size ($)',
        'Max Sector Exposure (%)',
        'Daily Loss Limit (%)',
        'Weekly Loss Limit (%)',
        '',
        '=== SAMPLE TRADE CALCULATION ===',
        'Stock Symbol',
        'Entry Price ($)',
        'Stop Loss ($)',
        'Stop Loss Distance (%)',
        'Risk Per Share ($)',
        'Shares to Buy',
        'Position Value ($)',
        'Position Size (% of Account)',
        'Actual Risk ($)',
        'Actual Risk (%)',
        '',
        '=== PROFIT TARGETS ===',
        'Target 1 ($)',
        'Target 1 Gain (%)',
        'Profit at Target 1 ($)',
        'Target 2 ($)',
        'Target 2 Gain (%)',
        'Profit at Target 2 ($)',
        '',
        '=== MONTHLY MATH ===',
        'Trades Needed for 4%',
        'If 60% Win Rate',
        'Winning Trades',
        'Avg Win ($)',
        'Total Wins ($)',
        'Losing Trades',
        'Avg Loss ($)',
        'Total Losses ($)',
        'Net Monthly P&L ($)',
        'Net Monthly Return (%)'
    ],
    'Value': [
        '',
        50000,
        4.0,
        2000,
        '',
        '',
        1.5,
        750,
        8,
        25,
        12500,
        30,
        2.0,
        5.0,
        '',
        '',
        'NVDA',
        875.50,
        845.00,
        3.48,
        30.50,
        24,
        21012,
        42.02,
        732,
        1.46,
        '',
        '',
        936.50,
        6.97,
        1464,
        967.00,
        10.45,
        2196,
        '',
        '',
        12,
        '7.2 wins, 4.8 losses',
        7,
        600,
        4200,
        5,
        400,
        2000,
        2200,
        4.4
    ],
    'Formula_Notes': [
        '',
        'Your trading capital - EDIT THIS',
        'AGGRESSIVE monthly target',
        '= Account × 4%',
        '',
        '',
        '1.5% vs 1% for higher returns',
        '= Account × Risk %',
        'More positions for higher activity',
        'Slightly higher concentration allowed',
        '= Account × Max Position %',
        'Allow slightly more sector concentration',
        'Stop trading if down 2% in a day',
        'Stop trading if down 5% in a week',
        '',
        '',
        'High ATR stock example',
        'Your planned entry price',
        'Based on 1.75 × ATR',
        '= (Entry - Stop) / Entry × 100',
        '= Entry - Stop Loss',
        '= Risk $ / Risk Per Share',
        '= Shares × Entry Price',
        '= Position Value / Account × 100',
        '= Shares × Risk Per Share',
        '= Actual Risk / Account × 100',
        '',
        '',
        'First profit target (2.5 × ATR)',
        '= (Target - Entry) / Entry × 100',
        '= Shares × (Target 1 - Entry)',
        'Second target (4 × ATR)',
        '= (Target - Entry) / Entry × 100',
        '= Shares × (Target 2 - Entry)',
        '',
        '',
        'Higher trade frequency needed',
        'Expected distribution',
        'Rounded down',
        'Average winning trade',
        '= Wins × Avg Win',
        'Rounded up',
        'Average losing trade',
        '= Losses × Avg Loss',
        '= Total Wins - Total Losses',
        '= Net P&L / Account × 100'
    ]
}

df_position = pd.DataFrame(position_calc)
df_position.to_excel(writer, sheet_name='Position_Calculator_4PCT', index=False)
print("✓ Sheet 4: Position Calculator created")

# ============================================================
# SHEET 5: TRADE JOURNAL - 4% EXAMPLES
# ============================================================

trade_journal = {
    'Trade_ID': list(range(1, 16)),
    'Date_Entry': ['2024-01-02', '2024-01-03', '2024-01-05', '2024-01-08', '2024-01-09',
                   '2024-01-11', '2024-01-12', '2024-01-15', '2024-01-17', '2024-01-19',
                   '2024-01-22', '2024-01-24', '2024-01-25', '2024-01-29', '2024-01-31'],
    'Date_Exit': ['2024-01-05', '2024-01-08', '2024-01-09', '2024-01-12', '2024-01-15',
                  '2024-01-16', '2024-01-18', '2024-01-19', '2024-01-24', '2024-01-24',
                  '2024-01-26', '2024-01-29', '2024-01-30', '2024-02-02', ''],
    'Symbol': ['NVDA', 'AMD', 'TSLA', 'META', 'GOOGL', 'MSFT', 'NFLX', 'CRM', 'ADBE', 'AMZN',
               'NOW', 'NVDA', 'AMD', 'CRWD', 'PANW'],
    'Setup_Type': ['PULLBACK', 'MOMENTUM', 'PULLBACK', 'BREAKOUT', 'PULLBACK',
                   'MOMENTUM', 'PULLBACK', 'BREAKOUT', 'PULLBACK', 'MOMENTUM',
                   'BREAKOUT', 'PULLBACK', 'MOMENTUM', 'PULLBACK', 'BREAKOUT'],
    'Entry_Price': [850.00, 160.00, 240.00, 495.00, 138.00, 372.00, 475.00, 258.00, 565.00, 175.00,
                    775.00, 865.00, 162.00, 318.00, 310.00],
    'Exit_Price': [898.00, 170.50, 232.00, 522.00, 146.00, 378.00, 498.00, 250.00, 598.00, 168.00,
                   812.00, 905.00, 155.00, 338.00, 0],
    'Shares': [12, 31, 20, 10, 36, 13, 10, 19, 8, 28,
               6, 11, 30, 15, 16],
    'Stop_Loss': [820.00, 152.00, 228.00, 480.00, 132.00, 362.00, 458.00, 248.00, 545.00, 168.00,
                  750.00, 835.00, 154.00, 305.00, 298.00],
    'Target_1': [900.00, 172.00, 258.00, 525.00, 148.00, 390.00, 510.00, 278.00, 600.00, 188.00,
                 820.00, 915.00, 178.00, 345.00, 335.00],
    'Result': ['WIN', 'WIN', 'LOSS', 'WIN', 'WIN', 'WIN', 'WIN', 'LOSS', 'WIN', 'LOSS',
               'WIN', 'WIN', 'LOSS', 'WIN', 'OPEN'],
    'P_L_Dollars': [576.00, 325.50, -160.00, 270.00, 288.00, 78.00, 230.00, -152.00, 264.00, -196.00,
                    222.00, 440.00, -210.00, 300.00, 0],
    'P_L_Percent': [5.65, 6.56, -3.33, 5.45, 5.80, 1.61, 4.84, -3.10, 5.84, -4.00,
                    4.77, 4.62, -4.32, 6.29, 0],
    'R_Multiple': [1.60, 1.31, -0.42, 1.80, 1.33, 0.60, 1.35, -0.80, 1.32, -1.00,
                   1.48, 1.33, -0.88, 1.54, 0],
    'Hold_Days': [3, 5, 4, 4, 6, 5, 6, 4, 7, 5, 4, 5, 5, 4, 0],
    'Notes': ['Perfect pullback to 20 EMA', 'Strong momentum continuation', 'Gapped down on news - loss',
              'Clean breakout with volume', 'Textbook EMA bounce', 'Quick scalp, took early profit',
              'Held through consolidation', 'False breakout - stopped out', 'Support bounce worked',
              'Market pullback hit stop', 'Sector strength helped', 'Second entry on same setup',
              'Overtraded - forced entry', 'Quality setup, patient entry', 'Currently holding']
}

df_journal = pd.DataFrame(trade_journal)
df_journal.to_excel(writer, sheet_name='Trade_Journal_4PCT', index=False)
print("✓ Sheet 5: Trade Journal created")

# ============================================================
# SHEET 6: PERFORMANCE DASHBOARD - 4% TARGET
# ============================================================

completed = df_journal[df_journal['Result'] != 'OPEN']
wins = completed[completed['Result'] == 'WIN']
losses = completed[completed['Result'] == 'LOSS']

total_trades = len(completed)
win_count = len(wins)
loss_count = len(losses)
win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
total_pnl = completed['P_L_Dollars'].sum()
avg_win = wins['P_L_Dollars'].mean() if len(wins) > 0 else 0
avg_loss = abs(losses['P_L_Dollars'].mean()) if len(losses) > 0 else 0
profit_factor = wins['P_L_Dollars'].sum() / abs(losses['P_L_Dollars'].sum()) if losses['P_L_Dollars'].sum() != 0 else 0
avg_r = completed['R_Multiple'].mean()
expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)

performance_data = {
    'Metric': [
        '=== 4% MONTHLY TARGET TRACKING ===',
        'Target Monthly Return',
        'Target Monthly Dollars',
        'Current Month P&L',
        'Progress to Target',
        'Status',
        '',
        '=== TRADE STATISTICS ===',
        'Total Trades (Completed)',
        'Winning Trades',
        'Losing Trades',
        'Win Rate',
        'Required Win Rate',
        'Win Rate Status',
        '',
        '=== PROFIT METRICS ===',
        'Total P&L ($)',
        'Average Win ($)',
        'Average Loss ($)',
        'Largest Win ($)',
        'Largest Loss ($)',
        'Profit Factor',
        'Average R-Multiple',
        'Expectancy per Trade ($)',
        '',
        '=== RISK METRICS ===',
        'Max Drawdown ($)',
        'Max Drawdown (%)',
        'Consecutive Wins (Max)',
        'Consecutive Losses (Max)'
    ],
    'Value': [
        '',
        '4.00%',
        '$2,000',
        f'${total_pnl:,.2f}',
        f'{(total_pnl / 2000 * 100):.1f}%',
        '✓ ON TRACK' if total_pnl >= 1800 else ('⚠ CLOSE' if total_pnl >= 1200 else '✗ BEHIND'),
        '',
        '',
        total_trades,
        win_count,
        loss_count,
        f'{win_rate:.1f}%',
        '58%+',
        '✓ EXCEEDS' if win_rate >= 58 else '⚠ BELOW TARGET',
        '',
        '',
        f'${total_pnl:,.2f}',
        f'${avg_win:,.2f}',
        f'${avg_loss:,.2f}',
        f'${wins["P_L_Dollars"].max():,.2f}' if len(wins) > 0 else '$0',
        f'${losses["P_L_Dollars"].min():,.2f}' if len(losses) > 0 else '$0',
        f'{profit_factor:.2f}',
        f'{avg_r:.2f}',
        f'${expectancy:,.2f}',
        '',
        '',
        '-$450',
        '-0.90%',
        5,
        2
    ],
    'Notes': [
        '',
        'AGGRESSIVE TARGET',
        'Account Size × 4%',
        'Sum of all closed trades',
        'Current P&L / Target',
        'Need $2,000 by month end',
        '',
        '',
        '',
        '',
        '',
        '',
        'Minimum for 4% target',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        'Should be > 1.5 for 4% target',
        'Should be > 1.0',
        'Average profit per trade',
        '',
        '',
        'Peak to trough',
        'As % of account',
        '',
        ''
    ]
}

df_performance = pd.DataFrame(performance_data)
df_performance.to_excel(writer, sheet_name='Performance_4PCT', index=False)
print("✓ Sheet 6: Performance Dashboard created")

# ============================================================
# SHEET 7: TRADING RULES
# ============================================================

rules_data = {
    'Rule_Category': [
        '=== ENTRY RULES (AGGRESSIVE) ===',
        'Entry 1', 'Entry 2', 'Entry 3', 'Entry 4', 'Entry 5',
        '',
        '=== EXIT RULES (LARGER TARGETS) ===',
        'Exit 1', 'Exit 2', 'Exit 3', 'Exit 4', 'Exit 5',
        '',
        '=== RISK RULES (CRITICAL) ===',
        'Risk 1', 'Risk 2', 'Risk 3', 'Risk 4', 'Risk 5', 'Risk 6'
    ],
    'Rule': [
        '',
        'Enter on pullbacks to 20 EMA in strong uptrends',
        'Enter breakouts with 1.5x+ relative volume',
        'RSI between 40-65 (momentum with room)',
        'Only trade stocks with ATR 2.5-5%',
        'Minimum R:R ratio of 2:1',
        '',
        '',
        'Stop-loss at 1.75x ATR (wider for volatility)',
        'Target 1 at 2.5x ATR (~5-6% move)',
        'Target 2 at 4x ATR (~8-10% move)',
        'Move stop to breakeven at +3%',
        'Trail stop at 2x ATR after +5%',
        '',
        '',
        'Max 1.5% risk per trade',
        'Max 8 concurrent positions',
        'Daily loss limit: 2% - STOP TRADING',
        'Weekly loss limit: 5% - STOP TRADING',
        'Max 30% in single sector',
        '2 consecutive losses = reduce size 50%'
    ],
    'Rationale': [
        '',
        'Higher probability entries with trend',
        'Volume confirms institutional interest',
        'Sweet spot for momentum continuation',
        'Need volatility for 5%+ moves in days',
        'Maintains positive expectancy',
        '',
        '',
        'Wider stop for volatile stocks, prevents whipsaw',
        'Realistic target for 3-5 day holds',
        'Let winners run for home runs',
        'Protect capital once trade works',
        'Capture extended moves',
        '',
        '',
        'Slightly higher for aggressive returns',
        'More positions for 12 trades/month',
        'ABSOLUTE RULE - protects account',
        'ABSOLUTE RULE - survive bad weeks',
        'Diversification with higher activity',
        'Prevents revenge trading'
    ]
}

df_rules = pd.DataFrame(rules_data)
df_rules.to_excel(writer, sheet_name='Trading_Rules_4PCT', index=False)
print("✓ Sheet 7: Trading Rules created")

# ============================================================
# SHEET 8: MONTHLY TRACKER
# ============================================================

starting = 50000
monthly_return = 0.04
balances = [starting]
for i in range(12):
    balances.append(balances[-1] * (1 + monthly_return))

monthly_tracker = {
    'Month': ['Starting', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'Target_Balance': [round(b, 2) for b in balances],
    'Actual_Balance': [50000, 52285, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'Target_PnL': [0] + [round(balances[i] * monthly_return, 2) for i in range(12)],
    'Actual_PnL': [0, 2285, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'Target_Return': [''] + ['4.00%'] * 12,
    'Actual_Return': ['', '4.57%', '', '', '', '', '', '', '', '', '', '', ''],
    'Target_Met': ['', 'YES', '', '', '', '', '', '', '', '', '', '', ''],
    'Trades': [0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'Win_Rate': ['', '64%', '', '', '', '', '', '', '', '', '', '', ''],
    'Notes': ['Initial Capital', 'Strong start!', '', '', '', '', '', '', '', '', '', '', '']
}

df_monthly = pd.DataFrame(monthly_tracker)
df_monthly.to_excel(writer, sheet_name='Monthly_Tracker_4PCT', index=False)
print("✓ Sheet 8: Monthly Tracker created")

# ============================================================
# SHEET 9: WATCHLIST TEMPLATE
# ============================================================

watchlist_data = {
    'Symbol': ['NVDA', 'AMD', 'TSLA', '', '', '', '', '', '', ''],
    'Company': ['NVIDIA Corp', 'AMD', 'Tesla Inc', '', '', '', '', '', '', ''],
    'Current_Price': [875.50, 165.80, 248.30, '', '', '', '', '', '', ''],
    'Entry_Level': [850.00, 160.00, 240.00, '', '', '', '', '', '', ''],
    'Stop_Loss': [820.00, 152.00, 228.00, '', '', '', '', '', '', ''],
    'Target_1': [900.00, 175.00, 265.00, '', '', '', '', '', '', ''],
    'Setup_Type': ['PULLBACK', 'MOMENTUM', 'PULLBACK', '', '', '', '', '', '', ''],
    'R_R_Ratio': [1.67, 1.88, 2.08, '', '', '', '', '', '', ''],
    'Alert_Set': ['YES', 'YES', 'YES', '', '', '', '', '', '', ''],
    'Priority': ['HIGH', 'HIGH', 'MEDIUM', '', '', '', '', '', '', ''],
    'Notes': ['Watch for EMA bounce', 'Strong momentum', 'Wait for pullback', '', '', '', '', '', '', '']
}

df_watchlist = pd.DataFrame(watchlist_data)
df_watchlist.to_excel(writer, sheet_name='Watchlist', index=False)
print("✓ Sheet 9: Watchlist created")

# ============================================================
# SHEET 10: GROWTH PROJECTION
# ============================================================

years = 3
months_total = years * 12
projections = []

balance = 50000
for month in range(months_total + 1):
    projections.append({
        'Month': month,
        'Balance_4PCT': round(balance, 2),
        'Balance_3PCT': round(50000 * (1.03 ** month), 2),
        'Balance_2PCT': round(50000 * (1.02 ** month), 2),
        'Monthly_Income_4PCT': round(balance * 0.04, 2) if month > 0 else 0
    })
    if month > 0:
        balance = balance * 1.04

df_projections = pd.DataFrame(projections)
df_projections.to_excel(writer, sheet_name='Growth_Projection', index=False)
print("✓ Sheet 10: Growth Projection created")

# ============================================================
# SAVE AND CLOSE
# ============================================================

writer.close()

print("\n" + "=" * 60)
print("SUCCESS! Your trading system has been created!")
print("=" * 60)
print(f"\n📁 File saved to: {output_file}")
print("\n📊 Sheets included:")
print("   1. System_Overview - Strategy parameters")
print("   2. Stock_Screener_4PCT - Find volatile quality stocks")
print("   3. Technical_Analysis_4PCT - Entry/Exit levels")
print("   4. Position_Calculator_4PCT - Risk-based sizing")
print("   5. Trade_Journal_4PCT - Track your trades")
print("   6. Performance_4PCT - Monitor vs 4% target")
print("   7. Trading_Rules_4PCT - Your rule set")
print("   8. Monthly_Tracker_4PCT - Compound growth tracking")
print("   9. Watchlist - Track potential setups")
print("   10. Growth_Projection - 3-year projection")
print("\n" + "=" * 60)
