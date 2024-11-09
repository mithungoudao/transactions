from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        method TEXT NOT NULL,
                        account TEXT NOT NULL,
                        remarks TEXT
                    )''')
    conn.commit()
    conn.close()

# Call the init_db function to create the database table
init_db()

@app.route('/', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        method = request.form['method']
        account = request.form['account']
        remarks = request.form.get('remarks', '')

        # Insert into the database
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (amount, category, method, account, remarks) VALUES (?, ?, ?, ?, ?)",
                       (amount, category, method, account, remarks))
        conn.commit()
        conn.close()

        return redirect(url_for('show_transactions'))

    return render_template('index.html')

@app.route('/transactions')
def show_transactions():
    # Fetch all transactions from the database
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()

    return render_template('transactions.html', transactions=transactions)

@app.route('/category_chart')
def category_chart():
    # Connect to the database and retrieve category and amount data
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    # Prepare data for the pie chart
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

    # Save the pie chart to a bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

@app.route('/view_chart')
def view_chart():
    return render_template('chart.html')