import random
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["resource_allocation"]
initial_data_collection = db["initial_data"]

# Generate initial data
regions = ["Region_0", "Region_1", "Region_2", "Region_3", "Region_4", "Region_5", "Region_6", "Region_7", "Region_8", "Region_9"]

def generate_initial_data():
    data = []
    for region_id in range(5):  # Limiting to 5 regions
        region_data = {
            "region_id": region_id,
            "population_density": random.randint(100, 1000),
            "road_block_status": random.choice([0, 1]),  # 0: no block, 1: road block
            "severity_score": random.randint(0, 100),  # Generate severity score between 0 and 100
            "resource_needs": {
                "food": random.randint(1000, 5000),
                "water": random.randint(500, 3000),
                "medical": random.randint(100, 1000)
            }
        }
        data.append(region_data)
    initial_data_collection.insert_many(data)

if __name__ == "__main__":
    generate_initial_data()
    print("Initial data generated and stored in MongoDB.")
