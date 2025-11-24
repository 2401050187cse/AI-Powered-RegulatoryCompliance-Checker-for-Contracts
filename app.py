import os
import json
from groq import Groq
from dotenv import load_dotenv

# --- Load Groq API key ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Paths ---
Dataset_file = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\Dataset\Dataset.txt"
cache_file = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\processed_results.json"
final_result_file = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\final_result.txt"

# --- Load or initialize cache ---
if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

# --- Read dataset ---
if not os.path.exists(Dataset_file):
    raise FileNotFoundError(f"Dataset file not found: {Dataset_file}")

with open(Dataset_file, "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ Loaded dataset.txt ({len(content)} characters)")
if not content.strip():
    raise ValueError("⚠️ dataset.txt is empty")
print("✅ dataset.txt loaded successfully")

# --- Automatic transparent chunking ---
def process_large_text(text, model_name="llama-3.1-8b-instant", chunk_size=5000):
    """Process large text safely using chunking behind the scenes."""
    results = []
    num_chunks = (len(text) + chunk_size - 1) // chunk_size  # total number of chunks

    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = text[start:end]
        chunk_id = f"chunk_{i+1}"

        if chunk_id in cache:
            results.append(cache[chunk_id])
            continue

        print(f"📝 Processing chunk {i+1}/{num_chunks}...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Extract key clauses and highlight compliance risks."},
                {"role": "user", "content": chunk}
            ],
            model=model_name,
            temperature=0.7,
            max_tokens=1000
        )

        result = chat_completion.choices[0].message.content
        results.append(result)

        # Update cache
        cache[chunk_id] = result
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)

    # Combine results
    return "\n\n".join(results)

# --- Run processing ---
final_result = process_large_text(content, model_name="llama-3.1-8b-instant")

# --- Save final result ---
with open(final_result_file, "w", encoding="utf-8") as f:
    f.write(final_result)

print(f"\n✅ Final combined result saved to '{final_result_file}'")
