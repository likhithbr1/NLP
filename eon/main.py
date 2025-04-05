# main.py
import sys
import json
from llm_model import get_llm, PROMPT_TEMPLATE
from date_util import convert_to_sql_dates
from sql_builder import build_sql_query
from db_connection import get_db_connection

def main():
    # Establish DB connection once at startup.
    conn = get_db_connection()
    cursor = conn.cursor()

    # Instantiate the LLM model.
    llm = get_llm()

    print("Type your queries (or 'exit' to quit).")

    while True:
        user_input = input("\nUser Query: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        # Build the prompt with the user query.
        prompt = f"{PROMPT_TEMPLATE}\n\nInput: \"{user_input}\"\nOutput:\n"
        output = llm(
            prompt=prompt,
            max_tokens=512,
            stop=["Input:", "Output:"],
        )
        response_text = output["choices"][0]["text"].strip()
        print("\nLLM Response (raw):")
        print(response_text)

        try:
            response_data = json.loads(response_text)
        except Exception as e:
            print(f"\nError parsing JSON: {e}")
            continue

        # Convert fuzzy dates to SQL-compatible format.
        try:
            start_sql, end_sql = convert_to_sql_dates(
                response_data.get("start_date", ""),
                response_data.get("end_date", None)
            )
            response_data["start_date"] = start_sql
            response_data["end_date"] = end_sql
        except Exception as e:
            print(f"\nDate parsing error: {e}")
            continue

        print("\nFinal Parsed Filters (with SQL-compatible dates):")
        print(json.dumps(response_data, indent=2))

        # Build the final SQL query using the extracted filters.
        final_sql = build_sql_query(response_data)
        print("\nExecuting SQL Query against the database...")

        try:
            cursor.execute(final_sql)
            rows = cursor.fetchall()
            # Print out the results (format as needed)
            if rows:
                print("\nDatabase Output:")
                for row in rows:
                    print(row)
            else:
                print("\nNo records found for the given query.")
        except Exception as e:
            print(f"\nError executing SQL query: {e}")

    # Cleanup: close the database connection.
    cursor.close()
    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()
