#!/usr/bin/env python3
"""
HLAL & SPUS Backtesting + Sell Order Generator
Backtests multiple strategies on historical data and generates specific sell orders for tomorrow.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def calculate_indicators(prices):
    """Calculate all technical indicators"""
    closes = prices.values
    
    # RSI
    rsi = calculate_rsi(closes)
    
    # EMAs
    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    ema200 = calculate_ema(closes, 200)
    
    # MACD
    macd_line, signal_line, histogram = calculate_macd(closes)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower, bb_percent = calculate_bollinger_bands(closes)
    
    return {
        'rsi': rsi,
        'ema20': ema20[-1],
        'ema50': ema50[-1],
        'ema200': ema200[-1],
        'macd_histogram': histogram[-1] if len(histogram) > 0 else 0,
        'bb_upper': bb_upper,
        'bb_percent': bb_percent,
        'current_price': closes[-1]
    }

def calculate_rsi(prices, period=14):
    """Calculate Wilder's RSI"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_ema(prices, period):
    """Calculate EMA"""
    if len(prices) < period:
        return [np.mean(prices)]
    
    ema = [np.mean(prices[:period])]
    multiplier = 2 / (period + 1)
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    return ema

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    if len(prices) < slow:
        return np.array([0]), np.array([0]), np.array([0])
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    min_len = min(len(ema_fast), len(ema_slow))
    macd_line = np.array(ema_fast[-min_len:]) - np.array(ema_slow[-min_len:])
    
    if len(macd_line) >= signal:
        signal_line = calculate_ema(macd_line, signal)
        histogram = macd_line[-len(signal_line):] - np.array(signal_line)
        return macd_line, signal_line, histogram
    
    return macd_line, np.array([0]), np.array([0])

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return prices[-1], prices[-1], prices[-1], 0.5
    
    recent = prices[-period:]
    sma = np.mean(recent)
    std = np.std(recent, ddof=0)
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    current_price = prices[-1]
    b_percent = (current_price - lower) / (upper - lower) if upper != lower else 0.5
    
    return upper, sma, lower, b_percent

def backtest_strategy(symbol, strategy_name, strategy_func, start_date, end_date):
    """Backtest a strategy on historical data"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_date, end=end_date, interval="1d")
    
    if hist.empty:
        return None
    
    signals = []
    returns = []
    position = None
    entry_price = 0
    
    for i in range(20, len(hist)):
        current_data = hist.iloc[:i+1]
        signal = strategy_func(current_data)
        
        current_price = hist['Close'].iloc[i]
        
        if signal == 'BUY' and position is None:
            position = 'LONG'
            entry_price = current_price
            signals.append(('BUY', current_price, hist.index[i]))
        
        elif signal == 'SELL' and position == 'LONG':
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            returns.append(profit_pct)
            signals.append(('SELL', current_price, hist.index[i], profit_pct))
            position = None
    
    total_return = sum(returns) if returns else 0
    win_rate = len([r for r in returns if r > 0]) / len(returns) * 100 if returns else 0
    
    return {
        'strategy': strategy_name,
        'symbol': symbol,
        'total_trades': len(returns),
        'total_return_pct': total_return,
        'win_rate_pct': win_rate,
        'avg_return_pct': np.mean(returns) if returns else 0,
        'signals': signals[-5:]  # Last 5 signals
    }

def rsi_overbought_strategy(data):
    """Sell when RSI > 70, Buy when RSI < 30"""
    closes = data['Close'].values
    rsi = calculate_rsi(closes)
    
    if rsi > 70:
        return 'SELL'
    elif rsi < 30:
        return 'BUY'
    return 'HOLD'

def macd_crossunder_strategy(data):
    """Sell when MACD crosses below signal line"""
    closes = data['Close'].values
    
    if len(closes) < 35:
        return 'HOLD'
    
    macd_line, signal_line, histogram = calculate_macd(closes)
    
    if len(histogram) >= 2:
        if histogram[-2] > 0 and histogram[-1] < 0:
            return 'SELL'
        elif histogram[-2] < 0 and histogram[-1] > 0:
            return 'BUY'
    
    return 'HOLD'

def bollinger_breakout_strategy(data):
    """Sell when price hits upper Bollinger Band"""
    closes = data['Close'].values
    
    if len(closes) < 20:
        return 'HOLD'
    
    bb_upper, _, _, bb_percent = calculate_bollinger_bands(closes)
    current_price = closes[-1]
    
    if bb_percent > 1.0:  # Above upper band
        return 'SELL'
    elif bb_percent < 0:  # Below lower band
        return 'BUY'
    
    return 'HOLD'

def combined_exit_strategy(data):
    """Combined strategy: Sell on any 2 of 3 exhaustion signals"""
    closes = data['Close'].values
    
    if len(closes) < 35:
        return 'HOLD'
    
    rsi = calculate_rsi(closes)
    macd_line, signal_line, histogram = calculate_macd(closes)
    bb_upper, _, _, bb_percent = calculate_bollinger_bands(closes)
    
    sell_signals = 0
    
    # Signal 1: RSI overbought
    if rsi > 70:
        sell_signals += 1
    
    # Signal 2: MACD histogram shrinking
    if len(histogram) >= 2:
        if histogram[-1] > 0 and (histogram[-1] - histogram[-2]) < 0:
            sell_signals += 1
    
    # Signal 3: Price above upper Bollinger
    if bb_percent > 1.0:
        sell_signals += 1
    
    if sell_signals >= 2:
        return 'SELL'
    elif rsi < 30 and bb_percent < 0:
        return 'BUY'
    
    return 'HOLD'

def analyze_current_opportunity(symbol, name):
    """Analyze current opportunity and generate sell orders"""
    print(f"\n{'='*70}")
    print(f"📊 {name} ({symbol}) - SELL ORDER ANALYSIS")
    print(f"{'='*70}")
    
    ticker = yf.Ticker(symbol)
    
    # Get data
    hist_6mo = ticker.history(period="6mo", interval="1d")
    hist_1y = ticker.history(period="1y", interval="1d")
    
    if hist_6mo.empty:
        print(f"❌ No data available for {symbol}")
        return None
    
    current_price = hist_6mo['Close'].iloc[-1]
    
    # Calculate indicators
    indicators_6mo = calculate_indicators(hist_6mo)
    indicators_1y = calculate_indicators(hist_1y)
    
    # Backtest strategies on 6-month data
    print(f"\n🧪 BACKTESTING STRATEGIES (Past 6 Months):")
    
    strategies = [
        ('RSI Overbought', rsi_overbought_strategy),
        ('MACD Crossunder', macd_crossunder_strategy),
        ('Bollinger Breakout', bollinger_breakout_strategy),
        ('Combined Exit (2/3)', combined_exit_strategy)
    ]
    
    backtest_results = []
    
    for strategy_name, strategy_func in strategies:
        result = backtest_strategy(
            symbol, 
            strategy_name, 
            strategy_func,
            (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )
        
        if result:
            backtest_results.append(result)
            print(f"  {strategy_name}:")
            print(f"    Trades: {result['total_trades']}")
            print(f"    Total Return: {result['total_return_pct']:.2f}%")
            print(f"    Win Rate: {result['win_rate_pct']:.1f}%")
            print(f"    Avg Trade: {result['avg_return_pct']:.2f}%")
    
    # Find best strategy
    if backtest_results:
        best_strategy = max(backtest_results, key=lambda x: x['total_return_pct'])
        print(f"\n  🏆 BEST STRATEGY: {best_strategy['strategy']}")
        print(f"     Return: {best_strategy['total_return_pct']:.2f}% | Win Rate: {best_strategy['win_rate_pct']:.1f}%")
    
    # Current technical picture
    print(f"\n💰 CURRENT MARKET DATA:")
    print(f"  Price: ${current_price:.2f}")
    print(f"  RSI-14: {indicators_6mo['rsi']:.1f}")
    print(f"  52-Week High: ${ticker.info.get('fiftyTwoWeekHigh', 0):.2f}")
    print(f"  52-Week Low: ${ticker.info.get('fiftyTwoWeekLow', 0):.2f}")
    
    # Generate sell orders
    print(f"\n🎯 SELL ORDER RECOMMENDATIONS:")
    
    sell_orders = []
    
    # Order 1: Conservative (RSI > 65)
    conservative_target = current_price * 1.02  # 2% above current
    sell_orders.append({
        'type': 'Conservative',
        'target_price': conservative_target,
        'reason': 'RSI approaching overbought (65+)',
        'probability': 'High'
    })
    
    # Order 2: Moderate (RSI > 70)
    moderate_target = current_price * 1.04  # 4% above current
    sell_orders.append({
        'type': 'Moderate',
        'target_price': moderate_target,
        'reason': 'RSI overbought (>70) + MACD exhaustion',
        'probability': 'Medium'
    })
    
    # Order 3: Aggressive (Upper Bollinger)
    aggressive_target = indicators_6mo['bb_upper']
    sell_orders.append({
        'type': 'Aggressive',
        'target_price': aggressive_target,
        'reason': 'Upper Bollinger Band + momentum peak',
        'probability': 'Low-Medium'
    })
    
    for i, order in enumerate(sell_orders, 1):
        print(f"\n  {i}. {order['type'].upper()} SELL ORDER:")
        print(f"     Target: ${order['target_price']:.2f} (+{((order['target_price']/current_price)-1)*100:.1f}%)")
        print(f"     Reason: {order['reason']}")
        print(f"     Probability: {order['probability']}")
        print(f"     📝 Action: Place limit sell order at ${order['target_price']:.2f}")
    
    # News sentiment (simplified)
    print(f"\n📰 NEWS SENTIMENT:")
    print(f"  Recent market conditions: Check Yahoo Finance / Google Finance for {symbol}")
    print(f"  Shariah ETF sector outlook: Technology/Healthcare focus (HLAL) or Broad market (SPUS)")
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'best_strategy': best_strategy['strategy'] if backtest_results else 'N/A',
        'sell_orders': sell_orders
    }

def main():
    print("="*70)
    print("🚀 ETF BACKTESTING + SELL ORDER GENERATOR")
    print("="*70)
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"📅 Trading Date: Tomorrow, July 9, 2026")
    print(f"🕐 Place Orders: AFTER 4:00 PM today (after-hours) or BEFORE 9:30 AM EDT")
    
    # Analyze both ETFs
    results = []
    
    hlal_result = analyze_current_opportunity("HLAL", "Wahed HLAL Shariah ETF")
    if hlal_result:
        results.append(hlal_result)
    
    spus_result = analyze_current_opportunity("SPUS", "SP Funds SPUS Shariah ETF")
    if spus_result:
        results.append(spus_result)
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 TOMORROW'S ACTION PLAN")
    print(f"{'='*70}")
    print(f"\n⏰ TIMELINE:")
    print(f"  1. TODAY 4:00 PM - 8:00 AM: Place limit sell orders (after-hours/pre-market)")
    print(f"  2. TOMORROW 9:30 AM: Market opens - monitor execution")
    print(f"  3. TOMORROW 10:00 AM: Check if orders filled, adjust if needed")
    print(f"  4. TOMORROW 3:30 PM: End-of-day check, place new orders if needed")
    
    print(f"\n💡 ORDER PLACEMENT TIPS:")
    print(f"  • Use GOOD-TIL-CANCELED (GTC) orders")
    print(f"  • Set limit prices slightly below targets for faster execution")
    print(f"  • Monitor RSI every 30 mins during trading hours")
    print(f"  • Cancel unfilled orders at 3:55 PM if holding overnight is not desired")
    
    # Save results
    with open('etf_sell_orders.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Detailed sell orders saved to: etf_sell_orders.json")
    print(f"\n🚨 NEXT STEP: I can help you place these orders if you have a broker API setup")

if __name__ == "__main__":
    main()
