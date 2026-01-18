import pandas as pd
import random
import os
from datetime import datetime, timedelta

# Output Files
DATA_DIR = os.path.join(os.getcwd(), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.csv')
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.csv')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.csv')

# --- DATA GENERATION ---

DEPARTMENTS = ['Computer Science', 'Mechanical', 'Civil', 'Electronics', 'MBA']
ROLES = ['Student', 'Faculty']

# 1. Books
# (BookID, Title, Author, Department, Status)
books_data = [
    # CS
    ("B101", "Introduction to Algorithms", "Cormen", "Computer Science", "Available"),
    ("B102", "Clean Code", "Robert C. Martin", "Computer Science", "Available"),
    ("B103", "The Pragmatic Programmer", "Andy Hunt", "Computer Science", "Available"),
    ("B104", "Artificial Intelligence", "Russell & Norvig", "Computer Science", "Available"),
    ("B105", "Database System Concepts", "Silberschatz", "Computer Science", "Available"),
    # Mech
    ("B201", "Engineering Thermodynamics", "P.K. Nag", "Mechanical", "Available"),
    ("B202", "Fluid Mechanics", "R.K. Bansal", "Mechanical", "Available"),
    ("B203", "Theory of Machines", "S.S. Rattan", "Mechanical", "Available"),
    # Civil
    ("B301", "Surveying Vol. 1", "B.C. Punmia", "Civil", "Available"),
    ("B302", "Structural Analysis", "Hibbeler", "Civil", "Available"),
    # Electronics
    ("B401", "Microelectronic Circuits", "Sedra & Smith", "Electronics", "Available"),
    ("B402", "Digital Logic Design", "Morris Mano", "Electronics", "Available"),
    # MBA
    ("B501", "Principles of Marketing", "Philip Kotler", "MBA", "Available"),
    ("B502", "Financial Management", "Prasanna Chandra", "MBA", "Available")
]

# Generate more copies
final_books = []
for i in range(1, 51):
    base = random.choice(books_data)
    # Unique ID per copy
    bid = f"LIB{1000+i}"
    final_books.append({
        "BookID": bid,
        "Title": base[1],
        "Author": base[2],
        "Department": base[3],
        "Status": "Available"
    })

# 2. Members
# (MemberID, Name, Role, Department, Batch/Designation)
names = [
    "Aarav Sharma", "Vivaan Patel", "Aditya Vernekar", "Vihaan Rao", "Arjun Mehta",
    "Sai Iyer", "Reyansh Reddy", "Ayaan Kumar", "Krishna Das", "Ishaan Nair",
    "Diya Malhotra", "Saanvi Shetty", "Ananya Joshi", "Kiara Singh", "Pari Kapoor"
]

final_members = []
for i, name in enumerate(names):
    mid = f"STU{2023000+i}"
    dept = random.choice(DEPARTMENTS)
    final_members.append({
        "MemberID": mid,
        "Name": name,
        "Role": "Student",
        "Department": dept,
        "Batch": "2023-2027"
    })

# Add some faculty
fac_names = ["Dr. R.K. Mishra", "Prof. S. Deshpande", "Dr. A.P.J. Abdul"]
for i, name in enumerate(fac_names):
    mid = f"FAC{100+i}"
    dept = random.choice(DEPARTMENTS)
    final_members.append({
        "MemberID": mid,
        "Name": name,
        "Role": "Faculty",
        "Department": dept,
        "Batch": "Senior Professor"
    })

# 3. Transactions (History)
# Generate some history
transactions = []
current_status = {} # BookID -> Status

for i in range(30):
    # Random Issue
    book = random.choice(final_books)
    member = random.choice(final_members)
    days_ago = random.randint(1, 60)
    date_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    
    tx_id = f"TX{1000+i}"
    
    # Issue
    transactions.append({
        "TransactionID": tx_id,
        "BookID": book['BookID'],
        "MemberID": member['MemberID'],
        "Date": date_str,
        "Action": "Issue"
    })
    
    # 50% chance of return if it was long ago
    if days_ago > 10 and random.random() > 0.3:
        # Return
        ret_date = (datetime.now() - timedelta(days=days_ago-random.randint(1, 5))).strftime('%Y-%m-%d')
        transactions.append({
            "TransactionID": f"TX{1000+i}_R",
            "BookID": book['BookID'],
            "MemberID": member['MemberID'],
            "Date": ret_date,
            "Action": "Return"
        })
        current_status[book['BookID']] = 'Available'
    else:
        current_status[book['BookID']] = 'Issued'

# Apply final status to books
for b in final_books:
    if b['BookID'] in current_status:
        b['Status'] = current_status[b['BookID']]

# SAVE
pd.DataFrame(final_books).to_csv(BOOKS_FILE, index=False)
pd.DataFrame(final_members).to_csv(MEMBERS_FILE, index=False)
pd.DataFrame(transactions).sort_values(by='Date').to_csv(TRANSACTIONS_FILE, index=False)

print("College Data Seeded Successfully!")
