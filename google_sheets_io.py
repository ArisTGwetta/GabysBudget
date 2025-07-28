import os
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# 🔐 Secure credentials path
#CREDENTIALS_PATH = "C:/Users/arist/Downloads/GithubSecrets/gabysmoneyapp-73bccc529559.json"
import streamlit as st

service_account_info = st.secrets["google_sheets"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(credentials)


# 🔍 Try to load service account credentials
try:
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"❌ Credential file not found at: {CREDENTIALS_PATH}")

    with open(CREDENTIALS_PATH, "r") as f:
        service_account_info = json.load(f)

    # ✨ Define API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # ✅ Create credentials object & Sheets client
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(credentials)

    # 📗 Open spreadsheet and access worksheets
    spreadsheet = client.open("APP Memory - Gabys-Money")
    accounts_ws = spreadsheet.worksheet("Accounts")
    budget_ws = spreadsheet.worksheet("Budget")
    transactions_ws = spreadsheet.worksheet("Transactions")

except Exception as e:
    print(f"⚠️ Google Sheets setup failed: {e}")
    client = None
    spreadsheet = None
    accounts_ws = budget_ws = transactions_ws = None

# 📊 Load data from Google Sheets
def load_data():
    if not all([accounts_ws, budget_ws, transactions_ws]):
        raise RuntimeError("Sheets not initialized—cannot load data.")
    accounts = pd.DataFrame(accounts_ws.get_all_records())
    budget = pd.DataFrame(budget_ws.get_all_records())
    transactions = pd.DataFrame(transactions_ws.get_all_records())
    return accounts, budget, transactions

# 📝 Save data back to Google Sheets
def save_data(accounts_df, budget_df, transactions_df):
    if not all([accounts_ws, budget_ws, transactions_ws]):
        raise RuntimeError("Sheets not initialized—cannot save data.")

    accounts_ws.clear()
    if not accounts_df.empty:
        accounts_ws.update([accounts_df.columns.tolist()] + accounts_df.values.tolist())

    budget_ws.clear()
    if not budget_df.empty:
        budget_ws.update([budget_df.columns.tolist()] + budget_df.values.tolist())

    transactions_ws.clear()
    if not transactions_df.empty:
        transactions_ws.update([transactions_df.columns.tolist()] + transactions_df.values.tolist())