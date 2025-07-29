import streamlit as st
import gspread
gc = gspread.service_account_from_dict(st.secrets["google_sheets"])
sheet = gc.open("APP Memory - Gabys-Money").worksheet("Accounts")
st.write(sheet.row_values(1))  # Prints header row if connected
