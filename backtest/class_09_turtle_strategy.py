"""
    简单EMA策略.

"""
from vnpy.app.cta_strategy.template import CtaTemplate
from typing import Any
from vnpy.trader.object import BarData, Interval, TickData, TradeData, OrderData, Direction, Offset
from vnpy.trader.utility import BarGenerator, ArrayManager
from datetime import datetime
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.base import StopOrder
import talib


class BitquantTurtleStrategy(CtaTemplate):

    entry_window = 30
    exit_window = 13
    atr_window = 14

    risk_loss_money = 20000  # 1% - 2%

    long_entry_price = 0.0  # 多头进场价格
    short_entry_price = 0.0   # 空头进场价格
    long_stop_loss_price = 0.0
    short_stop_loss_price = 0.0
    atr_value = 0.0  # atr值

    trade_highest_price = 0.0
    trade_lowest_price = 0.0

    parameters = ["entry_window", "exit_window", "atr_window", "risk_loss_money"]
    variables = ["long_entry_price", "short_entry_price", "atr_value", "long_stop_loss_price",
                 "short_stop_loss_price", "trade_highest_price", "trade_lowest_price"]

    def __init__(
            self,
            cta_engine: Any,
            strategy_name: str,
            vt_symbol: str,
            setting: dict):
        super(BitquantTurtleStrategy, self).__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_hour_bar, interval=Interval.HOUR)
        self.am = ArrayManager(300)



    def on_init(self):
        print("on init")
        self.load_bar(3)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        print("on_start strategy")

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

    def on_hour_bar(self, bar: BarData):

        self.cancel_all()  # 先撤单
        self.am.update_bar(bar)

        if not self.am.inited:
            return

        entry_up, entry_dn = self.am.donchian(self.entry_window)
        exit_up, exit_dn = self.am.donchian(self.exit_window)

        if self.pos == 0:  # 没有仓位
            self.trade_highest_price = bar.high_price
            self.trade_lowest_price = bar.low_price

            self.atr_value = self.am.atr(self.atr_window)
            trade_volume = self.risk_loss_money/(self.atr_value * 2)
            self.buy(entry_up, trade_volume, stop=True)
            self.sell(entry_dn, trade_volume, stop=True)

        elif self.pos > 0:  # 有多头仓位
            self.trade_highest_price = max(self.trade_highest_price, bar.high_price)
            self.trade_lowest_price = min(self.trade_lowest_price, bar.low_price)

            # draw_back_price = self.trade_highest_price * (1-0.05)
            draw_back_price = self.trade_highest_price - self.atr_value * 4
            sell_price = max(exit_dn, self.long_stop_loss_price, draw_back_price)
            # sell_price = max(exit_dn, self.long_stop_loss_price)
            self.sell(sell_price, abs(self.pos), True)


        elif self.pos < 0:   # 有空头仓位
            self.trade_highest_price = max(self.trade_highest_price, bar.high_price)
            self.trade_lowest_price = min(self.trade_lowest_price, bar.low_price)

            # draw_back_price = self.trade_lowest_price * (1+0.05)
            draw_back_price = self.trade_lowest_price + self.atr_value * 4
            cover_price = min(exit_up, self.short_stop_loss_price, draw_back_price)
            # cover_price = min(exit_up, self.short_stop_loss_price)
            self.cover(cover_price, abs(self.pos), True)

    def on_trade(self, trade: TradeData):
        if self.pos != 0:
            if trade.direction == Direction.LONG and trade.offset == Offset.OPEN:
                self.long_entry_price = trade.price
                self.long_stop_loss_price = self.long_entry_price - 2 * self.atr_value
            elif trade.direction == Direction.SHORT and trade.offset == Offset.OPEN:
                self.short_entry_price = trade.price
                self.short_stop_loss_price = self.short_entry_price + 2 * self.atr_value

    def on_order(self, order: OrderData):
        pass

    def on_stop_order(self, stop_order: StopOrder):
        pass



if __name__ == '__main__':
    # 回测引擎初始化
    engine = BacktestingEngine()

    # 设置交易对产品的参数
    engine.set_parameters(
        vt_symbol="XBTUSD.BITMEX",  # 交易的标的
        interval=Interval.MINUTE,
        start=datetime(2018, 1, 1),  # 开始时间
        rate=7.5 / 10000,  # 手续费
        slippage=0.5,  # 交易滑点
        size=1,  # 合约乘数
        pricetick=0.5,  # 8500.5 8500.01
        capital=1_000_000,  # 初始资金
        # end=datetime(2018, 6, 1)  # 结束时间
    )

    # 添加策略
    engine.add_strategy(BitquantTurtleStrategy, {})

    # 加载
    engine.load_data()

    # # # 运行回测
    # engine.run_backtesting()
    #
    # # 统计结果
    # engine.calculate_result()
    #
    # # 计算策略的统计指标 Sharp ratio, drawdown
    # engine.calculate_statistics()
    #
    # # 绘制图表
    # engine.show_chart()
    """
    "total_return": total_return,
    "annual_return": annual_return,
    "daily_return": daily_return,
    "return_std": return_std,
    "sharpe_ratio": sharpe_ratio,
    "return_drawdown_ratio": return_drawdown_ratio,
    """
    setting = OptimizationSetting()
    setting.set_target("sharpe_ratio")
    setting.add_parameter("entry_window", 10, 300, 1)
    setting.add_parameter("exit_window", 5, 50, 1)
    setting.add_parameter("atr_window", 10, 50, 1)
    engine.run_ga_optimization(setting)  # 遗传算法优化.

    # engine.run_optimization()  # 多线程优化.






    def run(self):
                '''
                尋找交易訊號1時做多,-1時做空,1並實時更新equity,最後關閉倉位,
                並增加止損機制
                '''
                
                for i in range(1 , len(self.data)):
                    current_price = self.data.loc[i , 'Close']
                    current_atr = self.data.loc[i , 'atr']
                    if self.postion == 0:
                        if self.data.loc[i , 'signal'] == 1 :
                           self.long(row_index=i)
                           self.entry_price = current_price
                        elif self.data.loc[i , 'signal'] == -1 :
                           self.short(row_index=i)
                           self.entry_price = current_price
                    
                    elif self.position > 0 : #有多倉
                        donchianHighExit = self.data.loc[i , 'exit_dn']
                        long_stop_loss = self.entry_price - 2 * current_atr
                        sell_price = max(donchianHighExit , long_stop_loss)
                        self.data.loc[i , 'position'] = self.position
                        if current_price < sell_price :
                            self.sell(row_index = i , pric = current_price)
                            self.entry_price = None
                        else:
                            self.data.loc[i , 'position'] = self.position
                            if i != self.data.index[-1] :
                               if self.position > 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                               elif self.position < 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                                
                    if self.position < 0 : #有空倉
                        donchianlowExit = self.data.loc[i , 'exit_up']
                        shoet_stop_loss = self.entry_price + 2 * current_atr
                        cover_price = min(donchianlowExit , shoet_stop_loss)
                       
                        if current_price > cover_price :
                            self.cover(row_index = i , price = current_price)
                            self.entry_price = None
                        else:
                            self.data.loc[i , 'position'] = self.position
                            if i != self.data.index[-1] :
                               if self.position > 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                               elif self.position < 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                          
                
                self.max_drawdown = self.calculate_max_drawdown()
                
                self.close_position()
                
                return self.data[['Datetime','Close' , 'signal' , 'equity' , 'position' , 'transaction']]
            
            
            
            
            


    def run(self):
                '''
                尋找交易訊號1時做多,-1時做空,1並實時更新equity,最後關閉倉位,
                並增加止損機制
                '''
                
                for i in range(1 , len(self.data)):
                    current_price = self.data.loc[i , 'Close']
                    current_atr = self.data.loc[i , 'atr']
                    
                    if self.data.loc[i , 'signal'] == 1 :
                        self.cover(row_index = i ,price = current_price)
                        self.long(row_index=i)
                        self.entry_price = current_price
                    elif self.data.loc[i , 'signal'] == -1 :
                        self.sell(row_index = i , price = current_price)
                        self.short(row_index=i)
                        self.entry_price = current_price
                    else :
                        self.data.loc[i , 'position'] = self.position
                        if i != self.data.index[-1] :
                            if self.position > 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                            elif self.position < 0 :
                                self.data.loc[i , 'equity'] = self.get_total_equity(price = current_price)
                                
                    if self.position > 0 :
                        stop_loss_price = self.entry_price - 2 * current_atr
                        if current_price < stop_loss_price :
                            self.sell(row_index = i , price = current_price)
                            self.entry_price = None
                            continue
                    
                    elif self.position < 0 :
                        stop_loss_price = self.entry_price + 2 * current_atr
                        if current_price > stop_loss_price :
                            self.cover(row_index = i , price = current_price)
                            self.entry_price = None
                            continue
                
                self.max_drawdown = self.calculate_max_drawdown()
                
                self.close_position()
                
                return self.data[['Datetime','Close' , 'signal' , 'equity' , 'position' , 'transaction']]