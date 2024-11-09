# gan_model.py - REPLACE YOUR EXISTING gan_model.py WITH THIS CODE

import numpy as np
from pymongo import MongoClient
import time
from datetime import datetime

class RealisticDataGenerator:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["resource_allocation"]
        self.collection = self.db["synthetic_data"]
        
        # Initialize base states for consistent generation
        self.base_states = {
            0: {"name": "Delhi", "base_population": 250000, "variation": 0.02},
            1: {"name": "Mumbai", "base_population": 300000, "variation": 0.03},
            2: {"name": "Chennai", "base_population": 200000, "variation": 0.02},
            3: {"name": "Hyderabad", "base_population": 180000, "variation": 0.025},
            4: {"name": "Bangalore", "base_population": 220000, "variation": 0.03}
        }
        
        # Initialize resource consumption rates (units per hour)
        self.consumption_rates = {
            "food": {"base": 0.05, "variation": 0.01},    # 5% of stock per hour ± 1%
            "water": {"base": 0.08, "variation": 0.015},  # 8% of stock per hour ± 1.5%
            "medical": {"base": 0.03, "variation": 0.005} # 3% of stock per hour ± 0.5%
        }
        
        # Store previous states for smooth transitions
        self.previous_states = {}
        self.initialize_states()

    def initialize_states(self):
        """Initialize previous states for all regions"""
        for region_id in self.base_states.keys():
            self.previous_states[region_id] = {
                "population_density": self.base_states[region_id]["base_population"],
                "road_block_status": 0,
                "warehouse_stock_status": {
                    "food": 1000,    # Initial food units
                    "water": 2000,   # Initial water units
                    "medical": 500   # Initial medical supplies
                },
                "last_update": datetime.now()
            }

    def calculate_realistic_change(self, current, base, max_change_percent):
        """Calculate realistic change with momentum"""
        max_change = base * max_change_percent
        change = np.random.uniform(-max_change, max_change)
        # Add momentum (30% of previous change)
        if 'last_change' in self.previous_states:
            change = 0.7 * change + 0.3 * self.previous_states.get('last_change', 0)
        self.previous_states['last_change'] = change
        return current + change

    def update_resource_needs(self, region_id, current_stock):
        """Calculate resource needs based on current stock and consumption rates"""
        needs = {}
        for resource, rate in self.consumption_rates.items():
            base_consumption = current_stock[resource] * rate["base"]
            variation = np.random.uniform(-rate["variation"], rate["variation"])
            consumption = base_consumption * (1 + variation)
            needs[resource] = max(0, min(100, consumption))
        return needs

    def generate_synthetic_data(self):
        """Generate synthetic data for all regions"""
        current_time = datetime.now()
        synthetic_data = []

        for region_id, base_info in self.base_states.items():
            prev_state = self.previous_states[region_id]
            time_diff = (current_time - prev_state["last_update"]).total_seconds() / 3600.0

            # Update population with small random variations
            new_population = self.calculate_realistic_change(
                prev_state["population_density"],
                base_info["base_population"],
                base_info["variation"]
            )

            # Update road status with 5% chance of change
            new_road_status = prev_state["road_block_status"]
            if np.random.random() < 0.05:  # 5% chance to change
                new_road_status = 1 - new_road_status

            # Update warehouse stock based on consumption rates
            new_stock = {}
            for resource, current in prev_state["warehouse_stock_status"].items():
                consumption_rate = self.consumption_rates[resource]["base"]
                variation = self.consumption_rates[resource]["variation"]
                actual_rate = consumption_rate * (1 + np.random.uniform(-variation, variation))
                new_stock[resource] = max(0, current - (actual_rate * time_diff * current))

            # Calculate severity score
            severity_score = (new_population / base_info["base_population"] * 50 +
                            new_road_status * 30 +
                            (1 - min(1, sum(new_stock.values()) / sum(prev_state["warehouse_stock_status"].values()))) * 20)

            # Generate entry
            entry = {
                "region_id": region_id,
                "region_name": base_info["name"],
                "population_density": int(new_population),
                "road_block_status": new_road_status,
                "warehouse_stock_status": new_stock,
                "resource_needs": self.update_resource_needs(region_id, new_stock),
                "severity_score": min(100, max(0, severity_score)),
                "timestamp": current_time
            }
            
            synthetic_data.append(entry)
            
            # Update previous state
            self.previous_states[region_id] = {
                "population_density": new_population,
                "road_block_status": new_road_status,
                "warehouse_stock_status": new_stock,
                "last_update": current_time
            }

        # Update MongoDB
        self.collection.delete_many({})  # Clear previous data
        self.collection.insert_many(synthetic_data)
        print(f"Generated realistic data at {current_time}")

def main():
    generator = RealisticDataGenerator()
    while True:
        generator.generate_synthetic_data()
        time.sleep(3)  # Update every 3 seconds

if __name__ == "__main__":
    main()