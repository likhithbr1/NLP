import json
from llama_cpp import Llama

MODEL_PATH = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"  # Update as needed
N_CTX = 2048
N_THREADS = 6

# Short prompt telling the model to not guess if date is missing.
BASE_PROMPT = """Extract these fields from the input in JSON, no extra text:

Fields:
- source_system: [EON, PIPELINE, SWIFT, SALESFORCE, SDP_FOA, SDP_OA, SDP_ORION, SERVICENOW_ORDER, VLOCITY_ORDER] (default = EON)
- order_type: always "ALL"
- order_status: [ALL, In progress, entered, cancelled, complete, rejected, incomplete Entry, hiberated activation] (default = ALL)
- order_action: [ALL, Install, disconnect, change, legacy] (default = ALL)
- start_date: user-provided date/time (don't guess if missing)
- end_date: default to "now"

Rules:
- If any required field like start_date is missing, return: {"missing": "start_date"}
- Output compact JSON, no explanation.

Example:
Input: "show me all cancelled install orders from SALESFORCE last week"
Output: {"source_system":"SALESFORCE","order_type":"ALL","order_status":"cancelled","order_action":"Install","start_date":"last week","end_date":"now"}

Input: """

def call_llm(prompt):
    """Calls the local Mistral model with llama-cpp-python and returns text."""
    llama = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        temperature=0.2,
        top_p=0.9,
        max_tokens=256,
        echo=False
    )
    output = llama(prompt=prompt, stop=["Input:", "Output:"], echo=False)
    return output["choices"][0]["text"].strip()

def main():
    print("Type your queries (or 'exit' to quit).")
    while True:
        user_query = input("\nUser Query: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        # Build the one-shot prompt for the user input
        # Use 'Input: "..."' then 'Output:' to force the model's JSON response.
        final_prompt = BASE_PROMPT + f"\"{user_query}\"\nOutput:"

        # 1) First LLM call
        response = call_llm(final_prompt)
        print("\nRaw LLM Response:", response)

        # Try to parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            print("LLM did not return valid JSON. Please try again.")
            continue

        # 2) Check if start_date is missing
        if data.get("missing") == "start_date":
            print("\nLLM says 'start_date' is missing. Please provide a date or time range.")
            date_input = input("Date/Time: ")

            # Append date to the original user query & re-run
            # e.g. "hello i want orders which are cancelled" + " from january" → "hello i want orders which are cancelled from january"
            combined_query = user_query + " from " + date_input

            # Build new prompt
            second_prompt = BASE_PROMPT + f"\"{combined_query}\"\nOutput:"
            second_response = call_llm(second_prompt)

            print("\nFinal LLM Response:", second_response)
            # Attempt to parse final JSON
            try:
                final_data = json.loads(second_response)
                print("Final JSON:", final_data)
            except json.JSONDecodeError:
                print("Could not parse final response as JSON.")
        else:
            # If start_date is present, just show the data
            print("Parsed JSON:", data)

if __name__ == "__main__":
    main()
