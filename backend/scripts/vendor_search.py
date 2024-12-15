from pymilvus import MilvusClient
from sentence_transformers.SentenceTransformer import SentenceTransformer

COLLECTION_NAME = "vendor_category_mapping"
client = MilvusClient("./vendors.db")
model = SentenceTransformer('all-MiniLM-L6-v2')


client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=384  # This is the default dimension value of all-MiniLM-L6-v2 model
)
print(f"collection {COLLECTION_NAME} created\n")


def store_mappings(mappings: list[dict]):
    for item in mappings:
        item["vector"] = model.encode([item["description"]])[0].tolist()
    client.insert(collection_name=COLLECTION_NAME, data=mappings)
    for item in mappings:
        print(f"stored {item['description']} => {item['category']}")


def search(query: str):
    to_search = [model.encode([query])[0].tolist()]
    res = client.search(
        collection_name=COLLECTION_NAME,
        data=to_search,
        limit=2,
        output_fields=["description", "category"],
    )[0];
    print(f"\nresult for query: {query}")
    for result in res:
        print(f"Distance: {result['distance']} | {result['entity']['description']} | {result['entity']['category']}")

input_mappings = [
    {"id": 1, "description": "Amazon purchase", "category": "Shopping"},
    {"id": 2, "description": "Uber ride", "category": "Transport"},
    {"id": 3, "description": "Starbucks coffee", "category": "Food & Beverage"},
]
store_mappings(input_mappings)
print(f"stored {len(input_mappings)} mappings\n")

search("coffee")
search("Starbucks")
search("Star")
search("Uber")

client.drop_collection(COLLECTION_NAME)

print(f"\ncollection {COLLECTION_NAME} dropped")
