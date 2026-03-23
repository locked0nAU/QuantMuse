#!/usr/bin/env python3
"""
图表库和WebSocket功能演示
展示Plotly、Matplotlib图表和WebSocket实时数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import pandas as pd
import numpy as np
import logging

# 导入我们的模块
from data_service.visualization import PlotlyChartGenerator
from data_service.realtime import RealTimeDataFeed
from data_service.factors import FactorCalculator

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def generate_sample_data():
    """生成示例数据"""
    print("📊 生成示例数据...")
    
    # 生成价格数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    symbols = ['AAPL', 'GOOGL', 'TSLA']
    
    market_data = {}
    for symbol in symbols:
        base_price = np.random.uniform(100, 500)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # 生成OHLCV数据
        ohlcv_data = []
        for i, price in enumerate(prices):
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else price
            volume = np.random.randint(1000000, 10000000)
            
            ohlcv_data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        
        market_data[symbol] = pd.DataFrame(ohlcv_data, index=dates)
    
    return market_data

def demo_plotly_charts():
    """演示Plotly图表功能"""
    print("\n📈 演示Plotly图表功能")
    print("=" * 50)
    
    # 生成数据
    market_data = generate_sample_data()
    
    # 初始化图表生成器
    chart_generator = PlotlyChartGenerator()
    
    # 1. K线图
    print("1. 创建K线图...")
    symbol = 'AAPL'
    data = market_data[symbol]
    
    candlestick_fig = chart_generator.create_candlestick_chart(
        data=data,
        symbol=symbol,
        title=f"{symbol} K线图示例"
    )
    
    # 保存图表
    candlestick_fig.write_html(f"charts/{symbol}_candlestick.html")
    print(f"   ✅ K线图已保存到 charts/{symbol}_candlestick.html")
    
    # 2. 技术分析图
    print("2. 创建技术分析图...")
    
    # 添加技术指标
    data['sma_20'] = data['close'].rolling(20).mean()
    data['ema_20'] = data['close'].ewm(span=20).mean()
    data['rsi'] = calculate_rsi(data['close'])
    
    # 布林带
    data['bb_upper'] = data['close'].rolling(20).mean() + 2 * data['close'].rolling(20).std()
    data['bb_lower'] = data['close'].rolling(20).mean() - 2 * data['close'].rolling(20).std()
    
    tech_fig = chart_generator.create_technical_analysis_chart(
        data=data,
        symbol=symbol,
        indicators=['sma', 'ema', 'bollinger']
    )
    
    tech_fig.write_html(f"charts/{symbol}_technical.html")
    print(f"   ✅ 技术分析图已保存到 charts/{symbol}_technical.html")
    
    # 3. 因子分析图
    print("3. 创建因子分析图...")
    
    # 生成因子数据
    factor_calc = FactorCalculator()
    factor_data = pd.DataFrame()
    
    for symbol in symbols:
        symbol_data = market_data[symbol]
        factors = factor_calc.calculate_all_factors(
            symbol=symbol,
            prices=symbol_data['close'],
            volumes=symbol_data['volume']
        )
        
        for factor_name, factor_value in factors.items():
            factor_data.loc[symbol, factor_name] = factor_value
    
    factor_fig = chart_generator.create_factor_analysis_chart(
        factor_data=factor_data,
        factor_names=['momentum_20d', 'volatility', 'price_vs_ma20']
    )
    
    factor_fig.write_html("charts/factor_analysis.html")
    print("   ✅ 因子分析图已保存到 charts/factor_analysis.html")
    
    # 4. 投资组合表现图
    print("4. 创建投资组合表现图...")
    
    # 模拟投资组合数据
    portfolio_returns = np.random.normal(0.001, 0.02, len(dates))
    equity_curve = pd.Series((1 + pd.Series(portfolio_returns)).cumprod(), index=dates)
    
    # 模拟基准数据
    benchmark_returns = np.random.normal(0.0008, 0.015, len(dates))
    benchmark = pd.Series((1 + pd.Series(benchmark_returns)).cumprod(), index=dates)
    
    # 模拟交易数据
    trades_data = []
    for i in range(10):
        trade_date = dates[np.random.randint(0, len(dates))]
        trades_data.append({
            'timestamp': trade_date,
            'price': np.random.uniform(100, 500),
            'side': np.random.choice(['buy', 'sell']),
            'quantity': np.random.randint(100, 1000)
        })
    
    trades_df = pd.DataFrame(trades_data)
    
    portfolio_fig = chart_generator.create_portfolio_performance_chart(
        equity_curve=equity_curve,
        benchmark=benchmark,
        trades=trades_df
    )
    
    portfolio_fig.write_html("charts/portfolio_performance.html")
    print("   ✅ 投资组合表现图已保存到 charts/portfolio_performance.html")

def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

async def demo_websocket():
    """演示WebSocket功能"""
    print("\n🌐 演示WebSocket功能")
    print("=" * 50)
    
    # 创建实时数据流
    real_time_feed = RealTimeDataFeed(exchanges=["binance"])
    
    # 添加回调函数
    async def on_tick(tick):
        print(f"📊 收到 {tick.symbol} 价格: ${tick.price:.2f} 时间: {tick.timestamp}")
    
    async def on_snapshot(snapshot):
        print(f"📈 {snapshot.symbol} 快照: O:{snapshot.open:.2f} H:{snapshot.high:.2f} L:{snapshot.low:.2f} C:{snapshot.close:.2f}")
    
    async def on_alert(alert):
        print(f"🚨 警报: {alert['symbol']} {alert['alert_type']} 当前值: {alert['current_value']:.2f}")
    
    real_time_feed.add_tick_callback(on_tick)
    real_time_feed.add_snapshot_callback(on_snapshot)
    real_time_feed.add_alert_callback(on_alert)
    
    # 设置价格警报
    real_time_feed.set_price_alert("btcusdt", "high", 50000)
    real_time_feed.set_price_alert("btcusdt", "low", 40000)
    
    print("🔌 启动WebSocket连接...")
    try:
        # 启动实时数据流
        await real_time_feed.start(symbols=["btcusdt", "ethusdt"])
        
        # 运行一段时间
        print("⏱️ 运行30秒接收实时数据...")
        await asyncio.sleep(30)
        
        # 停止
        await real_time_feed.stop()
        print("✅ WebSocket演示完成")
        
    except Exception as e:
        print(f"❌ WebSocket错误: {e}")
        print("💡 注意: 这需要有效的API密钥才能连接到交易所")

def demo_matplotlib_charts():
    """演示Matplotlib图表功能"""
    print("\n📊 演示Matplotlib图表功能")
    print("=" * 50)
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.patches import Rectangle
        
        # 生成数据
        market_data = generate_sample_data()
        symbol = 'AAPL'
        data = market_data[symbol]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 1. K线图
        print("1. 创建Matplotlib K线图...")
        
        # 绘制K线
        for i, (date, row) in enumerate(data.iterrows()):
            color = 'green' if row['close'] >= row['open'] else 'red'
            
            # 实体
            rect = Rectangle((i-0.3, min(row['open'], row['close'])), 
                           0.6, abs(row['close'] - row['open']), 
                           facecolor=color, edgecolor='black')
            ax1.add_patch(rect)
            
            # 影线
            ax1.plot([i, i], [row['low'], row['high']], color='black', linewidth=1)
        
        ax1.set_title(f'{symbol} K线图 (Matplotlib)')
        ax1.set_ylabel('价格')
        ax1.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax1.set_xticks(range(0, len(data), 10))
        ax1.set_xticklabels([data.index[i].strftime('%Y-%m-%d') for i in range(0, len(data), 10)], rotation=45)
        
        # 2. 成交量图
        print("2. 创建成交量图...")
        
        ax2.bar(range(len(data)), data['volume'], alpha=0.7, color='blue')
        ax2.set_title('成交量')
        ax2.set_ylabel('成交量')
        ax2.set_xlabel('日期')
        ax2.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax2.set_xticks(range(0, len(data), 10))
        ax2.set_xticklabels([data.index[i].strftime('%Y-%m-%d') for i in range(0, len(data), 10)], rotation=45)
        
        plt.tight_layout()
        plt.savefig('charts/matplotlib_candlestick.png', dpi=300, bbox_inches='tight')
        print("   ✅ Matplotlib图表已保存到 charts/matplotlib_candlestick.png")
        
        # 3. 技术指标图
        print("3. 创建技术指标图...")
        
        fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 价格和移动平均线
        ax3.plot(data.index, data['close'], label='收盘价', linewidth=2)
        ax3.plot(data.index, data['close'].rolling(20).mean(), label='SMA 20', linewidth=2)
        ax3.plot(data.index, data['close'].ewm(span=20).mean(), label='EMA 20', linewidth=2)
        
        ax3.set_title(f'{symbol} 技术指标')
        ax3.set_ylabel('价格')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # RSI
        rsi = calculate_rsi(data['close'])
        ax4.plot(data.index, rsi, label='RSI', linewidth=2, color='purple')
        ax4.axhline(y=70, color='r', linestyle='--', alpha=0.7)
        ax4.axhline(y=30, color='g', linestyle='--', alpha=0.7)
        ax4.fill_between(data.index, 70, 100, alpha=0.3, color='red')
        ax4.fill_between(data.index, 0, 30, alpha=0.3, color='green')
        
        ax4.set_ylabel('RSI')
        ax4.set_xlabel('日期')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('charts/matplotlib_technical.png', dpi=300, bbox_inches='tight')
        print("   ✅ 技术指标图已保存到 charts/matplotlib_technical.png")
        
    except ImportError:
        print("❌ Matplotlib未安装，跳过Matplotlib演示")
    except Exception as e:
        print(f"❌ Matplotlib图表创建失败: {e}")

def create_charts_directory():
    """创建图表目录"""
    if not os.path.exists('charts'):
        os.makedirs('charts')
        print("📁 创建charts目录")

async def main():
    """主函数"""
    setup_logging()
    
    print("🚀 图表库和WebSocket功能演示")
    print("=" * 60)
    
    # 创建目录
    create_charts_directory()
    
    try:
        # 演示Plotly图表
        demo_plotly_charts()
        
        # 演示Matplotlib图表
        demo_matplotlib_charts()
        
        # 演示WebSocket（可选）
        print("\n❓ 是否要演示WebSocket功能？(需要API密钥)")
        print("   输入 'y' 继续，其他键跳过...")
        
        # 这里简化处理，直接跳过WebSocket演示
        print("⏭️ 跳过WebSocket演示（需要API密钥）")
        
        print("\n✅ 演示完成！")
        print("\n📋 功能总结:")
        print("  • Plotly图表: K线图、技术分析、因子分析、投资组合表现")
        print("  • Matplotlib图表: K线图、技术指标、成交量")
        print("  • WebSocket支持: 实时数据流、价格警报、回调处理")
        print("  • 图表导出: HTML、PNG、PDF格式")
        
        print("\n📁 生成的图表文件:")
        print("  • charts/AAPL_candlestick.html - K线图")
        print("  • charts/AAPL_technical.html - 技术分析图")
        print("  • charts/factor_analysis.html - 因子分析图")
        print("  • charts/portfolio_performance.html - 投资组合表现图")
        print("  • charts/matplotlib_candlestick.png - Matplotlib K线图")
        print("  • charts/matplotlib_technical.png - Matplotlib技术指标图")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 