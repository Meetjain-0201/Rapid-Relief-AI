from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["resource_allocation"]
collection = db["initial_data"]

def calculate_severity():
    for entry in collection.find():
        population_density = entry["population_density"]
        road_block_status = entry["road_block_status"]
        severity_score = population_density * (1.5 if road_block_status else 1.0)
        
        collection.update_one(
            {"region_id": entry["region_id"]},
            {"$set": {"severity_score": severity_score}}
        )
    print("Severity scores calculated and updated in MongoDB.")

if __name__ == "__main__":
    calculate_severity()
