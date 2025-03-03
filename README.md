# Major League Hacking Hackathon - Best Team for Streamlit Innovation
# Project Title: Rapid-Relief-AI
Disaster Relief and Resource Management Using Generative AI

Project Description
This project will use generative AI to optimize and simulate resource allocation in real-time for disaster response scenarios, such as floods, wildfires, or earthquakes. The AI will provide a resource distribution plan for critical supplies (like food, water, and medical kits) based on inputs such as disaster severity, location density, and infrastructure status. A clear, actionable demo can show the AI’s potential to improve disaster response efficiency.

Core Idea
Leverage generative models to simulate and generate maps or routes for resource allocation, focusing on real-world factors like road access, population distribution, and time constraints. This tool could then help agencies make faster, more efficient decisions during critical situations.

Steps:
Keep all files in one location (main.py, data_generation.py, severity_calculation.py, resource_allocation.py, dashboard.py and gan_model.py)

1) Start MongoDB if it's not running

2) Train your GAN Model in one terminal:
python train_gan.py

3) Run your gan_generator.py in same terminal:
python gan_generator.py

4) Run the dashboard in another terminal:
streamlit run dashboard.py
