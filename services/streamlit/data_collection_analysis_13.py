import streamlit as st

class DataCollectionAnalysisService:
    @staticmethod
    def show_insights():
        """Display insights from data collection analysis."""
        st.markdown("## Data Collection Analysis Insights")

        # Key Metrics
        num_categories = 5
        num_insights = 15
        st.metric("Categories Analyzed", num_categories)
        st.metric("Total Insights Generated", num_insights)

        # Main Insights
        categories = [
            "Customer Behavior", "Operational Efficiency", 
            "Market Intelligence", "Service Quality", "Strategic Implications"
        ]
        insights = {
            "Customer Behavior": [
                "Demographics collection for personalized marketing",
                "Trip purpose and payment method analysis",
                "App usage and cancellation history monitoring"
            ],
            "Operational Efficiency": [
                "Pickup wait times and trip duration tracking",
                "Peak hour demand and driver availability analysis",
                "Route optimization data gathering"
            ],
            "Market Intelligence": [
                "Competitor pricing analysis",
                "Local events calendar incorporation",
                "Traffic pattern data collection"
            ],
            "Service Quality": [
                "Detailed feedback collection",
                "Performance metrics for driver training",
                "Issue tracking for service reliability"
            ],
            "Strategic Implications": [
                "Comprehensive view of customer behavior and operations",
                "Data-driven targeted improvements",
                "Enhanced insights for market competitiveness"
            ]
        }

        for category in categories:
            with st.expander(f"### {category}"):
                for insight in insights[category]:
                    st.markdown(f"- {insight}")

        # Story
        st.markdown("### Data Collection Strategy Narrative")
        st.markdown(f"""
        My analysis reveals {num_insights} key insights across {num_categories} critical areas 
        of our business. By implementing these data collection strategies, we can:

        1. Personalize our marketing and enhance our service offerings based on customer behavior.
        2. Optimize our operations, from driver allocation to route planning.
        3. Stay competitive by analyzing market trends and anticipating demand.
        4. Continuously improve our service quality through targeted training and issue tracking.
        5. Make data-driven strategic decisions to drive growth and maintain our competitive edge.

        This comprehensive approach to data collection and analysis will provide us with a 
        360-degree view of our business, enabling us to make informed decisions and stay ahead 
        in the dynamic mobility market.
        """)