import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

@st.cache_resource
def get_engine():
    """Creates a cached SQLAlchemy engine connected to Supabase Postgres."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("Missing DATABASE_URL in .env file.")

    # Force SQLAlchemy to use psycopg2-binary instead of psycopg3
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return create_engine(db_url, pool_pre_ping=True)


@st.cache_data(ttl=300, show_spinner=False)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Executes a read-only SQL query against k12_education and returns a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


if __name__ == "__main__":
    test_df = run_query("SELECT COUNT(*) AS total_districts FROM k12_education.districts;")
    print("Connected to Supabase! Result:")
    print(test_df)