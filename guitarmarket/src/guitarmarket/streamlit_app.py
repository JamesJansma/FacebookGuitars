import os
from playwright.sync_api import sync_playwright

os.system("playwright install --with-deps")

# Handle SQLite for ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except (ImportError, KeyError):
    pass

import sys
import streamlit as st
from crew import Guitarmarket



st.title('Your Guitar Price Comparison')


with st.sidebar:
    st.header('Enter FB Login')
    topic = st.text_input("Username")
    detailed_questions = st.text_area("Password")

if st.button('Run Research'):
    if not topic or not detailed_questions:
        st.error("Please fill all the fields.")
    else:
        inputs = {
            'topic' : 'Guitar'
        }
        try:
            result = Guitarmarket().crew().kickoff(inputs=inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")
        st.subheader("Results of your research project:")
        st.write(result.raw)