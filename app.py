from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from utils.data_manager import load_data, issue_book, return_book, get_transaction_history
from utils.analytics import calculate_kpis, generate_charts

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_mvp'

@app.route('/')
def dashboard():
    books, members, transactions = load_data()
    
    # Calculate Metrics
    kpis = calculate_kpis(books, members, transactions)
    charts = generate_charts(books, transactions)
    
    # Fetch History
    history = get_transaction_history()
    
    return render_template('dashboard.html', kpis=kpis, charts=charts, history=history[:10]) # Show last 10

@app.route('/issue', methods=['GET', 'POST'])
def issue_page():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        
        success, message = issue_book(book_id, member_id)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
            return redirect(url_for('issue_page'))
    
    # GET request: Load available books for reference
    books, _, _ = load_data()
    available_ids = books[books['Status'] == 'Available']['BookID'].tolist()
    
    return render_template('issue_book.html', available_ids=available_ids)

@app.route('/return', methods=['GET', 'POST'])
def return_page():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        
        success, message = return_book(book_id)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
            return redirect(url_for('return_page'))
    
    # GET request: Load issued books for reference
    books, _, _ = load_data()
    issued_ids = books[books['Status'] == 'Issued']['BookID'].tolist()
    
    return render_template('return_book.html', issued_ids=issued_ids)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book_page():
    if request.method == 'POST':
        data = {
            'BookID': request.form.get('book_id'),
            'Title': request.form.get('title'),
            'Author': request.form.get('author'),
            'Department': request.form.get('department')
        }
        from utils.data_manager import add_new_book
        success, msg = add_new_book(data)
        if success:
            flash(msg, 'success')
            return redirect(url_for('books_page'))
        else:
            flash(msg, 'danger')
            
    return render_template('add_book.html')

@app.route('/add_member', methods=['GET', 'POST'])
def add_member_page():
    if request.method == 'POST':
        data = {
            'MemberID': request.form.get('member_id'),
            'Name': request.form.get('name'),
            'Role': request.form.get('role'),
            'Department': request.form.get('department'),
            'Batch': request.form.get('batch')
        }
        from utils.data_manager import add_new_member
        success, msg = add_new_member(data)
        if success:
            flash(msg, 'success')
            return redirect(url_for('members_page'))
        else:
            flash(msg, 'danger')
            
    return render_template('add_member.html')

@app.route('/books')
def books_page():
    books, _, _ = load_data()
    
    # Filter by Status if provided
    status_filter = request.args.get('status')
    if status_filter:
        books = books[books['Status'] == status_filter]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(books)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_books = books.iloc[start:end].to_dict('records')
    
    has_next = end < total
    has_prev = page > 1
        
    return render_template('books.html', books=paginated_books, filter=status_filter, page=page, has_next=has_next, has_prev=has_prev)

@app.route('/members')
def members_page():
    _, members, _ = load_data()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(members)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_members = members.iloc[start:end].to_dict('records')
    
    has_next = end < total
    has_prev = page > 1
    
    return render_template('members.html', members=paginated_members, page=page, has_next=has_next, has_prev=has_prev)

@app.route('/delete/book/<book_id>')
def delete_book_route(book_id):
    from utils.data_manager import delete_book
    success, msg = delete_book(book_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('books_page'))

@app.route('/delete/member/<member_id>')
def delete_member_route(member_id):
    from utils.data_manager import delete_member
    success, msg = delete_member(member_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('members_page'))

@app.route('/member/<member_id>')
def member_details(member_id):
    _, members, _ = load_data()
    member = members[members['MemberID'] == member_id]
    
    if member.empty:
        flash('Member not found', 'danger')
        return redirect(url_for('members_page'))
        
    from utils.data_manager import get_member_history, get_member_current_loans
    history = get_member_history(member_id)
    current_loans = get_member_current_loans(member_id)
    
    return render_template('member_details.html', member=member.iloc[0].to_dict(), history=history, current_loans=current_loans)

# --- API Endpoints ---
@app.route('/api/book/<book_id>')
def api_get_book(book_id):
    books, _, _ = load_data()
    book = books[books['BookID'] == book_id]
    if not book.empty:
        return jsonify(book.iloc[0].to_dict())
    return jsonify({}), 404

@app.route('/api/member/<member_id>')
def api_get_member(member_id):
    _, members, _ = load_data()
    member = members[members['MemberID'] == member_id]
    if not member.empty:
        return jsonify(member.iloc[0].to_dict())
    return jsonify({}), 404

if __name__ == '__main__':
    app.run(debug=True)
