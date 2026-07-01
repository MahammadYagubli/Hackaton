
# =========================

# 1. IMPORT LIBRARIES

# =========================

import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# =========================

# 2. CONFIGURATION

# =========================

EXCEL_FILE = 'company_names.xlsx'
COLUMN_NAME = 'Short Name'
START_DATE = '2026-01-01'
OUTPUT_FOLDER = 'stock_data'

# Create output folder

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("Setup completed.")

# =========================

# 3. LOAD EXCEL FILE

# =========================

df = pd.read_excel(EXCEL_FILE)

 
# Clean tickers

tickers = df[COLUMN_NAME].dropna().astype(str).str.strip().str.upper()

print(f"Total tickers found: {len(tickers)}")
display(tickers.head())

# =========================

# 4. DOWNLOAD FUNCTION

# =========================

def download_and_save(ticker):
    try:
        print(f"Downloading: {ticker}")
        data = yf.download(ticker, start=START_DATE, progress=False)

        if data.empty:
            print(f"⚠️ No data for {ticker}")
            return False

        file_path = os.path.join(OUTPUT_FOLDER, f"{ticker}_historical_data.csv")
        data.to_csv(file_path)

        print(f" Saved: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error for {ticker}: {e}")
    return False
 

# =========================

# 5. LOOP THROUGH TICKERS

# =========================

success = 0
fail = 0

for ticker in tickers:
    result = download_and_save(ticker)
    if result:
        success += 1
    else:
        fail += 1
 

print("\n=========================")
print("SUMMARY")
print("=========================")
print(f"Total     : {len(tickers)}")
print(f"Success   : {success}")
print(f"Failed    : {fail}")
print(f"Finished  : {datetime.now()}")
print("=========================")
