#!/usr/bin/env python3
"""
HLAL & SPUS Sell Order Generator - FIXED VERSION
Generates specific sell orders based on technical analysis + historical levels
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def calculate_rsi(prices, period=14):
    """Calculate RSI - FIXED VERSION"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Use Wilder's smoothing
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period):
    """Calculate EMA - FIXED"""
    if len(prices) < period:
        return [float(np.mean(prices))]
    
    ema = [float(np.mean(prices[:period]))]
    multiplier = 2 / (period + 1)
    
    for price in prices[period:]:
        ema.append((float(price) - ema[-1]) * multiplier + ema[-1])
    
    return ema

def calculate_macd(prices):
    """Calculate MACD - FIXED"""
    if len(prices) < 26:
        return 0, 0, 0
    
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    
    min_len = min(len(ema12), len(ema26))
    macd_line = np.array(ema12[-min_len:]) - np.array(ema26[-min_len:])
    
    if len(macd_line) < 9:
        return float(macd_line[-1]) if len(macd_line) > 0 else 0, 0, 0
    
    signal_line = calculate_ema(macd_line, 9)
    histogram = macd_line[-len(signal_line):] - np.array(signal_line)
    
    return float(macd_line[-1]), float(signal_line[-1]), float(histogram[-1])

def calculate_bollinger(prices):
    """Calculate Bollinger Bands - FIXED"""
    if len(prices) < 20:
        return float(prices[-1]), float(prices[-1]), float(prices[-1]), 0.5
    
    recent = prices[-20:]
    sma = float(np.mean(recent))
    std = float(np.std(recent, ddof=0))
    
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    current = float(prices[-1])
    
    if upper != lower:
        b_percent = (current - lower) / (upper - lower)
    else:
        b_percent = 0.5
    
    return upper, sma, lower, b_percent

def find_resistance_levels(prices, lookback=60):
    """Find historical resistance levels"""
    if len(prices) < lookback:
        return [float(np.max(prices))]
    
    recent_highs = prices[-lookback:]
    max_price = float(np.max(recent_highs))
    
    # Find local maxima
    resistance_levels = []
    for i in range(5, len(recent_highs) - 5):
        if all(recent_highs[i] >= recent_highs[i-j] for j in range(1, 6)) and \
           all(recent_highs[i] >= recent_highs[i+j] for j in range(1, 6)):
            resistance_levels.append(float(recent_highs[i]))
    
    if not resistance_levels:
        resistance_levels = [max_price]
    
    return sorted(set(resistance_levels), reverse=True)[:3]  # Top 3

def analyze_and_generate_orders(symbol, name):
    """Main analysis function"""
    print(f"\n{'='*70}")
    print(f"📊 {name} ({symbol}) - SELL ORDER GENERATOR")
    print(f"{'='*70}")
    
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="6mo", interval="1d")
    
    if hist.empty or len(hist) < 30:
        print(f"❌ Insufficient data for {symbol}")
        return None
    
    closes = hist['Close'].values
    current_price = float(closes[-1])
    
    # Calculate indicators
    rsi = calculate_rsi(closes)
    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    macd, signal, hist_macd = calculate_macd(closes)
    bb_upper, bb_middle, bb_lower, bb_pct = calculate_bollinger(closes)
    
    # Find resistance levels
    resistance = find_resistance_levels(closes)
    
    # Get 52-week high/low
    info = ticker.info
    week52_high = info.get('fiftyTwoWeekHigh', current_price * 1.05)
    week52_low = info.get('fiftyTwoWeekLow', current_price * 0.95)
    
    print(f"\n💰 CURRENT MARKET DATA:")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  RSI-14: {rsi:.1f}")
    print(f"  EMA20: ${ema20[-1]:.2f}")
    print(f"  EMA50: ${ema50[-1]:.2f}")
    print(f"  MACD Histogram: {hist_macd:.4f}")
    print(f"  Bollinger %B: {bb_pct:.2f}")
    print(f"  52-Week High: ${week52_high:.2f}")
    print(f"  52-Week Low: ${week52_low:.2f}")
    
    print(f"\n📈 RESISTANCE LEVELS (Past 60 days):")
    for i, level in enumerate(resistance, 1):
        distance = ((level / current_price) - 1) * 100
        print(f"  {i}. ${level:.2f} ({distance:+.1f}% from current)")
    
    # Generate sell orders
    print(f"\n🎯 SELL ORDER RECOMMENDATIONS:")
    
    orders = []
    
    # Order 1: Conservative (Based on resistance)
    if resistance:
        conservative_target = resistance[0]
        orders.append({
            'level': 1,
            'type': 'Conservative',
            'target': conservative_target,
            'gain_pct': ((conservative_target / current_price) - 1) * 100,
            'reason': f'Near historical resistance (${resistance[0]:.2f})',
            'priority': 'HIGH'
        })
    
    # Order 2: Technical (Upper Bollinger)
    if bb_pct > 0.8:
        technical_target = bb_upper
        orders.append({
            'level': 2,
            'type': 'Technical',
            'target': technical_target,
            'gain_pct': ((technical_target / current_price) - 1) * 100,
            'reason': 'Upper Bollinger Band + momentum',
            'priority': 'MEDIUM'
        })
    
    # Order 3: RSI Overbought
    if rsi > 60:
        rsi_target = current_price * 1.03  # 3% above current
        orders.append({
            'level': 3,
            'type': 'RSI Target',
            'target': rsi_target,
            'gain_pct': 3.0,
            'reason': f'RSI {rsi:.1f} approaching overbought',
            'priority': 'MEDIUM'
        })
    
    # Sort by target price
    orders.sort(key=lambda x: x['target'])
    
    for order in orders:
        print(f"\n  {order['level']}. {order['type'].upper()} SELL ORDER:")
        print(f"     Target: ${order['target']:.2f} (+{order['gain_pct']:.1f}%)")
        print(f"     Reason: {order['reason']}")
        print(f"     Priority: {order['priority']}")
        print(f"     📝 Action: Place LIMIT SELL at ${order['target']:.2f}")
    
    # Timing recommendation
    print(f"\n⏰ ORDER PLACEMENT TIMING:")
    print(f"  • TODAY 4:00 PM - 8:00 PM: Place after-hours limit orders")
    print(f"  • TOMORROW 7:00 AM - 9:25 AM: Place pre-market orders")
    print(f"  • Use GOOD-TIL-CANCELED (GTC) order type")
    print(f"  • Set limit price slightly BELOW target for faster fill")
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'rsi': rsi,
        'resistance_levels': resistance[:3],
        'sell_orders': orders
    }

def main():
    print("="*70)
    print("🚀 ETF SELL ORDER GENERATOR - READY TO EXECUTE")
    print("="*70)
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"📅 Trading Date: Tomorrow, July 9, 2026")
    print(f"🕐 Market Hours: 9:30 AM - 4:00 PM EDT")
    
    # Analyze both ETFs
    results = []
    
    hlal = analyze_and_generate_orders("HLAL", "Wahed HLAL Shariah ETF")
    if hlal:
        results.append(hlal)
    
    spus = analyze_and_generate_orders("SPUS", "SP Funds SPUS Shariah ETF")
    if spus:
        results.append(spus)
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 EXECUTION CHECKLIST")
    print(f"{'='*70}")
    print(f"\n✅ IMMEDIATE ACTIONS (TODAY):")
    print(f"  1. Log into your broker (Robinhood, E*TRADE, etc.)")
    print(f"  2. For each ETF, place LIMIT SELL orders at target prices")
    print(f"  3. Set order type to GTC (Good Til Canceled)")
    print(f"  4. Set limit price 0.01-0.02 BELOW target for faster execution")
    
    print(f"\n📊 ORDER SUMMARY:")
    for result in results:
        print(f"\n  {result['symbol']}:")
        for order in result['sell_orders']:
            print(f"    • ${order['target']:.2f} ({order['type']}) - {order['reason']}")
    
    print(f"\n⚠️ IMPORTANT NOTES:")
    print(f"  • These are LIMIT orders - they'll only execute at target price or better")
    print(f"  • Cancel unfilled orders by 4:00 PM if you don't want to hold overnight")
    print(f"  • Monitor RSI throughout the day - if RSI > 75, consider selling immediately")
    print(f"  • Check news for any major market events that could affect ETFs")
    
    # Save orders
    with open('sell_orders_ready.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Orders saved to: sell_orders_ready.json")
    print(f"\n🚨 NEXT STEP: Execute these orders in your brokerage account NOW!")

if __name__ == "__main__":
    main()
