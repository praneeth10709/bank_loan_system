import sqlite3
from datetime import datetime

class Database:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            principal REAL,
            years INTEGER,
            rate REAL,
            interest REAL,
            total_amount REAL,
            emi REAL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            type TEXT,
            amount REAL,
            date TEXT
        )""")
        self.conn.commit()

    def add_loan(self, customer_id, principal, years, rate, interest, total_amount, emi):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO loans (customer_id, principal, years, rate, interest, total_amount, emi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (customer_id, principal, years, rate, interest, total_amount, emi))
        self.conn.commit()
        return cursor.lastrowid

    def make_payment(self, loan_id, type, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO payments (loan_id, type, amount, date) VALUES (?, ?, ?, ?)",
                       (loan_id, type, amount, datetime.now().isoformat()))
        self.conn.commit()

    def get_ledger(self, loan_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM loans WHERE loan_id=?", (loan_id,))
        loan = cursor.fetchone()
        cursor.execute("SELECT type, amount, date FROM payments WHERE loan_id=?", (loan_id,))
        payments = cursor.fetchall()
        total_paid = sum(p[1] for p in payments)
        emi = loan[7]
        emi_paid = sum(1 for p in payments if p[0] == "EMI")
        emi_left = max(0, round((loan[6] - total_paid) / emi))
        balance = max(0, loan[6] - total_paid)
        return {
            "loan_id": loan_id,
            "principal": loan[2],
            "total_amount": loan[6],
            "emi": emi,
            "transactions": [{"type": p[0], "amount": p[1], "date": p[2]} for p in payments],
            "total_paid": total_paid,
            "emi_left": emi_left,
            "balance": balance
        }

    def get_account_overview(self, customer_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM loans WHERE customer_id=?", (customer_id,))
        loans = cursor.fetchall()
        overview = []
        for loan in loans:
            loan_id = loan[0]
            cursor.execute("SELECT amount FROM payments WHERE loan_id=?", (loan_id,))
            payments = cursor.fetchall()
            paid = sum(p[0] for p in payments)
            emi_left = max(0, round((loan[6] - paid) / loan[7]))
            overview.append({
                "loan_id": loan_id,
                "principal": loan[2],
                "total_amount": loan[6],
                "emi": loan[7],
                "interest": loan[5],
                "amount_paid": paid,
                "emi_left": emi_left
            })
        return overview
