# 🎓 College Library Management System (Analytics Edition)

A Data-Driven Library Management System built for Colleges (Engineering/MBA), featuring real-time inventory tracking, member analytics, and a modern dashboard.

## 🚀 Key Features

### 1. 📊 Smart Dashboard
- **Real-time Analytics**: Visual charts showing Book Distribution by Department (Computer Science, Civil, MBA, etc.).
- **KPIs**: Instant view of Total Books, Active Members, and Issue Counts.

### 2. 📚 Inventory Management
- **College Taxonomy**: Books categorized by Department (CS, Mech, Civil) and Status (Available/Issued).
- **Search & Filter**: Find books instantly by Title, Author, or ID.
- **One-Click Actions**: Issue books directly from the list.
- **Admin Tools**: Add or **Delete** books locally with validation safety.

### 3. 👥 Member Directory
- **Student & Faculty Support**: distinct roles with Department and Batch tracking.
- **History Tracking**: View complete borrowing history for any student.
- **Active Loans**: See exactly what a student is holding right now.

### 4. ⚡ "Mini-Project" Optimized
- **No Database Setup**: Runs entirely on CSV files (pandas-powered).
- **Zero Config**: Just run `python app.py` and go.
- **Data Repair**: Includes tools to auto-fix inconsistent transaction data.

---

## 🛠️ Technology Stack
- **Backend**: Python (Flask)
- **Data Engine**: Pandas (CSV-based NoSQL approach)
- **Visualization**: Matplotlib
- **Frontend**: HTML5, Bootstrap 5, Custom CSS

---

## 🏃‍♂️ How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the App**:
   ```bash
   python app.py
   ```

3. **Open Browser**:
   Go to `http://127.0.0.1:5000`

---

## 📂 Project Structure
- `app.py`: Main controller.
- `utils/data_manager.py`: Handles all CSV read/write logic.
- `data/`: Contains the database (books.csv, members.csv, transactions.csv).
- `templates/`: HTML frontend files.
- `static/`: CSS and Assets.
