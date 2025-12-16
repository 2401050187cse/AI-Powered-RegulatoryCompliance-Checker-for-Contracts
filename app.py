import os
import json
from groq import Groq
from dotenv import load_dotenv

# --------------------------------------------------
# LOAD ENV & INITIALIZE GROQ
# --------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("❌ GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------
DATASET_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\Dataset\Dataset.txt"
CACHE_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\processed_results.json"
FINAL_RESULT_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\final_result.txt"

# --------------------------------------------------
# LOAD CACHE
# --------------------------------------------------
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------
if not os.path.exists(DATASET_FILE):
    raise FileNotFoundError(f"❌ Dataset file not found: {DATASET_FILE}")

with open(DATASET_FILE, "r", encoding="utf-8") as f:
    content = f.read().strip()

if not content:
    raise ValueError("❌ Dataset file is empty")

print(f"✅ Loaded dataset.txt ({len(content)} characters)")

# --------------------------------------------------
# CHUNK PROCESSING FUNCTION
# --------------------------------------------------
def process_large_text(
    text,
    model_name="llama-3.1-8b-instant",
    chunk_size=4000
):
    """
    Process large text using safe chunking with caching.
    """
    results = []
    total_chunks = (len(text) + chunk_size - 1) // chunk_size

    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = text[start:end].strip()

        if not chunk:
            continue

        chunk_id = f"chunk_{i+1}"

        # Use cached result if available
        if chunk_id in cache:
            print(f"⚡ Using cached result for {chunk_id}")
            results.append(cache[chunk_id])
            continue

        print(f"📝 Processing chunk {i+1}/{total_chunks}...")

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a legal compliance assistant. "
                            "Extract key clauses, identify compliance risks, "
                            "and summarize regulatory issues clearly."
                        ),
                    },
                    {"role": "user", "content": chunk},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            result_text = response.choices[0].message.content.strip()
            results.append(result_text)

            # Save to cache
            cache[chunk_id] = result_text
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=4, ensure_ascii=False)

        except Exception as e:
            error_msg = f"❌ Error processing {chunk_id}: {str(e)}"
            print(error_msg)
            results.append(error_msg)

    return "\n\n" + "=" * 80 + "\n\n".join(results)

# --------------------------------------------------
# RUN PROCESSING
# --------------------------------------------------
final_result = process_large_text(content)

# --------------------------------------------------
# SAVE FINAL OUTPUT
# --------------------------------------------------
with open(FINAL_RESULT_FILE, "w", encoding="utf-8") as f:
    f.write(final_result)

print(f"\n✅ Final combined result saved to:\n{FINAL_RESULT_FILE}")
