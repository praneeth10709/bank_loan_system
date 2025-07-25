from flask import Flask, request, jsonify
import uuid
from datetime import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"loans": {}}, f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

@app.route('/lend', methods=['POST'])
def lend():
    data = load_data()
    req = request.get_json()
    customer_id = req["customer_id"]
    principal = req["loan_amount"]
    years = req["loan_period"]
    rate = req["rate_of_interest"]

    interest = (principal * years * rate) // 100
    total_amount = principal + interest
    emi = total_amount // (years * 12)

    loan_id = str(uuid.uuid4())

    data["loans"][loan_id] = {
        "customer_id": customer_id,
        "principal": principal,
        "years": years,
        "rate": rate,
        "interest": interest,
        "total_amount": total_amount,
        "emi": emi,
        "transactions": [],
        "amount_paid": 0
    }

    save_data(data)
    return jsonify({"loan_id": loan_id, "total_amount": total_amount, "emi": emi})

@app.route('/payment', methods=['POST'])
def payment():
    data = load_data()
    req = request.get_json()
    loan_id = req["loan_id"]
    amount = req["amount"]

    if loan_id not in data["loans"]:
        return jsonify({"error": "Invalid loan ID"}), 404

    loan = data["loans"][loan_id]
    loan["amount_paid"] += amount
    loan["transactions"].append({
        "amount": amount,
        "type": "payment",
        "timestamp": datetime.now().isoformat()
    })

    save_data(data)
    return jsonify({"message": "Payment successful", "total_paid": loan["amount_paid"]})

@app.route('/ledger/<loan_id>', methods=['GET'])
def ledger(loan_id):
    data = load_data()
    if loan_id not in data["loans"]:
        return jsonify({"error": "Invalid loan ID"}), 404

    loan = data["loans"][loan_id]
    balance = loan["total_amount"] - loan["amount_paid"]
    emi_left = max((balance + loan["emi"] - 1) // loan["emi"], 0)

    return jsonify({
        "loan_id": loan_id,
        "transactions": loan["transactions"],
        "emi": loan["emi"],
        "balance": balance,
        "emi_left": emi_left
    })
@app.route('/account_overview/<customer_id>', methods=['GET'])
def account_overview(customer_id):
    data = load_data()
    overview = []

    for loan_id, loan in data["loans"].items():
        if loan["customer_id"] == customer_id:
            balance = loan["total_amount"] - loan["amount_paid"]
            emi_left = max((balance + loan["emi"] - 1) // loan["emi"], 0)

            overview.append({
                "loan_id": loan_id,
                "principal": loan["principal"],
                "total_amount": loan["total_amount"],
                "emi": loan["emi"],
                "interest": loan["interest"],
                "paid": loan["amount_paid"],
                "emi_left": emi_left
            })

    return jsonify(overview)


if __name__ == '__main__':
    app.run(debug=True)

