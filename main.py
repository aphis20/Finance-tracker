# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from typing import List

app = FastAPI()

# Constants
CSV_FILE = "finance_data.csv"
COLUMNS = ["date", "amount", "category", "description"]
DATE_FORMAT = "%d-%m-%Y"

# Initialize CSV
def initialize_csv():
    try:
        pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

# Models
class Transaction(BaseModel):
    date: str
    amount: float
    category: str
    description: str

# Initialize the CSV at the start
initialize_csv()

# Endpoints

@app.get("/")
def read_root():
    return {"message": "Welcome to the Finance Tracker API"}

@app.post("/transactions/")
def add_transaction(transaction: Transaction):
    # Parse the transaction into a DataFrame
    new_entry = {
        "date": transaction.date,
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
    }
    df = pd.DataFrame([new_entry])
    
    # Append the new entry to the CSV
    df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    return {"message": "Transaction added successfully"}

@app.get("/transactions/", response_model=List[Transaction])
def get_transactions():
    try:
        df = pd.read_csv(CSV_FILE)
        transactions = df.to_dict(orient="records")
        return transactions
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No transactions found")

@app.get("/transactions/{start_date}/{end_date}")
def get_transactions_by_date(start_date: str, end_date: str):
    df = pd.read_csv(CSV_FILE)
    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT)
    
    start = datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.strptime(end_date, DATE_FORMAT)
    
    mask = (df["date"] >= start) & (df["date"] <= end)
    filtered_df = df.loc[mask]
    
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No transactions found in the given date range")
    
    return filtered_df.to_dict(orient="records")

@app.delete("/transactions/")
def delete_all_transactions():
    try:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return {"message": "All transactions deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No transactions found")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
