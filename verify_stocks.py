import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from data.stock_database import get_all_stocks, get_stocks_by_sector

stocks = get_all_stocks()
print(f"Total stocks: {len(stocks)}")

general_stocks = get_stocks_by_sector('general')
print(f"General/Unclassified stocks: {len(general_stocks) if general_stocks else 0}")

# Check a sample
if len(stocks) > 500:
    print("Sample stock from CSV:", stocks[-1])
