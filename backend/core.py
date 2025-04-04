import os
import sys
from typing import Optional
import logging
import re

# Disable LangChain debug logs
logging.getLogger("langchain").setLevel(logging.ERROR)
import langchain
langchain.debug = False

# Import LangChain Community utilities and (we no longer use HuggingFacePipeline)
from langchain_community.utilities import SQLDatabase

from sqlalchemy import create_engine, inspect, text

import torch
# We no longer use transformers for model loading

# ----- New: Use Mistral-7B-Instruct-v0-2.Q4_km.gguf via llama-cpp-python -----
from llama_cpp import Llama

# Define a wrapper so our LLM interface remains the same:
class MistralLLM:
    def __init__(self, model_path: str, n_ctx: int, n_threads: int, verbose: bool):
        print("⏳ Loading Mistral-7B-Instruct model (llama-cpp)...")
        self.llama = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=verbose
        )
        print("✅ Model loaded!")
    
    def __call__(self, prompt: str) -> str:
        # Call the model and return the generated text.
        output = self.llama(
            prompt,
            max_tokens=512,
            stop=["</s>","SQL:"])
        # Expecting output in the form: {"choices": [{"text": "..."}], ...}
        return output["choices"][0]["text"].strip()

# Set your model path and parameters here:
MODEL_PATH = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"  # Replace with your actual model path
N_CTX = 2048
N_THREADS = 6
VERBOSE = True
# ----- End New Model Loading Section -----

def load_mistral_llm():
    return MistralLLM(model_path=MODEL_PATH, n_ctx=N_CTX, n_threads=N_THREADS, verbose=VERBOSE)

def pick_tables(question: str, all_tables: list) -> list:
    """Naive approach: pick tables whose names appear in the user's question.
       Fallback: pick the first 3 tables."""
    question_lower = question.lower()
    relevant = [t for t in all_tables if t.lower() in question_lower]
    return relevant or all_tables[:3]

def get_schema_text(db: SQLDatabase, db_uri: str) -> str:
    """
    Build a textual representation of the schema from the database.
    For each table, list its columns, types, and foreign key constraints.
    Uses SQLDatabase.get_table_info(); if that fails, falls back on SQLAlchemy inspector.
    """
    engine = create_engine(db_uri)
    inspector = inspect(engine)
    tables = db.get_usable_table_names()
    lines = []
    for tbl in tables:
        lines.append(f"Table: {tbl}")
        try:
            columns = db.get_table_info(tbl)
            if not columns:
                raise Exception("No columns found")
            for col in columns:
                lines.append(f"  - {col['name']} ({col['type']})")
        except Exception as e:
            try:
                cols = inspector.get_columns(tbl)
                for col in cols:
                    lines.append(f"  - {col['name']} ({col['type']})")
            except Exception as e2:
                lines.append("  - [Error retrieving columns]")
        # Retrieve foreign key constraints
        try:
            fks = inspector.get_foreign_keys(tbl)
            if fks:
                for fk in fks:
                    constrained = ", ".join(fk.get("constrained_columns", []))
                    referred = fk.get("referred_table", "Unknown")
                    lines.append(f"  * FK: {constrained} -> {referred}")
        except Exception as e:
            lines.append("  * [Error retrieving foreign keys]")
        lines.append("")  # Blank line between tables
    return "\n".join(lines).strip()

def extract_sql_query(text: str) -> str:
    """
    Extracts the SQL query from the model's response.
    Removes ```sql blocks and grabs the first valid SQL statement.
    """
    # Remove markdown-style SQL code block (```sql ... ```)
    text = text.strip()
    if text.startswith("```sql"):
        text = text.removeprefix("```sql").strip()
    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    # Now extract the actual SQL query
    pattern = re.compile(r"(?i)(SELECT|INSERT|UPDATE|DELETE).*?;", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(0).strip()
    else:
        return text.strip()
def generate_sql_custom(question: str, schema_text: str, llm) -> str:
    """
    Manually constructs a prompt (similar to your base version) and uses the LLM
    to generate a SQL query.
    """
    prompt = (
        "Generate an SQL query strictly based on the schema provided.\n\n"
        f"Schema:\n{schema_text}\n\n"
        f"Question:\n{question}\n\n"
        "Only output SQL code. Do not output any explanation or additional text.\n"
        "SQL:"
    )
    result = llm(prompt)
    return result.strip()

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text

def process_question(question: str, db_uri: str, llm) -> dict:
    """
    Process a user question and return generated SQL and DB results.
    This is the web-friendly version of the original main() loop.
    """

    # 1) Build a wide DB for table discovery
    wide_db = SQLDatabase.from_uri(db_uri)
    all_table_names = wide_db.get_usable_table_names()

    # 2) Choose relevant tables using partial schema selection
    relevant_tables = pick_tables(question, all_table_names)

    # 3) Reflect columns only for relevant tables
    filtered_db = SQLDatabase.from_uri(db_uri, include_tables=relevant_tables)

    # 4) Build a schema text from the filtered DB (including FK info)
    schema_text = get_schema_text(filtered_db, db_uri)

    # 5) Generate SQL using the custom prompt (manual logic)
    sql_query_raw = generate_sql_custom(question, schema_text, llm)
    final_sql = extract_sql_query(sql_query_raw)

    # 6) Execute the SQL query using SQLAlchemy
    engine = create_engine(db_uri)
    with engine.connect() as connection:
        result = connection.execute(text(final_sql))
        rows = [dict(row._mapping) for row in result.fetchall()]  # Convert to list of dicts

    # 7) Return SQL + results
    return {
        "sql": final_sql,
        "results": rows
    }
