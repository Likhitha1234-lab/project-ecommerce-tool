import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

os.environ['GROQ_MODEL']

faqs_path = Path(__file__).parent/"resources/faq_data.csv"
chroma_client = chromadb.Client()
collection_name_faq = 'faqs'
groq_client = Groq()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Distance threshold for relevance filtering.
# Chroma's default distance for this embedding function is cosine distance
# (lower = more similar, 0 = identical). Tune this based on what you see
# when you print distances for your own FAQ data - start around 1.0-1.3
# and tighten/loosen from there.
DISTANCE_THRESHOLD = 1.2


def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in chroma_client.list_collections()]:
        print("Ingesting FAQ data into Chromadb...✅")
        collection = chroma_client.get_or_create_collection(
            name=collection_name_faq,
            embedding_function=ef
        )
        df = pd.read_csv(path)
        docs = df['question'].to_list()
        metadata = [{"answer": ans} for ans in df['answer'].to_list()]
        ids = [f"id_{i}" for i in range(len(docs))]

        collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )
        print(f"FAQ Data successfully ingested into Chroma collection:{collection_name_faq}")
    else:
        print(f"Collection {collection_name_faq} already exists")


def get_relevant_qa(query, n_results=2):
    collection = chroma_client.get_collection(
        name=collection_name_faq,
        embedding_function=ef
    )
    result = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return result


def faq_chain(query, debug=False):
    result = get_relevant_qa(query)

    documents = result['documents'][0]
    metadatas = result['metadatas'][0]
    distances = result['distances'][0]

    if debug:
        for doc, dist in zip(documents, distances):
            print(f"[{dist:.4f}] {doc}")

    # Keep only results that are actually close enough to be relevant.
    relevant_answers = [
        meta.get('answer')
        for meta, dist in zip(metadatas, distances)
        if dist <= DISTANCE_THRESHOLD
    ]

    if not relevant_answers:
        return "I don't know."

    context = '\n\n'.join(relevant_answers)
    answer = generate_answer(query, context)
    return answer


def generate_answer(query, context):
    prompt = f'''Given the question and the context below, generate the answer based on context only.
    If you don't find the answer inside the context then say "I don't know".
    Do not make things up.

    QUESTION: {query}

    CONTEXT: {context}
    '''
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0,
        max_completion_tokens=1024
    )

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    ingest_faq_data(faqs_path)
    query = "Do you take cash as payment option?"
    answer = faq_chain(query, debug=True)
    print(answer)