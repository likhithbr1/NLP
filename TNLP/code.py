import sys
from llama_cpp import Llama

# -------------------------------
# Model Configuration
# -------------------------------
MODEL_PATH = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"  # Replace with your actual model path
N_CTX = 2048
N_THREADS = 6
VERBOSE = True

# -------------------------------
# Prompt Template
# -------------------------------
PROMPT_TEMPLATE = """
You are an assistant that extracts filters for querying orders from different source systems.

Your goal is to extract the following fields in JSON format:
- source_system (choose from the list below)
- order_type (always set to "ALL")
- order_status (choose from list, default to "ALL")
- order_action (choose from list, default to "ALL")
- start_date (extract from natural language, like "last week", "Jan 2023", etc.)
- end_date (optional, default to "now" if not provided)

Valid options:

source_system:
- EON
- PIPELINE
- SWIFT
- SALESFORCE
- SDP_FOA
- SDP_OA
- SDP_ORION
- SERVICENOW_ORDER
- VLOCITY_ORDER

order_status:
- ALL
- In progress
- entered
- cancelled
- complete
- rejected
- incomplete Entry
- hiberated activation

order_action:
- ALL
- Install
- disconnect
- change
- legacy

Rules:
- If source_system is not mentioned, default to "EON"
- order_type is always "ALL"
- If order_status is not mentioned, default to "ALL"
- If order_action is not mentioned, default to "ALL"
- Always output date fields as natural phrases (e.g., "last 7 days", "March 1 to March 5")
- Respond in pure JSON with lowercase keys, no explanation or extra text

Examples:

Input: "Give me all completed install orders from SALESFORCE from Jan to Feb 2024"
Output:
{
  "source_system": "SALESFORCE",
  "order_type": "ALL",
  "order_status": "complete",
  "order_action": "Install",
  "start_date": "January 2024",
  "end_date": "February 2024"
}

Input: "Show me in progress change orders from SDP_OA for the last 5 hours"
Output:
{
  "source_system": "SDP_OA",
  "order_type": "ALL",
  "order_status": "In progress",
  "order_action": "change",
  "start_date": "last 5 hours",
  "end_date": "now"
}

Input: "Get me order details from PIPELINE for March 1"
Output:
{
  "source_system": "PIPELINE",
  "order_type": "ALL",
  "order_status": "ALL",
  "order_action": "ALL",
  "start_date": "March 1",
  "end_date": "now"
}
""".strip()

def main():
    # Instantiate the Llama model (this may take a few seconds to load)
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        verbose=VERBOSE
    )

    print("Type your queries (or 'exit' to quit).")

    while True:
        user_input = input("\nUser Query: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        # Build the final prompt
        # We add a new "Input:" line for the user's query, then "Output:" for the LLM's JSON
        prompt = f"{PROMPT_TEMPLATE}\n\nInput: \"{user_input}\"\nOutput:\n"

        # Generate the response
        # Note: You may want to tweak max_tokens, temperature, top_p, etc. for your use case.
        output = llm(
            prompt=prompt,
            max_tokens=512,
            stop=["Input:", "Output:"],  # Stop tokens to keep the model from running on
        )

        # Extract text from the LLM's response
        response_text = output["choices"][0]["text"].strip()

        print("\nLLM Response (raw):")
        print(response_text)
        print()

        # (Optional) If you trust the JSON structure, you can attempt to parse it:
        # try:
        #     parsed_json = json.loads(response_text)
        #     print("Parsed JSON:", parsed_json)
        # except Exception as e:
        #     print("Failed to parse JSON. Error:", e)

if __name__ == "__main__":
    main()
