import pandas as pd
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
BOOKS_FILE = DATA_DIR / 'books.csv'
TRANSACTIONS_FILE = DATA_DIR / 'transactions.csv'

def repair_data():
    print("Repairing data integrity...")
    books = pd.read_csv(BOOKS_FILE)
    transactions = pd.read_csv(TRANSACTIONS_FILE)
    
    # 2. Sync Book Status based on Last Transaction
    for idx, row in books.iterrows():
        bid = row['BookID']
        # Find last transaction for this book
        book_txs = transactions[transactions['BookID'] == bid].sort_values(by='Date')
        
        if not book_txs.empty:
            last_action = book_txs.iloc[-1]['Action']
            if last_action == 'Issue':
                books.at[idx, 'Status'] = 'Issued'
            else:
                books.at[idx, 'Status'] = 'Available'
        else:
            # No history, default to Available
            books.at[idx, 'Status'] = 'Available'
            
    # Save
    books.to_csv(BOOKS_FILE, index=False)
    transactions.to_csv(TRANSACTIONS_FILE, index=False)
    print("-> Data Synced Successfully!")

if __name__ == "__main__":
    repair_data()
