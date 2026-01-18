import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.csv')
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.csv')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.csv')

def load_data():
    """Loads all CSVs into DataFrames"""
    books = pd.read_csv(BOOKS_FILE)
    members = pd.read_csv(MEMBERS_FILE)
    transactions = pd.read_csv(TRANSACTIONS_FILE)
    return books, members, transactions

def save_books(books_df):
    """Saves books DF back to CSV"""
    books_df.to_csv(BOOKS_FILE, index=False)

def save_transactions(transactions_df):
    """Saves transactions DF back to CSV"""
    transactions_df.to_csv(TRANSACTIONS_FILE, index=False)

def add_new_book(data):
    """Adds a new book if ID is unique."""
    books, _, _ = load_data()
    
    # Tiny Safety: Check for empty strings
    if not data['BookID'] or not data['Title'] or not data['Author']:
        return False, "All fields are required."

    if data['BookID'] in books['BookID'].values:
        return False, "Book ID already exists."
    
    # Ensure correct columns
    new_book = pd.DataFrame([{
        'BookID': data['BookID'],
        'Title': data['Title'],
        'Author': data['Author'],
        'Department': data['Department'],
        'Status': 'Available'
    }])
    
    books = pd.concat([books, new_book], ignore_index=True)
    save_books(books)
    return True, "Book added successfully."

def add_new_member(data):
    """Adds a new member if ID is unique."""
    _, members, _ = load_data()
    
    # Tiny Safety: Check for empty strings
    if not data['MemberID'] or not data['Name']:
        return False, "ID and Name are required."

    if data['MemberID'] in members['MemberID'].values:
        return False, "Member ID already exists."
        
    new_member = pd.DataFrame([{
        'MemberID': data['MemberID'],
        'Name': data['Name'],
        'Role': data['Role'],
        'Department': data['Department'],
        'Batch': data['Batch']
    }])
    
    # Save back to CSV directly to handle differing columns gracefully if needed
    # but here we follow the strict schema
    members = pd.concat([members, new_member], ignore_index=True)
    members.to_csv(MEMBERS_FILE, index=False)
    return True, "Member registered successfully."

def issue_book(book_id, member_id):
    """
    Issues a book to a member.
    Returns (Success: bool, Message: str)
    """
    books, members, transactions = load_data()

    # 1. Validation
    if book_id not in books['BookID'].values:
        return False, "Book ID not found."
    if member_id not in members['MemberID'].values:
        return False, "Member ID not found."
    
    book_row_idx = books.index[books['BookID'] == book_id][0]
    if books.at[book_row_idx, 'Status'] == 'Issued':
        return False, "Book is already issued."

    # 2. Update Books Status
    books.at[book_row_idx, 'Status'] = 'Issued'
    save_books(books)

    # 3. Add Transaction
    new_transaction = {
        'TransactionID': f"T{len(transactions) + 1:03d}",
        'BookID': book_id,
        'MemberID': member_id,
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Action': 'Issue'
    }
    # Using pd.concat instead of append (deprecated)
    new_interactions_df = pd.DataFrame([new_transaction])
    transactions = pd.concat([transactions, new_interactions_df], ignore_index=True)
    save_transactions(transactions)

    return True, f"Book {book_id} issued to {member_id} successfully."

def return_book(book_id):
    """
    Returns a book.
    Returns (Success: bool, Message: str)
    """
    books, members, transactions = load_data()

    if book_id not in books['BookID'].values:
        return False, "Book ID not found."
    
    book_row_idx = books.index[books['BookID'] == book_id][0]
    if books.at[book_row_idx, 'Status'] == 'Available':
        return False, "Book is already available."

    # 1. Update Books Status
    books.at[book_row_idx, 'Status'] = 'Available'
    save_books(books)

    # 2. Add Transaction
    new_transaction = {
        'TransactionID': f"T{len(transactions) + 1:03d}",
        'BookID': book_id,
        'MemberID': 'N/A', # Return doesn't necessarily need a member if we just scan the book
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Action': 'Return'
    }
    new_interactions_df = pd.DataFrame([new_transaction])
    transactions = pd.concat([transactions, new_interactions_df], ignore_index=True)
    save_transactions(transactions)

    return True, f"Book {book_id} returned successfully."

def get_transaction_history():
    """
    Returns a merged DataFrame with Book Titles and Member Names.
    """
    books, members, transactions = load_data()
    
    # Merge with Books to get Title
    merged = pd.merge(transactions, books[['BookID', 'Title']], on='BookID', how='left')
    
    # Merge with Members to get Name
    merged = pd.merge(merged, members[['MemberID', 'Name']], on='MemberID', how='left')
    
    # Fill N/A for Returns where MemberID might be N/A or generic
    merged['Name'] = merged['Name'].fillna('Library')
    
    # Sort by TransactionID descending (newest first)
    merged = merged.sort_values(by='TransactionID', ascending=False)
    
    return merged.to_dict('records')

def get_member_history(member_id):
    """
    Returns history for a specific member.
    """
    books, members, transactions = load_data()
    
    # Filter transactions for this member
    member_tx = transactions[transactions['MemberID'] == member_id].copy()
    
    if member_tx.empty:
        return []
        
    # Merge with Books
    merged = pd.merge(member_tx, books[['BookID', 'Title', 'Author']], on='BookID', how='left')
    
    # Sort by Date descending
    merged = merged.sort_values(by='Date', ascending=False)
    
    # Calculate Overdue Status (Simple Logic: Issue > 14 days ago)
    records = merged.to_dict('records')
    today = datetime.now().date()
    
    for record in records:
        if record['Action'] == 'Issue':
            tx_date = datetime.strptime(record['Date'], '%Y-%m-%d').date()
            delta = (today - tx_date).days
            record['DaysAgo'] = delta
            record['Overdue'] = delta > 14
        else:
            record['Overdue'] = False
            
    return records

def get_member_current_loans(member_id):
    """
    Replays transaction history to find currently holding books.
    Returns list of dicts with Overdue status.
    """
    _, _, transactions = load_data()
    # Filter for member
    txs = transactions[transactions['MemberID'] == member_id].sort_values(by='Date')
    
    loans = {} # BookID -> {Date, TransactionID}
    
    for _, row in txs.iterrows():
        bid = row['BookID']
        if row['Action'] == 'Issue':
            loans[bid] = row
        elif row['Action'] == 'Return':
            if bid in loans:
                del loans[bid]
                
    # Now loans contains only active books
    active_loans = []
    # Removed inner import causing UnboundLocalError
    books, _, _ = load_data()
    today = datetime.now().date()
    
    for bid, row in loans.items():
        # Get Book details
        book_info = books[books['BookID'] == bid].iloc[0]
        issue_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
        delta = (today - issue_date).days
        
        active_loans.append({
            'BookID': bid,
            'Title': book_info['Title'],
            'Author': book_info['Author'],
            'Date': row['Date'],
            'DaysHeld': delta,
            'Overdue': delta > 14
        })
        
    return active_loans
