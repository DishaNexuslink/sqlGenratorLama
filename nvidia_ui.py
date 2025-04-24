

# import json
# import tiktoken
# from openai import OpenAI

# # === Load tokenizer ===
# tokenizer = tiktoken.get_encoding("cl100k_base")

# def count_tokens(text):
#     return len(tokenizer.encode(text))

# # === Load schema ===
# with open(r"D:\queryGrok\data\datajson", "r") as f:
#     schema = json.load(f)


# # === Convert schema to readable format ===
# schema_text = json.dumps(schema, indent=2)

# # === Build system prompt ===
# system_prompt = f"""
# You are a SQL query expert.

# You will receive user questions and must generate valid SQL queries based ONLY on the following schema:
# {schema_text}

# Rules:
# - Use only tables/columns from the schema
# - Don't invent columns or join paths
# - Respond with only SQL, no markdown, no explanation
# """


# # === Setup NVIDIA-compatible OpenAI client ===
# client = OpenAI(
#     base_url="https://integrate.api.nvidia.com/v1",
#     api_key="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"
# )

# # === Continuous input loop ===
# print("📥 Enter your question (or type 'exit' to quit):")

# while True:
#     user_question = input(">> ")

#     if user_question.strip().lower() in ("exit", "quit"):
#         print("👋 Exiting...")
#         break

#     # === Build final prompt string for debug/logging ===
#     full_prompt = f"SYSTEM:\n{system_prompt.strip()}\n\nUSER:\n{user_question.strip()}"

#     input_tokens = count_tokens(full_prompt)

#     print("\n🧠 FULL PROMPT SENT TO MODEL:")
#     print("-" * 60)
#     print(full_prompt)
#     print("-" * 60)
#     print(f"🔢 Input Tokens: {input_tokens}")
#     print("\n⏳ Generating SQL...\n")

#     # === Make API call ===
#     output_text = ""
#     output_tokens = 0

#     completion = client.chat.completions.create(
#         model="meta/llama-3.3-70b-instruct",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_question}
#         ],
#         temperature=0,
#         top_p=0.95,
#         max_tokens=4096,
#         stream=True
#     )

#     for chunk in completion:
#         if chunk.choices[0].delta.content:
#             token_piece = chunk.choices[0].delta.content
#             print(token_piece, end="")
#             output_tokens += count_tokens(token_piece)

#     print("\n")
#     print(f"🔢 Tokens → Input: {input_tokens}, Output: {output_tokens}, Total: {input_tokens + output_tokens}")




import streamlit as st
import json
import tiktoken
import time
from openai import OpenAI

# === Load tokenizer ===
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(tokenizer.encode(text))

# === Load schema ===
with open(r"data\datajson", "r") as f:
    schema = json.load(f)

    schema = json.load(f)


# === Convert schema to readable format ===
schema_text = json.dumps(schema, indent=2)

# === Build system prompt ===
# system_prompt = f"""
# You are a SQL query expert.

# You will receive user questions and must generate valid SQL queries based ONLY on the following schema:
# {schema_text}

# Rules:
# - Use only tables/columns from the schema
# - Don't invent columns or join paths
# - Respond with only SQL, no markdown, no explanation
# """

system_prompt = f"""
You are an expert MS SQL assistant. Based on the database schema provided and the user’s question, generate a syntactically correct and semantically accurate SQL query.

Instructions:

Only use table names and column names exactly as provided in the schema.

Ensure all JOINs are logically valid, using correct foreign key relationships or inferred connections from the schema.

Do not guess or invent any table or column name not explicitly present in the schema.

Ensure there are no typos or spelling mistakes in the SQL.

Return only the SQL query, without explanations or comments.

Return logical column aliases for each calculated field

Only apply math functions like AVG() or SUM() to numeric fields — if the column is text but contains numeric values, explicitly cast it (e.g., CAST(column AS FLOAT)) before using.

Data types are respected when using functions like AVG(), SUM(), MAX(), etc.

Always reference columns from the correct table alias based on where they are defined in the schema. Never assume a surrogate key like ID exists in a table unless explicitly defined — use composite keys if needed.
Schema:
{schema}


"""
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

# === Setup OpenAI/NVIDIA-compatible client ===
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

# === Streamlit UI ===
st.set_page_config(page_title="Schema-aware SQL Generator", layout="centered")
st.title("🧠 SQL Generator from Schema")

user_question = st.text_area("💬 Ask a question:", height=100)

generate = st.button("🚀 Generate SQL")

if generate and user_question.strip():
    with st.spinner("⏳ Generating SQL..."):
        start_time = time.time()

        full_prompt = f"SYSTEM:\n{system_prompt.strip()}\n\nUSER:\n{user_question.strip()}"
        input_tokens = count_tokens(full_prompt)

        completion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0,
            top_p=0.95,
            max_tokens=4096,
            stream=True
        )

        output_text = ""
        output_tokens = 0

        for chunk in completion:
            if chunk.choices[0].delta.content:
                token_piece = chunk.choices[0].delta.content
                output_text += token_piece
                output_tokens += count_tokens(token_piece)

        end_time = time.time()
        total_tokens = input_tokens + output_tokens

        st.subheader("🧠 Generated SQL Query:")
        st.code(output_text.strip(), language="sql")

        st.subheader("📊 Stats")
        st.markdown(f"**Input Tokens:** {input_tokens}")
        st.markdown(f"**Output Tokens:** {output_tokens}")
        st.markdown(f"**Total Tokens:** {total_tokens}")
        st.markdown(f"**Time Taken:** {end_time - start_time:.2f} seconds")
