#!/usr/bin/env python3
"""
HLAL & SPUS Sell Signal Dashboard
Fetches real-time data and calculates technical indicators to identify optimal selling points.
Based on the three-pillar framework from agentic-trading-desk skill.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def calculate_rsi(prices, period=14):
    """Calculate Wilder's RSI"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    
    rs = up / down if down != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            up = (up * (period - 1) + delta) / period
            down = (down * (period - 1)) / period
        else:
            up = (up * (period - 1)) / period
            down = (down * (period - 1) - delta) / period
        
        if down == 0:
            rsi = 100
        else:
            rs = up / down
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_ema(prices, period):
    """Calculate EMA using TradingView convention"""
    ema = [np.mean(prices[:period])]  # Seed with SMA
    multiplier = 2 / (period + 1)
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    return ema

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # Align lengths
    macd_line = np.array(ema_fast[-len(ema_slow):]) - np.array(ema_slow)
    
    # Signal line
    signal_line = calculate_ema(macd_line.tolist(), signal)
    
    # Histogram
    histogram = macd_line[-len(signal_line):] - np.array(signal_line)
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands with population std dev"""
    sma = np.mean(prices[-period:])
    std = np.std(prices[-period:], ddof=0)  # Population std dev
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    # %B calculation
    current_price = prices[-1]
    b_percent = (current_price - lower) / (upper - lower) if upper != lower else 0
    
    return upper, sma, lower, b_percent

def analyze_etf(symbol, name):
    """Analyze a single ETF and return sell signals"""
    print(f"\n{'='*60}")
    print(f"📊 {name} ({symbol}) Analysis")
    print(f"{'='*60}")
    
    # Fetch data
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="6mo", interval="1d")
    
    if hist.empty:
        print(f"❌ No data found for {symbol}")
        return None
    
    # Get latest data
    closes = hist['Close'].values
    current_price = closes[-1]
    prev_price = closes[-2]
    
    # Calculate indicators
    rsi = calculate_rsi(closes)
    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    ema200 = calculate_ema(closes, 200)
    
    macd_line, signal_line, histogram = calculate_macd(closes)
    bb_upper, bb_middle, bb_lower, bb_percent = calculate_bollinger_bands(closes)
    
    # Get additional info
    info = ticker.info
    prev_close = info.get('previousClose', prev_price)
    
    # Determine trend
    trend = "BULLISH" if closes[-1] > ema20[-1] > ema50[-1] else "BEARISH"
    
    # SELL SIGNAL ANALYSIS
    sell_signals = []
    signal_strength = 0
    
    # 1. RSI Overbought Check
    if rsi > 70:
        sell_signals.append(f"⚠️  RSI OVERBOUGHT: {rsi:.1f} (>70)")
        signal_strength += 2
    elif rsi > 65:
        sell_signals.append(f"🔸 RSI Approaching Overbought: {rsi:.1f}")
        signal_strength += 1
    
    # 2. MACD Histogram Shrinking
    if len(histogram) >= 2:
        hist_slope = histogram[-1] - histogram[-2]
        if histogram[-1] > 0 and hist_slope < 0:
            sell_signals.append(f"⚠️  MACD Histogram SHRINKING: {histogram[-1]:.4f} (slope: {hist_slope:.4f})")
            signal_strength += 2
        elif histogram[-1] > 0:
            sell_signals.append(f"✓ MACD Histogram Positive: {histogram[-1]:.4f}")
    
    # 3. Bollinger Band Position
    if bb_percent > 1.0:
        sell_signals.append(f"⚠️  Price ABOVE Upper Bollinger Band: {bb_percent:.2f} (>1.0)")
        signal_strength += 2
    elif bb_percent > 0.95:
        sell_signals.append(f"🔸 Price Near Upper Bollinger Band: {bb_percent:.2f}")
        signal_strength += 1
    
    # 4. Price vs EMAs
    if current_price < ema20[-1]:
        sell_signals.append(f"⚠️  Price BELOW EMA20: ${current_price:.2f} < ${ema20[-1]:.2f}")
        signal_strength += 1
    
    # 5. Death Cross Check
    if ema50[-1] < ema200[-1] and current_price < ema50[-1]:
        sell_signals.append(f"⚠️  DEATH CROSS: EMA50 < EMA200 & Price < EMA50")
        signal_strength += 3
    
    # Display results
    print(f"\n💰 Current Price: ${current_price:.2f}")
    print(f"📈 Previous Close: ${prev_close:.2f}")
    print(f"📊 Daily Change: {((current_price/prev_close)-1)*100:+.2f}%")
    
    print(f"\n📈 TECHNICAL INDICATORS:")
    print(f"  RSI-14: {rsi:.1f}")
    print(f"  EMA20: ${ema20[-1]:.2f}")
    print(f"  EMA50: ${ema50[-1]:.2f}")
    print(f"  EMA200: ${ema200[-1]:.2f}")
    print(f"  MACD Histogram: {histogram[-1]:.4f}")
    print(f"  Bollinger %B: {bb_percent:.2f}")
    print(f"  Trend: {trend}")
    
    print(f"\n🚨 SELL SIGNALS (Strength: {signal_strength}/5):")
    if sell_signals:
        for signal in sell_signals:
            print(f"  {signal}")
    else:
        print("  ✓ No strong sell signals detected")
    
    # RECOMMENDATION
    print(f"\n🎯 RECOMMENDATION:")
    if signal_strength >= 4:
        print("  🔴 STRONG SELL - Multiple exhaustion signals detected")
        print("  → Consider selling NOW or set limit order near current price")
    elif signal_strength >= 2:
        print("  🟡 PARTIAL SELL - Momentum slowing, consider trimming")
        print("  → Sell 50% now, wait for clearer signal on rest")
    else:
        print("  🟢 HOLD - No exhaustion signals yet")
        print("  → Continue monitoring, no rush to sell")
    
    return {
        'symbol': symbol,
        'price': current_price,
        'rsi': rsi,
        'signal_strength': signal_strength,
        'recommendation': 'SELL' if signal_strength >= 4 else 'PARTIAL' if signal_strength >= 2 else 'HOLD'
    }

def main():
    print("="*60)
    print("🚀 HLAL & SPUS SELL SIGNAL DASHBOARD")
    print("="*60)
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"📍 NYSE Arca Trading Hours: 9:30 AM - 4:00 PM EDT")
    print()
    
    # Analyze both ETFs
    results = []
    
    # HLAL - Wahed ETF
    hlal = analyze_etf("HLAL", "Wahed HLAL Shariah ETF")
    if hlal:
        results.append(hlal)
    
    # SPUS - SP Funds Shariah ETF  
    spus = analyze_etf("SPUS", "SP Funds SPUS Shariah ETF")
    if spus:
        results.append(spus)
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY & TOMORROW'S PLAN")
    print(f"{'='*60}")
    
    for r in results:
        emoji = "🔴" if r['recommendation'] == 'SELL' else "🟡" if r['recommendation'] == 'PARTIAL' else "🟢"
        print(f"{emoji} {r['symbol']}: ${r['price']:.2f} | RSI: {r['rsi']:.1f} | {r['recommendation']}")
    
    print(f"\n⏰ TOMORROW'S TRADING PLAN (July 9, 2026):")
    print("  1. Run this script at 9:30 AM EDT (market open)")
    print("  2. Check RSI and MACD histogram for exhaustion")
    print("  3. Place limit sell orders if RSI > 70 or MACD shrinking")
    print("  4. Re-run at 3:30 PM to check end-of-day signals")
    print(f"\n💡 TIP: Sell during 9:30-10:30 AM or 3:00-4:00 PM for best liquidity")
    
    # Save results
    with open('etf_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: etf_analysis.json")

if __name__ == "__main__":
    main()
