import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.csv')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.csv')

def repair_data():
    print("Reparing Data Integrity...")
    books = pd.read_csv(BOOKS_FILE)
    transactions = pd.read_csv(TRANSACTIONS_FILE)
    
    # 1. Inject Active Loans (so the tab isn't empty)
    # Issue B002 to M001
    new_tx_1 = {
        "TransactionID": "T_FIX_01",
        "BookID": "B002",
        "MemberID": "M001",
        "Date": datetime.now().strftime('%Y-%m-%d'),
        "Action": "Issue"
    }
    # Issue B004 to M001
    new_tx_2 = {
        "TransactionID": "T_FIX_02",
        "BookID": "B004",
        "MemberID": "M001",
        "Date": datetime.now().strftime('%Y-%m-%d'),
        "Action": "Issue"
    }
    
    # Check if already exists to avoid duplicates on re-run
    if "T_FIX_01" not in transactions['TransactionID'].values:
        transactions = pd.concat([transactions, pd.DataFrame([new_tx_1, new_tx_2])], ignore_index=True)
        print("-> Injected 2 Active Loans for M001 (B002, B004)")
    
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
