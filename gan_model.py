# gan_model.py - Updated version with enhanced resource dynamics

import numpy as np
from pymongo import MongoClient
import time
from datetime import datetime

class RealisticDataGenerator:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["resource_allocation"]
        self.collection = self.db["synthetic_data"]
        
        # Initialize base states with realistic parameters
        self.base_states = {
            0: {"name": "Delhi", "base_population": 250000, "base_resources": {"food": 2000, "water": 3000, "medical": 1000}},
            1: {"name": "Mumbai", "base_population": 300000, "base_resources": {"food": 2500, "water": 3500, "medical": 1200}},
            2: {"name": "Chennai", "base_population": 200000, "base_resources": {"food": 1800, "water": 2800, "medical": 900}},
            3: {"name": "Hyderabad", "base_population": 180000, "base_resources": {"food": 1600, "water": 2600, "medical": 800}},
            4: {"name": "Bangalore", "base_population": 220000, "base_resources": {"food": 2000, "water": 3000, "medical": 1000}}
        }
        
        # Increased resource consumption rates per person per hour
        self.consumption_rates = {
            "food": 0.08,    # Increased from 0.02 to 0.08
            "water": 0.15,   # Increased from 0.04 to 0.15
            "medical": 0.04  # Increased from 0.01 to 0.04
        }
        
        # More aggressive resource depletion settings
        self.replenishment_threshold = 0.5   # Increased from 0.3 to 0.5
        self.replenishment_amount = 0.7      # Increased from 0.5 to 0.7
        
        # Random event chances
        self.emergency_chance = 0.1  # 10% chance of emergency event per update
        self.emergency_impact = {
            "food": (0.2, 0.4),    # 20-40% sudden increase in consumption
            "water": (0.3, 0.5),   # 30-50% sudden increase in consumption
            "medical": (0.4, 0.6)  # 40-60% sudden increase in consumption
        }
        
        # Store previous states
        self.previous_states = {}
        self.initialize_states()

    def initialize_states(self):
        """Initialize previous states for all regions"""
        for region_id, base_info in self.base_states.items():
            self.previous_states[region_id] = {
                "population_density": base_info["base_population"],
                "road_block_status": 0,
                "warehouse_stock_status": base_info["base_resources"].copy(),
                "last_update": datetime.now(),
                "resource_needs": {res: 0 for res in self.consumption_rates.keys()}
            }

    def simulate_emergency_event(self, consumption):
        """Simulate sudden increase in resource consumption due to emergency"""
        if np.random.random() < self.emergency_chance:
            for resource in consumption.keys():
                impact_range = self.emergency_impact[resource]
                impact_factor = np.random.uniform(impact_range[0], impact_range[1])
                consumption[resource] *= (1 + impact_factor)
        return consumption

    def calculate_resource_consumption(self, population, time_diff_hours):
        """Calculate realistic resource consumption with more variation"""
        consumption = {}
        for resource, rate in self.consumption_rates.items():
            # Base consumption with increased variation (±30%)
            base_consumption = population * rate * time_diff_hours
            variation = np.random.uniform(0.7, 1.3)
            consumption[resource] = base_consumption * variation
        
        # Add potential emergency consumption
        consumption = self.simulate_emergency_event(consumption)
        return consumption

    def calculate_resource_needs(self, current_stock, base_stock, population):
        """Calculate resource needs with more aggressive thresholds"""
        needs = {}
        for resource in current_stock.keys():
            # Calculate need based on stock level and population requirements
            stock_ratio = current_stock[resource] / base_stock[resource]
            population_factor = population / self.base_states[0]["base_population"]
            
            # More aggressive need calculation
            need = base_stock[resource] * (1.5 - stock_ratio) * population_factor
            
            # Add random surge in needs (0-50% extra)
            surge_factor = np.random.uniform(1.0, 1.5)
            needs[resource] = max(0, need * surge_factor)
        return needs

    def generate_synthetic_data(self):
        """Generate synthetic data with more dynamic resource changes"""
        current_time = datetime.now()
        synthetic_data = []

        for region_id, base_info in self.base_states.items():
            prev_state = self.previous_states[region_id]
            time_diff_hours = (current_time - prev_state["last_update"]).total_seconds() / 3600.0

            # More dynamic population changes (±0.5%)
            population_change = np.random.uniform(-0.005, 0.005) * prev_state["population_density"]
            new_population = max(0, prev_state["population_density"] + population_change)

            # Increased road block changes (10% chance)
            new_road_status = prev_state["road_block_status"]
            if np.random.random() < 0.10:
                new_road_status = 1 - new_road_status

            # Calculate resource consumption
            consumption = self.calculate_resource_consumption(new_population, time_diff_hours)
            
            # Update warehouse stocks
            new_stock = {}
            for resource, current in prev_state["warehouse_stock_status"].items():
                # More aggressive consumption
                new_amount = current - consumption[resource]
                
                # Replenishment logic
                if new_amount < base_info["base_resources"][resource] * self.replenishment_threshold:
                    replenishment = base_info["base_resources"][resource] * self.replenishment_amount
                    new_amount += replenishment
                
                new_stock[resource] = max(0, new_amount)

            # Calculate resource needs
            resource_needs = self.calculate_resource_needs(new_stock, base_info["base_resources"], new_population)

            # Calculate severity score with more weight on resource status
            stock_severity = sum(new_stock.values()) / sum(base_info["base_resources"].values())
            severity_score = (
                (new_population / base_info["base_population"]) * 30 +
                new_road_status * 20 +
                (1 - stock_severity) * 50  # Increased weight on resource status
            )

            # Generate entry
            entry = {
                "region_id": region_id,
                "region_name": base_info["name"],
                "population_density": int(new_population),
                "road_block_status": new_road_status,
                "warehouse_stock_status": new_stock,
                "resource_needs": resource_needs,
                "severity_score": min(100, max(0, severity_score)),
                "timestamp": current_time
            }
            
            synthetic_data.append(entry)
            
            # Update previous state
            self.previous_states[region_id].update({
                "population_density": new_population,
                "road_block_status": new_road_status,
                "warehouse_stock_status": new_stock,
                "resource_needs": resource_needs,
                "last_update": current_time
            })

        # Update MongoDB
        self.collection.delete_many({})
        self.collection.insert_many(synthetic_data)
        print(f"Generated realistic data at {current_time}")

def main():
    generator = RealisticDataGenerator()
    while True:
        generator.generate_synthetic_data()
        time.sleep(3)  # Update every 3 seconds

if __name__ == "__main__":
    main()
