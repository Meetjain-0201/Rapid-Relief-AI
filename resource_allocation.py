from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["resource_allocation"]
initial_data_collection = db["initial_data"]
allocation_collection = db["resource_allocation"]

def allocate_resources():
    # Limit to 5 regions
    regions = initial_data_collection.find({"region_id": {"$lt": 5}})

    for entry in regions:
        if "severity_score" in entry:  # Check if 'severity_score' exists
            severity_score = entry["severity_score"]
            allocation = {
                "region_id": entry["region_id"],
                "food": entry["resource_needs"]["food"] * severity_score / 100,
                "water": entry["resource_needs"]["water"] * severity_score / 100,
                "medical": entry["resource_needs"]["medical"] * severity_score / 100
            }
            allocation_collection.update_one(
                {"region_id": entry["region_id"]},
                {"$set": allocation},
                upsert=True
            )
        else:
            print(f"Warning: Missing 'severity_score' for region_id {entry['region_id']}")
    print("Resources allocated based on severity scores.")

if __name__ == "__main__":
    allocate_resources()
