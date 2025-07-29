import streamlit as st

try:
    import gspread
except ModuleNotFoundError as e:
    st.error(f"🧩 Missing module: {e}")
    st.stop()

try:
    import pandas as pd
    from datetime import datetime
    from google.oauth2.service_account import Credentials

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=SCOPES)
    client = gspread.authorize(creds)
    SHEET_NAME = "APP Memory - Gabys-Money"
    sheet = client.open(SHEET_NAME)

except Exception as e:
    st.error(f"🌧️ App startup error: {e.__class__.__name__}: {e}")

# 🧪 Data Sync Functions

# 🌿 Column headers for consistency
ACCOUNT_COLUMNS = ["Account", "Balance"]
BUDGET_COLUMNS = ["Category", "Monthly Budget"]
TRANSACTION_COLUMNS = ["Date", "Description", "Amount", "From Account", "To Account", "Category"]

# 🧪 Load Functions
def load_accounts_from_sheet():
    try:
        df = pd.DataFrame(sheet.worksheet("Accounts").get_all_values()[1:], columns=ACCOUNT_COLUMNS)
        df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce").fillna(0)
        st.session_state.accounts = df
    except Exception as e:
        st.error(f"Error loading accounts: {e}")

def load_budget_from_sheet():
    try:
        df = pd.DataFrame(sheet.worksheet("Budget").get_all_values()[1:], columns=BUDGET_COLUMNS)
        df["Monthly Budget"] = pd.to_numeric(df["Monthly Budget"], errors="coerce").fillna(0)
        st.session_state.budget = df
    except Exception as e:
        st.error(f"Error loading budget: {e}")

def load_transactions_from_sheet():
    try:
        df = pd.DataFrame(sheet.worksheet("Transactions").get_all_values()[1:], columns=TRANSACTION_COLUMNS)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        st.session_state.transactions = df
    except Exception as e:
        st.error(f"Error loading transactions: {e}")

# 💾 Save Functions
def save_accounts_to_sheet():
    try:
        sheet.worksheet("Accounts").update("A1", [ACCOUNT_COLUMNS] + st.session_state.accounts.astype(str).values.tolist())
    except Exception as e:
        st.error(f"Error saving accounts: {e}")

def save_budget_to_sheet():
    try:
        sheet.worksheet("Budget").update("A1", [BUDGET_COLUMNS] + st.session_state.budget.astype(str).values.tolist())
    except Exception as e:
        st.error(f"Error saving budget: {e}")

def save_transactions_to_sheet():
    try:
        sheet.worksheet("Transactions").update("A1", [TRANSACTION_COLUMNS] + st.session_state.transactions.astype(str).values.tolist())
    except Exception as e:
        st.error(f"Error saving transactions: {e}")

# 🖼️ App Layout Settings
st.set_page_config(
    page_title="🌸 Gaby’s Budget Garden",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌱 Session State Setup
if "accounts" not in st.session_state: st.session_state.accounts = pd.DataFrame(columns=["Account", "Balance"])
if "budget" not in st.session_state: st.session_state.budget = pd.DataFrame(columns=["Category", "Monthly Budget"])
if "transactions" not in st.session_state: st.session_state.transactions = pd.DataFrame(columns=[
    "Date", "Description", "Amount", "From Account", "To Account", "Category"
])
if "edit_index" not in st.session_state: st.session_state.edit_index = None
if "show_tour" not in st.session_state: st.session_state.show_tour = True
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# 🔄 Load Data
load_accounts_from_sheet()
load_budget_from_sheet()
load_transactions_from_sheet()

# 🌸 Welcome Tour
if st.session_state.show_tour:
    st.markdown("## 🌼 Welcome to Gaby’s Budget Garden!")
    st.markdown("You’re about to unlock your money superpowers 💖 Ready to begin?")
    if st.button("✨ Take the Tour"):
        st.markdown("- 💼 Create financial accounts\n- 🎮 Budget with emoji themes\n- 📈 Track spending like a garden")
    if st.button("🌷 I'm ready to start!"):
        st.session_state.show_tour = False
        st.session_state.page = "Setup"
        st.rerun()

# 📚 Navigation
st.sidebar.title("🌸 Navigation")
st.session_state.page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Setup", "Log Transaction"],
    index=["Dashboard", "Setup", "Log Transaction"].index(st.session_state.page)
)

# 🧭 Page Routing

if st.session_state.page == "Setup":
    st.title("💼 Setup Your Budget Garden")

    st.subheader("🌿 Create Financial Accounts")
    with st.form("account_form"):
        account_name = st.text_input("Account Name (e.g., 'Piggy Bank')")
        starting_balance = st.number_input("Starting Balance", min_value=0.0, step=1.0)
        submitted_account = st.form_submit_button("Add Account")

        if submitted_account:
            new_row = pd.DataFrame([[account_name, starting_balance]], columns=["Account", "Balance"])
            st.session_state.accounts = pd.concat([st.session_state.accounts, new_row], ignore_index=True)
            save_accounts_to_sheet()
            st.success(f"🌼 Added account '{account_name}'!")

    if not st.session_state.accounts.empty:
        st.markdown("### 🧺 Existing Accounts")
        st.dataframe(st.session_state.accounts, use_container_width=True)

    st.subheader("🎨 Create Budget Categories")
    with st.form("budget_form"):
        category_name = st.text_input("Category Name (e.g., 'Bubble Tea')")
        monthly_limit = st.number_input("Monthly Budget", min_value=0.0, step=1.0)
        submitted_category = st.form_submit_button("Add Category")

        if submitted_category:
            new_row = pd.DataFrame([[category_name, monthly_limit]], columns=["Category", "Monthly Budget"])
            st.session_state.budget = pd.concat([st.session_state.budget, new_row], ignore_index=True)
            save_budget_to_sheet()
            st.success(f"🎨 Added category '{category_name}'!")

    if not st.session_state.budget.empty:
        st.markdown("### 🍭 Budget Categories")
        st.dataframe(st.session_state.budget, use_container_width=True)

elif st.session_state.page == "Log Transaction":
    st.title("🧾 Log a Transaction")

    if st.session_state.accounts.empty or st.session_state.budget.empty:
        st.warning("⚠️ You need at least one account and one category before logging transactions.")
    else:
        with st.form("transaction_form"):
            date = st.date_input("Date", value=datetime.today())
            description = st.text_input("Description", placeholder="e.g. Ice cream with Gaby")
            amount = st.number_input("Amount", min_value=0.01, step=0.01)
            from_account = st.selectbox("From Account", st.session_state.accounts["Account"])
            to_account = st.selectbox("To Account (optional)", [""] + list(st.session_state.accounts["Account"]))
            category = st.selectbox("Category", st.session_state.budget["Category"])

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                new_trans = pd.DataFrame([[
                    date, description, amount, from_account, to_account, category
                ]], columns=["Date", "Description", "Amount", "From Account", "To Account", "Category"])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_trans], ignore_index=True)

                idx_from = st.session_state.accounts[st.session_state.accounts["Account"] == from_account].index[0]
                st.session_state.accounts.at[idx_from, "Balance"] -= amount

                if to_account:
                    idx_to = st.session_state.accounts[st.session_state.accounts["Account"] == to_account].index[0]
                    st.session_state.accounts.at[idx_to, "Balance"] += amount

                save_transactions_to_sheet()
                save_accounts_to_sheet()
                st.success(f"🌟 Logged transaction: {description} for ${amount:.2f}")

        if not st.session_state.transactions.empty:
            st.markdown("### 📘 Recent Transactions")
            st.dataframe(
                st.session_state.transactions.sort_values("Date", ascending=False).head(10),
                use_container_width=True
            )
elif st.session_state.page == "Dashboard":
    st.title("📊 Gaby’s Garden Dashboard")

    if st.session_state.accounts.empty:
        st.warning("🌱 No accounts yet! Create one in Setup to see the garden bloom.")
    else:
        st.subheader("💰 Account Balances")
        st.dataframe(st.session_state.accounts, use_container_width=True)

    if st.session_state.transactions.empty or st.session_state.budget.empty:
        st.info("🍃 Start logging transactions and adding budget categories to see insights.")
    else:
        st.subheader("🍭 Spending by Category")

        category_totals = st.session_state.transactions.groupby("Category")["Amount"].sum().reset_index()
        budget_df = st.session_state.budget.copy()
        merged = pd.merge(budget_df, category_totals, on="Category", how="left").fillna(0)
        merged["Remaining"] = merged["Monthly Budget"] - merged["Amount"]

        st.dataframe(merged, use_container_width=True)

        st.markdown("### 🌼 Budget Usage Overview")
        chart_df = merged.set_index("Category")[["Monthly Budget", "Amount"]]
        st.bar_chart(chart_df, use_container_width=True)
