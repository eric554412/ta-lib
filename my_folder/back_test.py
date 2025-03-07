import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.ticker as mticker
import numpy as np


class BackTest(object):
    def __init__(self, data, equity, commission=0.00075):

        self.data = data.copy()
        self.equity = equity
        self.commission = commission
        self.position = 0
        self.entry_price = None
        self.data['equity'] = equity
        self.data['position'] = 0
        self.data['transaction'] = None
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
        self.trade = []
        self.highest_price = 0
        self.lowest_price = 0

        self.long_trades = 0
        self.short_trades = 0
        self.winning_long_trades = 0
        self.losing_long_trades = 0
        self.winning_short_trades = 0
        self.losing_short_trades = 0

    def long(self, row_index, price):
        '''
        做多時有空頭倉位先平倉,並動態紀錄equity,並記錄進場的high和low
        '''

        # 開多倉
        amount = 10000 / price
        self.position += amount
        self.equity -= amount * price * (1 + self.commission)
        # 紀錄進場的close和high和low
        self.entry_price = price
        self.highest_price = self.data.loc[row_index, 'High']
        self.lowest_price = self.data.loc[row_index, 'Low']

        self.data.loc[row_index, 'equity'] = self.get_total_equity(price=price)
        self.data.loc[row_index, 'position'] = self.position
        self.data.loc[row_index, 'transaction'] = f'buy_{amount}_at_{price}'
        self.trade.append({'time': self.data.loc[row_index, 'Datetime'] + pd.Timedelta(hours=1),
                           'action': 'long', 'amount': amount, 'price': price,
                           'equity': self.get_total_equity(price=price)})
        self.long_trades += 1

    def short(self, row_index, price):
        '''
        做空時有多頭倉位先平倉,記錄進場的high和low
        '''

        # 開空倉
        amount = 10000 / price
        self.position -= amount
        self.equity += amount * price * (1 - self.commission)
        # 紀錄進場時的close和high和low
        self.entry_price = price
        self.highest_price = self.data.loc[row_index, 'High']
        self.lowest_price = self.data.loc[row_index, 'Low']

        self.data.loc[row_index, 'equity'] = self.get_total_equity(price=price)
        self.data.loc[row_index, 'position'] = self.position
        self.data.loc[row_index, 'transaction'] = f'short_{amount}_at_{price}'
        self.trade.append({'time': self.data.loc[row_index, 'Datetime'] + pd.Timedelta(hours=1),
                           'action': 'short', 'amount': amount, 'price': price,
                           'equity': self.get_total_equity(price=price)})
        self.short_trades += 1

    def sell(self, row_index, price):
        '''
        平多倉的函數
        '''

        if self.position > 0:
            self.equity += self.position * price * (1 - self.commission)
            self.data.loc[row_index,
                          'transaction'] = f'close_long _{self.position}_at_{price}'
            pnl = (price - self.entry_price) * self.position
            self.position = 0
            self.trade.append({'time': self.data.loc[row_index, 'Datetime'] + pd.Timedelta(hours=1),
                               'action': 'close_long', 'amount': self.position, 'price': price,
                               'equity': self.equity})

            if pnl > 0:
                self.winning_long_trades += 1
            elif pnl < 0:
                self.losing_long_trades += 1
            self.entry_price = None

        return self.equity, self.position

    def cover(self, row_index, price):
        '''
        平空倉的函數
        '''

        if self.position < 0:
            self.equity -= abs(self.position) * price * (1 + self.commission)
            self.data.loc[row_index,
                          'transaction'] = f'close_short _{self.position}_at_{price}'
            pnl = (self.entry_price - price) * abs(self.position)
            self.position = 0
            self.trade.append({'time': self.data.loc[row_index, 'Datetime'] + pd.Timedelta(hours=1),
                               'action': 'close_short', 'amount': self.position, 'price': price,
                               'equity': self.equity})

            if pnl > 0:
                self.winning_short_trades += 1
            elif pnl < 0:
                self.losing_short_trades += 1
            self.entry_price = None

        return self.equity, self.position

    def get_total_equity(self, price):
        '''
        紀錄equity的函數,包含未實現損益
        '''

        unrealized_profit = self.position * price
        total_equity = self.equity + unrealized_profit
        return total_equity

    def close_position(self):
        '''
        基於最後一根k線的close,平倉,結束回測
        '''

        final_price = self.data.loc[self.data.index[-1], 'Open']

        if self.position > 0:
            self.equity += self.position * final_price * (1 - self.commission)
        elif self.position < 0:
            self.equity -= abs(self.position) * \
                final_price * (1 + self.commission)
        self.position = 0
        self.data.loc[self.data.index[-1], 'position'] = self.position
        self.data.loc[self.data.index[-1], 'equity'] = self.equity
        self.data.loc[self.data.index[-1],
                      'transaction'] = f'close_position_at_{final_price}'
        self.trade.append({'time': self.data.loc[self.data.index[-1], 'Datetime'],
                           'action': 'close_position', 'amount': self.position, 'price': final_price,
                           'equity': self.equity})

    def calculate_max_drawdown(self):
        equity = self.data['equity']
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()
        # 找出最大回撤時間點
        max_drawdown_end = drawdown.idxmin()
        max_drawdown_start = (equity[:max_drawdown_end]).idxmax()

        return max_drawdown, max_drawdown_start, max_drawdown_end

    def run(self):
        '''
        macd不設止盈
        '''

        for i in tqdm(range(1, len(self.data))):

            current_price = self.data.loc[i, 'Close']
            atr = self.data.loc[i, 'atr']

            if self.position == 0:
                if self.data.loc[i, 'signal'] == 1:
                    self.long(row_index=i, price=current_price)
                    # self.stop_profit_atr = current_price + 4 * atr
                    self.stop_loss = current_price - 1 * atr

                elif self.data.loc[i, 'signal'] == -1:
                    self.short(row_index=i, price=current_price)
                    # self.stop_profit_atr = current_price - 4 * atr
                    self.stop_loss = current_price + 1 * atr

            elif self.position > 0:

                # if current_price > self.stop_profit_atr: #停利
                #     self.sell(row_index = i, price = self.stop_profit_atr)
                #     self.stop_profit = None
                #     self.stop_loss = None

                if current_price < self.stop_loss:  # 停損
                    self.sell(row_index=i, price=self.stop_loss)
                    self.stop_profit = None
                    self.stop_loss = None

                else:
                    self.stop_loss = max(
                        self.stop_loss, current_price - 1 * atr)

            elif self.position < 0:

                # if current_price < self.stop_profit_atr : #停利
                #     self.cover(row_index = i, price = self.stop_profit_atr)
                #     self.stop_profit = None
                #     self.stop_loss = None

                if current_price > self.stop_loss:  # 停損
                    self.cover(row_index=i, price=self.stop_loss)
                    self.stop_profit = None
                    self.stop_loss = None

                else:
                    self.stop_loss = min(
                        self.stop_loss, current_price + 1 * atr)

            self.data.loc[i, 'position'] = self.position
            self.data.loc[i, 'equity'] = self.get_total_equity(
                price=current_price)

        self.close_position()
        self.max_drawdown = self.calculate_max_drawdown()

        return self.data[['Datetime', 'Close', 'signal', 'equity', 'position', 'transaction']]

    def get_trades(self):
        '''
        打印交易日誌
        '''
        return pd.DataFrame(self.trade)

    def get_equity_curve(self):
        '''
        繪製 Equity Curve + 雙 Y 軸顯示 Close：
        1. 樣本內（綠色）、樣本外（藍色）
        2. 保留原始最大回撤 (MDD)
        3. 額外標示樣本外 (2024/3/6 - 2024/4/1) 的 MDD
        4. 添加 2024-01-01 分界線
        5. 在右側 Y 軸淡灰色顯示 Close 價格
        '''
        # 取得最大回撤資訊
        max_drawdown, max_drawdown_start, max_drawdown_end = self.calculate_max_drawdown()

        # 轉換時間格式
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
        split_date = pd.Timestamp('2024-01-01 00:00:00')

        # 樣本內與樣本外
        in_sample = self.data[self.data['Datetime'] < split_date]
        out_sample = self.data[self.data['Datetime'] >= split_date]

        # 樣本外 MDD 區間
        mdd_start_date = pd.Timestamp('2024-03-06')
        mdd_end_date = pd.Timestamp('2024-04-01')
        mdd_range = self.data[(self.data['Datetime'] >= mdd_start_date) & (
            self.data['Datetime'] <= mdd_end_date)]

        # 若區間不空，找該區間的最大/最小 Equity
        if not mdd_range.empty:
            mdd_local_max = mdd_range['equity'].max()
            mdd_local_min = mdd_range['equity'].min()
            mdd_local_max_date = mdd_range[mdd_range['equity']
                                           == mdd_local_max]['Datetime'].values[0]
            mdd_local_min_date = mdd_range[mdd_range['equity']
                                           == mdd_local_min]['Datetime'].values[0]
        else:
            mdd_local_max_date, mdd_local_min_date = None, None

        # 建立圖表與兩條 Y 軸
        fig, ax = plt.subplots(figsize=(16, 8))       # ax: 專門放 Equity Curve
        ax2 = ax.twinx()                             # ax2: 專門放 Close 價格

        # 在右軸 (ax2) 上繪製 Close (淡灰色)
        ax2.plot(
            self.data['Datetime'],
            self.data['Close'],
            color='gray',
            alpha=0.3,
            linewidth=1.5,
            label='Close Price'
        )
        ax2.set_ylabel('Close Price', fontsize=14)

        # 在左軸 (ax) 上繪製完整 Equity Curve（灰色淡化）
        ax.plot(
            self.data['Datetime'],
            self.data['equity'],
            label='Equity Curve',
            color='gray',
            linewidth=1.5,
            alpha=0.6
        )

        # 樣本內 (綠色)
        ax.plot(
            in_sample['Datetime'],
            in_sample['equity'],
            label='In-Sample Equity',
            color='#2ca02c',
            linewidth=2
        )

        # 樣本外 (藍色)
        ax.plot(
            out_sample['Datetime'],
            out_sample['equity'],
            label='Out-Sample Equity',
            color='#1f77b4',
            linewidth=2
        )

        # 繪製原始最大回撤 (MDD)
        start_date = self.data.loc[max_drawdown_start, 'Datetime']
        end_date = self.data.loc[max_drawdown_end, 'Datetime']
        start_equity = self.data.loc[max_drawdown_start, 'equity']
        end_equity = self.data.loc[max_drawdown_end, 'equity']

        ax.plot(
            [start_date, end_date],
            [start_equity, end_equity],
            color='red',
            linestyle='--',
            linewidth=2,
            label='Max Drawdown'
        )
        ax.scatter(
            start_date,
            start_equity,
            color='green',
            label='Peak',
            s=100,
            zorder=5
        )
        ax.scatter(
            end_date,
            end_equity,
            color='red',
            label='Trough',
            s=100,
            zorder=5
        )

        # 標記樣本外 MDD (紅色虛線)
        if not mdd_range.empty:
            ax.plot(
                mdd_range['Datetime'],
                mdd_range['equity'],
                label='Out-Sample MDD Range',
                color='red',
                linewidth=2.5,
                linestyle='dotted'
            )
            ax.scatter(
                mdd_local_max_date,
                mdd_local_max,
                color='green',
                label='MDD Peak (Out-Sample)',
                s=100,
                zorder=5
            )
            ax.scatter(
                mdd_local_min_date,
                mdd_local_min,
                color='red',
                label='MDD Trough (Out-Sample)',
                s=100,
                zorder=5
            )

        # 樣本內 / 樣本外分界線
        ax.axvline(
            split_date,
            color='black',
            linestyle='--',
            linewidth=2,
            label='Sample Split'
        )

        # 設定左軸標題、格式
        ax.set_title(
            f'Equity Curve (Max Drawdown: {max_drawdown:.2%})', fontsize=20)
        ax.set_xlabel('Time', fontsize=14)
        ax.set_ylabel('Equity', fontsize=14)
        ax.yaxis.set_major_formatter(
            mticker.StrMethodFormatter('{x:.0f}'))  # 顯示完整數字

        # 組合圖例：把 ax 與 ax2 的 legend 放在一起
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2,
                   loc='upper left', fontsize=12)

        # 網格與布局
        ax.grid(alpha=0.5)
        fig.tight_layout()
        plt.show()

    def calculate_annual_sharpe_ratio(self, risk_free_rate=0, annual_trading_hours=8760):
        '''
        計算年化 Sharpe Ratio
        risk_free_rate: 無風險利率 (預設 2%)
        annual_trading_hours: 每年交易小時數 (一小時 K 棒一年 8760 小時)
        '''
        returns = self.data['equity'].pct_change().dropna()
        excess_returns = returns - (risk_free_rate / annual_trading_hours)
        sharpe_ratio = np.sqrt(annual_trading_hours) * \
            (excess_returns.mean() / excess_returns.std())

        return sharpe_ratio

    def calculate_cumulative_return(self):
        '''
        累積報酬率 = (最終資產 / 初始資產) - 1
        '''
        final_equity = self.data['equity'].iloc[-1]
        initial_equity = self.data.loc[0, 'equity']
        return (final_equity / initial_equity) - 1

    def calculate_annual_return(self):
        '''
        年化報酬率 = (1 + 累積報酬率) ** (365 * 24 / K棒數量) - 1
        '''
        cumulative_return = self.calculate_cumulative_return()
        total_hours = len(self.data)
        annualized_return = (
            1 + cumulative_return) ** (365 * 24 / total_hours) - 1
        return annualized_return

    def calculate_annualized_volatility(self):
        '''
        年化波動度 = Equity每小時報酬率標準差 * sqrt(8760)
        '''
        self.data['hourly_return'] = self.data['equity'].pct_change()
        hourly_volatility = self.data['hourly_return'].std()
        return hourly_volatility * np.sqrt(8760)

    def calculate_profit_factor(self):
        '''
        風報比 = 總盈利 / 總虧損
        '''
        trades = self.get_trades()

        # 過濾出開倉與平倉的交易
        open_trades = trades[trades['action'].isin(
            ['long', 'short'])].reset_index()
        close_trades = trades[trades['action'].isin(
            ['close_long', 'close_short'])].reset_index()

        if len(open_trades) == 0 or len(close_trades) == 0:
            return np.nan

        # 計算每筆交易的損益
        pnl_list = []
        for i in range(len(close_trades)):
            entry_price = open_trades.loc[i, 'price']
            exit_price = close_trades.loc[i, 'price']
            position_size = open_trades.loc[i, 'amount']

            # 如果是做多
            if open_trades.loc[i, 'action'] == 'long':
                pnl = (exit_price - entry_price) * position_size

            # 如果是做空
            elif open_trades.loc[i, 'action'] == 'short':
                pnl = (entry_price - exit_price) * position_size

            pnl_list.append(pnl)

        # 分開計算總盈利與總虧損
        total_profit = sum(p for p in pnl_list if p > 0)
        total_loss = sum(p for p in pnl_list if p < 0)

        if total_loss == 0:
            return float('inf')  # 若無虧損，風報比為無限大

        return total_profit / abs(total_loss)

    def calculate_avg_hold_bars(self):
        '''
        平均持有K棒數 = 所有交易持有K棒數平均
        '''
        trades = self.get_trades()
        open_trades = trades[trades['action'].isin(
            ['long', 'short'])].reset_index()
        close_trades = trades[trades['action'].isin(
            ['close_long', 'close_short', 'close_position'])].reset_index()

        if len(open_trades) == 0 or len(close_trades) == 0:
            return np.nan

        hold_bars = (close_trades['time'] -
                     open_trades['time']).dt.total_seconds() / 3600
        return np.mean(hold_bars)

    def calculate_buy_and_hold_return(self):
        '''
        Buy and Hold Return = 最終收盤價 / 初始收盤價 - 1
        '''
        return self.data['Close'].iloc[-1] / self.data['Close'].iloc[0] - 1

    def calculate_trade_stats(self):
        '''
        計算交易統計數據：多單、空單次數、獲利次數、虧損次數及勝率
        '''
        total_trades = self.long_trades + self.short_trades
        total_winning_trades = self.winning_long_trades + self.winning_short_trades
        total_losing_trades = self.losing_long_trades + self.losing_short_trades

        long_win_rate = self.winning_long_trades / \
            self.long_trades if self.long_trades > 0 else 0
        short_win_rate = self.winning_short_trades / \
            self.short_trades if self.short_trades > 0 else 0
        total_win_rate = total_winning_trades / total_trades if total_trades > 0 else 0

        return {
            'long_trades': self.long_trades,
            'short_trades': self.short_trades,
            'winning_long_trades': self.winning_long_trades,
            'losing_long_trades': self.losing_long_trades,
            'winning_short_trades': self.winning_short_trades,
            'losing_short_trades': self.losing_short_trades,
            'total_winning_trades': total_winning_trades,
            'total_losing_trades': total_losing_trades,
            'long_win_rate': long_win_rate,
            'short_win_rate': short_win_rate,
            'total_win_rate': total_win_rate
        }

    def calculate_long_trade_performance(self):
        '''
        計算多單的平均獲利與平均虧損 (以百分比表示)
        '''
        trades = self.get_trades()
        long_trades = trades[trades['action'] == 'long'].reset_index()
        close_long_trades = trades[trades['action']
                                   == 'close_long'].reset_index()

        if len(long_trades) == 0 or len(close_long_trades) == 0:
            return np.nan, np.nan  # 沒有交易時回傳 NaN

        pnl_percent_list = []
        for i in range(len(close_long_trades)):
            entry_price = long_trades.loc[i, 'price']
            exit_price = close_long_trades.loc[i, 'price']
            position_size = long_trades.loc[i, 'amount']
            pnl = (exit_price - entry_price) * position_size
            pnl_percent = (pnl / (entry_price * position_size))
            pnl_percent_list.append(pnl_percent)

        # 計算多單平均獲利與平均虧損 (以百分比表示)
        avg_profit = np.mean([p for p in pnl_percent_list if p > 0]) if any(
            p > 0 for p in pnl_percent_list) else 0
        avg_loss = np.mean([p for p in pnl_percent_list if p < 0]) if any(
            p < 0 for p in pnl_percent_list) else 0

        return avg_profit, avg_loss

    def calculate_short_trade_performance(self):
        '''
        計算空單的平均獲利與平均虧損
        '''
        trades = self.get_trades()
        short_trades = trades[trades['action'] == 'short'].reset_index()
        close_short_trades = trades[trades['action']
                                    == 'close_short'].reset_index()

        if len(short_trades) == 0 or len(close_short_trades) == 0:
            return np.nan, np.nan  # 沒有交易時回傳 NaN

        pnl_percent_list = []
        for i in range(len(close_short_trades)):
            entry_price = short_trades.loc[i, 'price']
            exit_price = close_short_trades.loc[i, 'price']
            position_size = short_trades.loc[i, 'amount']
            pnl = (entry_price - exit_price) * position_size  # 空單收益公式
            pnl_percent = (pnl / (entry_price * position_size))
            pnl_percent_list.append(pnl_percent)

        # 計算空單平均獲利與平均虧損
        avg_profit = np.mean([p for p in pnl_percent_list if p > 0]) if any(
            p > 0 for p in pnl_percent_list) else 0
        avg_loss = np.mean([p for p in pnl_percent_list if p < 0]) if any(
            p < 0 for p in pnl_percent_list) else 0

        return avg_profit, avg_loss

    def calculate_all_trade_performance(self):
        """
        直接遍歷所有交易(多+空)，算出每筆交易的報酬率，
        最後分別取正報酬的平均、負報酬的平均。
        """
        trades = self.get_trades()
        open_trades = trades[trades['action'].isin(
            ['long', 'short'])].reset_index(drop=True)
        close_trades = trades[trades['action'].isin(
            ['close_long', 'close_short'])].reset_index(drop=True)

        if len(open_trades) == 0 or len(close_trades) == 0:
            return np.nan, np.nan

        pnl_percent_list = []
        for i in range(len(close_trades)):
            entry_price = open_trades.loc[i, 'price']
            exit_price = close_trades.loc[i, 'price']
            position_size = open_trades.loc[i, 'amount']

            # 多單
            if open_trades.loc[i, 'action'] == 'long':
                pnl = (exit_price - entry_price) * position_size
            # 空單
            else:
                pnl = (entry_price - exit_price) * position_size

            pnl_percent = (pnl / (entry_price * position_size))
            pnl_percent_list.append(pnl_percent)

        # 正報酬的平均、負報酬的平均
        avg_profit = np.mean([p for p in pnl_percent_list if p > 0]) if any(
            p > 0 for p in pnl_percent_list) else 0
        avg_loss = np.mean([p for p in pnl_percent_list if p < 0]) if any(
            p < 0 for p in pnl_percent_list) else 0

        return avg_profit, avg_loss

    def plot_pnl_distribution(self):
        """
        繪製多單、空單以及所有交易的獲利分佈圖 (以百分比計算)
        """

        trades = self.get_trades()

        # 函數：取得特定類型交易的 pnl(%)
        def get_pnl_percent_list(open_action, close_action):
            open_df = trades[trades['action'] ==
                             open_action].reset_index(drop=True)
            close_df = trades[trades['action'] ==
                              close_action].reset_index(drop=True)
            pnl_list = []
            # 以最小長度為準，避免出現對應不上的狀況
            for i in range(min(len(open_df), len(close_df))):
                entry_price = open_df.loc[i, 'price']
                exit_price = close_df.loc[i, 'price']
                position_size = open_df.loc[i, 'amount']

                # 做多
                if open_action == 'long':
                    pnl = (exit_price - entry_price) * position_size
                # 做空
                else:
                    pnl = (entry_price - exit_price) * position_size

                pnl_percent = (pnl / (entry_price * position_size)) * 100
                pnl_list.append(pnl_percent)
            return pnl_list

        # 分別取得「多單」、「空單」以及「所有交易」的 pnl%
        long_pnl = get_pnl_percent_list('long', 'close_long')
        short_pnl = get_pnl_percent_list('short', 'close_short')
        all_pnl = long_pnl + short_pnl  # 合併多、空單

        # 畫出三個直方圖
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

        # 多單分佈
        axes[0].hist(long_pnl, bins=30, color='green', alpha=0.7)
        axes[0].set_title('Long PnL Distribution')
        axes[0].set_xlabel('PnL (%)')
        axes[0].set_ylabel('Frequency')

        # 空單分佈
        axes[1].hist(short_pnl, bins=30, color='red', alpha=0.7)
        axes[1].set_title('Short PnL Distribution')
        axes[1].set_xlabel('PnL (%)')

        # 所有交易分佈
        axes[2].hist(all_pnl, bins=30, color='blue', alpha=0.7)
        axes[2].set_title('All Trades PnL Distribution')
        axes[2].set_xlabel('PnL (%)')

        plt.tight_layout()
        plt.show()
