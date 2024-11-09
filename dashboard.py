# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime, timedelta
import time

# Initialize MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["resource_allocation"]
synthetic_collection = db["synthetic_data"]

# Initialize session state for tracking changes
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'previous_data' not in st.session_state:
    st.session_state.previous_data = None

def load_data():
    """Load data from MongoDB"""
    data = list(synthetic_collection.find({}, {'_id': 0}))
    return pd.DataFrame(data)

def calculate_resource_recommendations(df):
    """Calculate resource allocation recommendations based on severity and needs"""
    recommendations = []
    
    for _, row in df.iterrows():
        region_name = row['region_name']
        severity = row['severity_score']
        stocks = row['warehouse_stock_status']
        needs = row['resource_needs']
        
        urgent_resources = []
        for resource, need in needs.items():
            stock = stocks[resource]
            # Mark resource as urgent if stock is less than 3x the need
            if stock < need * 3:
                days_left = stock / need if need > 0 else float('inf')
                urgent_resources.append(f"{resource.capitalize()} (Stock: {stock:.0f}, Need: {need:.0f}, {days_left:.1f} days left)")
        
        # Calculate resource depletion rate
        depletion_warning = []
        for resource, stock in stocks.items():
            if stock < needs[resource] * 4:  # Increased threshold
                days_left = stock / needs[resource] if needs[resource] > 0 else float('inf')
                if days_left < 3:  # Changed from hours to days
                    depletion_warning.append(f"{resource.capitalize()}: {days_left:.1f} days left")
        
        if severity > 70:
            priority = "CRITICAL"
            action = f"Immediate intervention required. {', '.join(depletion_warning)}" if depletion_warning else "Immediate intervention required."
        elif severity > 50:
            priority = "HIGH"
            action = f"Urgent attention needed. {', '.join(depletion_warning)}" if depletion_warning else "Urgent attention needed."
        elif severity > 30:
            priority = "MODERATE"
            action = "Monitor closely"
        else:
            priority = "LOW"
            action = "Regular monitoring"
            
        recommendations.append({
            "region": region_name,
            "priority": priority,
            "action": action,
            "urgent_resources": urgent_resources,
            "severity": severity
        })
    
    return sorted(recommendations, key=lambda x: x['severity'], reverse=True)

def create_resource_chart(df):
    """Create resource comparison chart"""
    resource_data = []
    
    for _, row in df.iterrows():
        stocks = row['warehouse_stock_status']
        needs = row['resource_needs']
        
        for resource in stocks.keys():
            resource_data.append({
                'Region': row['region_name'],
                'Resource': resource.capitalize(),
                'Type': 'Available',
                'Value': stocks[resource]
            })
            resource_data.append({
                'Region': row['region_name'],
                'Resource': resource.capitalize(),
                'Type': 'Needed',
                'Value': needs[resource]
            })
    
    resource_df = pd.DataFrame(resource_data)
    
    fig = px.bar(resource_df,
                 x='Region',
                 y='Value',
                 color='Type',
                 pattern_shape='Resource',
                 barmode='group',
                 title='Resource Availability vs Needs',
                 labels={'Value': 'Units'},
                 color_discrete_map={'Available': 'rgb(99, 110, 250)', 'Needed': 'rgb(239, 85, 59)'})
    
    return fig

def main():
    st.set_page_config(layout="wide", page_title="Real-time Resource Allocation Dashboard")
    
    st.title("🌐 Real-time Disaster Resource Management Dashboard")
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # Load new data
            df = load_data()
            
            # Top metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Regions Monitored", len(df))
            with col2:
                current_severity = df['severity_score'].mean()
                if st.session_state.previous_data is not None:
                    previous_severity = st.session_state.previous_data['severity_score'].mean()
                    delta = current_severity - previous_severity
                else:
                    delta = None
                st.metric("Average Severity", f"{current_severity:.1f}", delta=f"{delta:.1f}" if delta else None)
            with col3:
                blocked_roads = df['road_block_status'].sum()
                st.metric("Blocked Roads", blocked_roads)
            with col4:
                total_population = df['population_density'].sum()
                st.metric("Total Population", f"{total_population:,}")

            # Create two columns for main visualizations
            col_left, col_right = st.columns([2, 1])

            with col_left:
                # Severity Map
                fig_severity = px.bar(df, 
                                    x='region_name',
                                    y='severity_score',
                                    color='severity_score',
                                    color_continuous_scale='RdYlGn_r',
                                    title='Regional Severity Scores')
                st.plotly_chart(fig_severity, use_container_width=True)

                # Resource Status
                fig_resources = create_resource_chart(df)
                st.plotly_chart(fig_resources, use_container_width=True)

            with col_right:
                # Critical Recommendations
                st.subheader("📊 Situation Analysis")
                recommendations = calculate_resource_recommendations(df)
                
                for rec in recommendations:
                    color = {
                        "CRITICAL": "red",
                        "HIGH": "orange",
                        "MODERATE": "blue",
                        "LOW": "green"
                    }[rec["priority"]]
                    
                    st.markdown(f"""
                    <div style='padding: 10px; border-left: 5px solid {color}; margin-bottom: 10px;'>
                        <h4 style='color: {color};'>{rec['region']}</h4>
                        <p><strong>Priority:</strong> {rec['priority']}</p>
                        <p><strong>Action:</strong> {rec['action']}</p>
                        <p><strong>Urgent Resources:</strong> {', '.join(rec['urgent_resources']) if rec['urgent_resources'] else 'None'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Add timestamp
                st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Update previous data
            st.session_state.previous_data = df
            time.sleep(3)  # Update every 3 seconds

if __name__ == "__main__":
    main()
