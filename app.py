from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    name = db.Column(db.String(100))
    symbol = db.Column(db.String(20))
    buy_price = db.Column(db.Float)
    quantity = db.Column(db.Float)
    interest = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    action = db.Column(db.String(20))
    price = db.Column(db.Float)
    quantity = db.Column(db.Float)
    date = db.Column(db.String(20))
    notes = db.Column(db.Text)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20))
    added_price = db.Column(db.Float)
    notes = db.Column(db.Text)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assets", methods=["GET", "POST"])
def handle_assets():
    if request.method == "POST":
        data = request.json
        asset = Asset(**data)
        db.session.add(asset)
        db.session.commit()
        return jsonify({"message": "Asset added."}), 201
    else:
        assets = Asset.query.all()
        result = []
        for a in assets:
            result.append({
                "id": a.id,
                "type": a.type,
                "name": a.name,
                "symbol": a.symbol,
                "buy_price": a.buy_price,
                "quantity": a.quantity,
                "interest": a.interest,
                "notes": a.notes
            })
        return jsonify(result)

@app.route("/transactions", methods=["GET", "POST"])
def handle_transactions():
    if request.method == "POST":
        data = request.json
        txn = Transaction(**data)
        db.session.add(txn)
        db.session.commit()
        return jsonify({"message": "Transaction recorded."}), 201
    else:
        txns = Transaction.query.all()
        result = []
        for t in txns:
            result.append({
                "id": t.id,
                "asset_id": t.asset_id,
                "action": t.action,
                "price": t.price,
                "quantity": t.quantity,
                "date": t.date,
                "notes": t.notes
            })
        return jsonify(result)

@app.route("/price/<symbol>")
def get_price(symbol):
    if symbol.upper().endswith("-USD"):
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower().replace('-usd','')}&vs_currencies=usd")
        return jsonify(response.json())
    else:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return jsonify({"price": round(price, 2)})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
