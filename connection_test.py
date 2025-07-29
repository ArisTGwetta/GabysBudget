import streamlit as st
import gspread

# Load credentials and create client
gc = gspread.service_account_from_dict(st.secrets["google_sheets"])

# Optional debug: show accessible spreadsheet titles
st.write([s.title for s in gc.openall()])

# Access specific sheet and display header row
sheet = gc.open("APP Memory - Gabys-Money").worksheet("Accounts")
st.write(sheet.row_values(1))
