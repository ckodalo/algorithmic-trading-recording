# Momentum Trading App

This project is a Django application intended to automate a momentum-based stock trading strategy. It uses Massive for historical market data, SnapTrade for brokerage integration, and a database to track portfolios and trading activity.

## Trading workflow

1. **Choose a stock universe.** The current implementation uses a fixed list of 50 stocks.
2. **Fetch historical prices from Massive.** Calculate momentum as the price change from approximately 12 months ago to one month ago, deliberately skipping the most recent month:

   ```text
   momentum = (price_one_month_ago - price_twelve_months_ago) / price_twelve_months_ago
   ```

3. **Rank stocks into five groups (quintiles).** Stocks with the highest momentum belong to the top group; those with the lowest momentum belong to the bottom group.
4. **Generate trading signals.** Buy top-quintile stocks that the portfolio does not already hold. Sell held stocks that fall into the bottom quintile. Keep existing holdings in the middle groups.
5. **Submit orders through SnapTrade.** Submit sell orders first, then allocate the buying budget equally among new buy candidates.
6. **Track portfolio activity.** Store positions, cash balances, trade records, momentum scores, signals, rebalance events, and performance metrics.
7. **Repeat periodically.** The strategy defaults to weekly rebalancing and also supports a monthly interval.

The strategy aims to capture persistence in relative stock performance by buying recent relative winners and exiting holdings that become relative losers. Existing top-quintile holdings are retained rather than automatically resized to equal weights.

## Project structure

The Django project lives in `project1/`.

| Component | Responsibility |
| --- | --- |
| `project1/momentum_trader/` | Django settings and application URL configuration |
| `project1/trading/` | Stocks, historical prices, momentum scores, trading signals, and rebalance events |
| `project1/trading/services/massive_client.py` | Historical market data access |
| `project1/trading/services/momentum_calculator.py` | Momentum calculations and stock rankings |
| `project1/trading/services/strategy_engine.py` | Signal generation and rebalance orchestration |
| `project1/trading/services/snaptrade_client.py` | Brokerage position synchronization and order operations |
| `project1/portfolio/` | Portfolios, holdings, trade records, and performance metrics |

## Current state

The Django admin is currently the main interface. The code outlines the intended trading workflow, but the application is still an unfinished prototype. The user-facing dashboard, backtesting, and full automation are not yet implemented, and parts of the execution and reconciliation workflow need further work.

Weekly and monthly rebalancing are interval checks in the strategy code; a recurring job scheduler is not yet provided. The backtest method is a placeholder, and the test files currently contain no tests.
