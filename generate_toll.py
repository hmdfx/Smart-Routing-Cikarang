import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
start_time = datetime(2026, 1, 29, 16, 0, 0) # 4:00 PM
end_time = datetime(2026, 1, 29, 16, 45, 0)  # 4:45 PM

card_types = ['Gold', 'Platinum', 'Black']
prices = [6000, 9000, 15000, 21000]

# Vehicle Distribution: 80% Car, 20% Bus/Truck
vehicle_types = ['Car', 'Bus', 'Truck']
vehicle_weights = [80, 10, 10]

def generate_traffic(gate_name, traffic_condition):
    data = []
    current_time = start_time
    
    while current_time < end_time:
        # Determine time gap based on traffic condition
        if traffic_condition == 'Heavy':
            gap = random.randint(6, 9)   # 6-9 seconds (West Cikarang)
        elif traffic_condition == 'Medium':
            gap = random.randint(10, 20) # 10-20 seconds (North Cikarang)
        else: # Low
            gap = random.randint(30, 90) # 30-90 seconds (Cibatu)
            
        # Add gap to current time
        current_time += timedelta(seconds=gap)
        
        # Stop if we exceed 4:45 PM
        if current_time > end_time:
            break
            
        # Select vehicle type (80% Car, 20% Others)
        vehicle = random.choices(vehicle_types, weights=vehicle_weights, k=1)[0]
        
        # Select random card and price
        card = random.choice(card_types)
        price = random.choice(prices)
        
        # Format Date & Time as string
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        data.append([time_str, vehicle, card, price])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date & Time', 'Vehicle Type', 'Card Name', 'Price'])
    
    # Save to CSV
    filename = f"{gate_name.replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)
    print(f"Generated {filename} | {len(df)} vehicles | {traffic_condition}")
    return df

# Generate the three datasets
print("Generating Traffic Data (4:00 PM - 4:45 PM)...\n")
df_north = generate_traffic("North Cikarang Toll Gate", "Medium")
df_west = generate_traffic("West Cikarang Toll Gate 3", "Heavy")
df_cibatu = generate_traffic("Cibatu Toll Gate", "Low")

# Preview the heavy traffic data
print("\nPreview: West Cikarang Toll Gate 3")
print(df_west[['Date & Time', 'Vehicle Type']].head(5))