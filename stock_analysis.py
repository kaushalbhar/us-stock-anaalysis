import yfinance as yf
import pandas as pd

stocks = {
    "Apple": "AAPL",
    "Google": "GOOGL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Amazon": "AMZN"
}

print("Downloading stock data...")

all_data = {}

for name, ticker in stocks.items():
    df = yf.download(ticker, period="1y", interval="1mo", auto_adjust=True, progress=False)
    df.columns = df.columns.get_level_values(0)
    df["Monthly Return (%)"] = df["Close"].pct_change() * 100
    all_data[name] = df
    print(f"  ✓ {name} done")

print("\n📊 ANALYSIS RESULTS")
print("=" * 50)

summary = []

for name, df in all_data.items():
    returns = df["Monthly Return (%)"].dropna()
    close   = df["Close"]

    total_return = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100)
    avg_monthly  = float(returns.mean())
    volatility   = float(returns.std())
    best_month   = returns.idxmax().strftime("%b %Y")
    worst_month  = returns.idxmin().strftime("%b %Y")
    best_val     = float(returns.max())
    worst_val    = float(returns.min())

    summary.append({
        "Stock": name,
        "Total Return (%)": round(total_return, 2),
        "Avg Monthly Return (%)": round(avg_monthly, 2),
        "Volatility (Std Dev)": round(volatility, 2),
        "Best Month": best_month,
        "Best Month Return (%)": round(best_val, 2),
        "Worst Month": worst_month,
        "Worst Month Return (%)": round(worst_val, 2),
    })

    print(f"\n{name} ({stocks[name]})")
    print(f"  Total 1-Year Return : {total_return:.2f}%")
    print(f"  Avg Monthly Return  : {avg_monthly:.2f}%")
    print(f"  Volatility          : {volatility:.2f}%")
    print(f"  Best Month          : {best_month} ({best_val:.2f}%)")
    print(f"  Worst Month         : {worst_month} ({worst_val:.2f}%)")

summary_df = pd.DataFrame(summary)

with pd.ExcelWriter("stock_analysis.xlsx", engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    for name, df in all_data.items():
        out = df[["Close", "Monthly Return (%)"]].copy()
        out.index = out.index.strftime("%b %Y")
        out.to_excel(writer, sheet_name=name[:31])

print("\n✅ File saved: stock_analysis.xlsx")

print("\n💡 KEY INSIGHTS")
print("=" * 50)

best_performer  = summary_df.loc[summary_df["Total Return (%)"].idxmax(), "Stock"]
worst_performer = summary_df.loc[summary_df["Total Return (%)"].idxmin(), "Stock"]
most_volatile   = summary_df.loc[summary_df["Volatility (Std Dev)"].idxmax(), "Stock"]
least_volatile  = summary_df.loc[summary_df["Volatility (Std Dev)"].idxmin(), "Stock"]

print(f"  🏆 Best Performer  : {best_performer} ({summary_df['Total Return (%)'].max():.2f}%)")
print(f"  📉 Worst Performer : {worst_performer} ({summary_df['Total Return (%)'].min():.2f}%)")
print(f"  🌊 Most Volatile   : {most_volatile} ({summary_df['Volatility (Std Dev)'].max():.2f}% std dev)")
print(f"  🪨 Most Stable     : {least_volatile} ({summary_df['Volatility (Std Dev)'].min():.2f}% std dev)")