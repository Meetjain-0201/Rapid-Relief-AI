import random
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["resource_allocation"]
collection = db["initial_data"]

def generate_initial_data(num_regions=10):
    data = []
    for i in range(num_regions):
        entry = {
            "region_id": i,
            "population_density": random.randint(100, 500),
            "road_block_status": random.choice([0, 1]),  # 0 = Clear, 1 = Blocked
            "warehouse_stock_status": random.randint(50, 300),  # Arbitrary stock level
            "resource_needs": {
                "food": random.randint(20, 100),
                "water": random.randint(20, 100),
                "medical": random.randint(10, 50)
            }
        }
        data.append(entry)
    collection.insert_many(data)
    print("Initial data generated and stored in MongoDB.")

if __name__ == "__main__":
    generate_initial_data()
