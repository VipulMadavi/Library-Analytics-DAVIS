import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def calculate_kpis(books, members, transactions):
    """Calculates simple KPIs for the dashboard"""
    total_books = len(books)
    issued_books = len(books[books['Status'] == 'Issued'])
    available_books = total_books - issued_books
    total_members = len(members)
    
    return {
        'total_books': total_books,
        'issued_books': issued_books,
        'available_books': available_books,
        'total_members': total_members
    }

def get_plot_url(plot_func, *args):
    """Helper to convert a Matplotlib plot to a base64 string for HTML"""
    img = io.BytesIO()
    plot_func(*args)
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close() # Close figure to free memory
    return 'data:image/png;base64,{}'.format(plot_url)

def plot_books_by_department(books):
    counts = books['Department'].value_counts()
    plt.figure(figsize=(6, 4))
    counts.plot(kind='bar', color='#6366f1') # Brand color
    plt.title('Library Collection by Department')
    plt.xlabel('Department')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()

def plot_transactions_timeline(transactions):
    # Ensure date is datetime
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    daily_counts = transactions.groupby('Date').size()
    
    plt.figure(figsize=(6, 4))
    daily_counts.plot(kind='line', marker='o', color='green')
    plt.title('Transactions Over Time')
    plt.xlabel('Date')
    plt.ylabel('Transactions')
    plt.grid(True)
    plt.tight_layout()

def generate_charts(books, transactions):
    """Generates all charts and returns a dict of base64 strings"""
    charts = {}
    
    # 1. Books by Department
    charts['category_bar'] = get_plot_url(plot_books_by_department, books)
    
    # 2. Transaction Timeline (only if check if not empty to avoid errors)
    if not transactions.empty:
        charts['transaction_line'] = get_plot_url(plot_transactions_timeline, transactions)
    else:
        charts['transaction_line'] = None # Handle empty case in template

    return charts
