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
            
    return render_template('return_book.html')

@app.route('/books')
def books_page():
    books, _, _ = load_data()
    
    # Filter by Status if provided
    status_filter = request.args.get('status')
    if status_filter:
        books = books[books['Status'] == status_filter]
        
    return render_template('books.html', books=books.to_dict('records'), filter=status_filter)

@app.route('/members')
def members_page():
    _, members, _ = load_data()
    return render_template('members.html', members=members.to_dict('records'))

@app.route('/member/<member_id>')
def member_details(member_id):
    _, members, _ = load_data()
    member = members[members['MemberID'] == member_id]
    
    if member.empty:
        flash('Member not found', 'danger')
        return redirect(url_for('members_page'))
        
    from utils.data_manager import get_member_history
    history = get_member_history(member_id)
    
    return render_template('member_details.html', member=member.iloc[0].to_dict(), history=history)

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
