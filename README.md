# Goodcabs Performance Dashboard 🚖

## Overview

The **Goodcabs Performance Dashboard** is an advanced data analysis and visualization application designed to enhance operational excellence for Goodcabs in tier-2 cities across India. Initially, the project began with data analysis and prototyping using **Python Notebooks**, later evolving into a fully functional **Streamlit App** and a robust **FastAPI** backend. This dashboard delivers actionable insights into key performance metrics, helping improve trip volumes, passenger satisfaction, and market positioning.

### Features

1. **City Performance Analysis**:
   - Evaluate city-specific metrics and trends.
   - Identify top and bottom-performing cities.

2. **Demand Analysis**:
   - Analyze demand fluctuations across months and day types.
   - Compare weekday vs. weekend demand.

3. **Passenger Behavior Analysis**:
   - Understand passenger ratings and repeat behaviors.
   - Analyze city-wise repeat passenger frequency.

4. **Target Achievement**:
   - Track performance against monthly trip targets.
   - Categorize results as "Above Target" or "Below Target."

5. **Strategic Insights**:
   - Data-driven recommendations for operational improvements.
   - Emerging trends in mobility and partnership opportunities.

---

## Deployment

Live Application: [Goodcabs Performance Dashboard](https://goodcabs-tier-2-cities.onrender.com)

---

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Gaurav-Wankhede/Goodcabs-Tier-2-Cities-Performance-Dashboard.git
   cd Goodcabs-Tier-2-Cities-Performance-Dashboard
   ```

2. **Install Dependencies**:
   - Set up a virtual environment:
     ```bash
     python3 -m venv env
     source env/bin/activate  # Linux/MacOS
     ./env/Scripts/activate   # Windows
     ```
   - Install required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the Application**:
   - Start the **Streamlit App**:
     ```bash
     streamlit run streamlit_app.py
     ```
   - Start the **FastAPI** backend (if applicable):
     ```bash
     uvicorn main:app --reload
     ```

---

## Key Insights

- **Trip Efficiency**: City-wise fare and trip summaries.
- **Passenger Loyalty**: Analysis of repeat passenger frequency.
- **Revenue Trends**: Identify months with peak revenues by city.
- **Environmental Impact**: Evaluate the potential benefits of EV adoption.

---

## Technologies Used

- **Streamlit**: For creating an interactive and user-friendly dashboard.
- **FastAPI**: For building a high-performance backend.
- **Altair**: For data visualization.
- **Python**: Backend logic and analysis services.
- **Jupyter Notebooks**: For initial data analysis and prototyping.

---

## Contact

- **Developer**: [Gaurav Wankhede](https://www.linkedin.com/in/wankhede-gaurav/)
- **Portfolio**: [gaurav-wankhede.vercel.app](https://gaurav-wankhede.vercel.app)
- **GitHub**: [Gaurav-Wankhede](https://github.com/Gaurav-Wankhede)
