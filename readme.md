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

The application includes a portfolio list and detail page, momentum rankings, trading signals, and rebalance history. These pages display saved database records; they do not fetch market data or submit orders. The trading workflow remains an unfinished prototype: backtesting, full automation, and parts of execution and reconciliation still need further work.

Weekly and monthly rebalancing are interval checks in the strategy code; a recurring job scheduler is not yet provided. The backtest method is a placeholder. View tests cover permissions, portfolio data isolation, filtering, pagination, and rendering.

## Local setup (Windows PowerShell)

From the repository root, with Python installed:

```powershell
cd project1
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in. SQLite is configured locally. API credentials are optional for browsing saved records; market data and brokerage services require their respective credentials in `.env`.

## Application pages

- `/portfolios/`: portfolio overview; click a name for holdings, the latest 50 trades, and the latest 30 performance snapshots.
- `/trading/rankings/`: latest saved momentum rankings, with calculation date and quintile filters. Momentum is displayed as a decimal return (0.25 means 25%).
- `/trading/signals/`: saved signals, filterable by date, signal type, and execution status.
- `/trading/rebalances/`: saved rebalance runs, filterable by status.
- `/admin/`: manage database records and user permissions.

A superuser can access all pages. Other users need the matching model view permissions in Django admin. Portfolio details require `view_portfolio`; holdings, trades, and performance sections additionally require `view_position`, `view_trade`, and `view_performancemetric`. Trading pages require `view_momentumscore`, `view_tradingsignal`, and `view_rebalanceevent`, respectively. The current models have no user ownership field, so permissions provide application-wide access. Signals and rebalance events are not linked to individual portfolios.

Run checks and tests from `project1`:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test portfolio trading
```

## Fetch momentum rankings

From `project1`, set `MASSIVE_API_KEY` in `.env` and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py pull_massive_data
```

The command creates AAPL and NVDA stock records, fetches historical momentum prices, saves scores, and assigns ranks and quintiles for today's date. Refresh `/trading/rankings/` afterward. Repeating the command updates scores for the same stock and calculation date. It does not create holdings, signals, rebalance events, or brokerage orders.

Choose other symbols or a historical calculation date with:

```powershell
.\.venv\Scripts\python.exe manage.py pull_massive_data --tickers AAPL NVDA MSFT --date 2026-10-04
```

Missing price data is reported; if no scores can be saved, the command exits with an error. Rankings include all saved scores for the selected calculation date. Existing scores for skipped stocks remain unchanged. With fewer than five scores, the current quintile method places all scores in quintile 1; use a larger stock universe for meaningful five-group comparisons.
