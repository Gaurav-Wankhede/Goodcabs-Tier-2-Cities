import streamlit as st
from streamlit_option_menu import option_menu
from services.streamlit.city_performance_1 import CityPerformanceService
from services.streamlit.rating_analysis_3 import RatingAnalysisService
from services.streamlit.repeat_passenger_analysis_6 import RepeatPassengerAnalysisService
from services.streamlit.rpr_analysis_8 import RPRAnalysisService
from services.streamlit.demand_analysis_4 import DemandAnalysisService
from services.streamlit.fare_analysis_2 import FareAnalysisService
from services.streamlit.daytype_analysis_5 import DayTypeAnalysisService
from services.streamlit.target_analysis_7 import TargetAnalysisService
from services.streamlit.tourism_business_analysis_10 import TourismBusinessAnalysisService
from services.streamlit.data_collection_analysis_13 import DataCollectionAnalysisService
from services.streamlit.rpr_factors_analysis_9 import RPRFactorsAnalysisService
from services.streamlit.mobility_trends_analysis_11 import MobilityTrendsAnalysisService
from services.streamlit.partnership_analysis_12 import PartnershipAnalysisService
from config.__init__ import DataPaths
import base64

st.set_page_config(page_title="🚖 Goodcabs Tier-2 Cities", page_icon="🚖", layout="wide")

st.markdown(
    """
    <style>
    .main .block-container{{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    .stButton>button{{
        color: black;
        background-color: #FFD700;
        border-color: #FFD700;
    }}
    .stTabs [data-baseweb="tab"]{{
        color: #FFD700;
    }}
    .stTabs [data-baseweb="tab"]:hover{{
        color: #FFD700;
        background-color: #333333;
    }}
    .stTabs [data-baseweb="tab"]:focus{{
        color: #FFD700;
        background-color: #333333;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title('🚖 Goodcabs Tier-2 Cities Performance Dashboard')

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'City Performance'
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Charts'

selected2 = option_menu(None, ["Charts", "Dataframes", "Insights"], 
    icons=["bar-chart", "table", "lightbulb", "🎯"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if selected2:
    st.session_state.view_mode = selected2

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Main Categories")
    main_categories = {
        "City Performance": "🏙️",
        "Demand Analysis": "📈",
        "Passenger Analysis": "👥",
        "Target Achievement": "📊",
        "Additional Insights": "💡"
    }
    
    for category, icon in main_categories.items():
        if st.button(f"{icon} {category}", key=category, use_container_width=True):
            st.session_state.current_page = category
    
    st.markdown("""
        <style>
        .social-badges {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 20%;
        }
        .social-badges a {
            text-decoration: none;
            margin: 5px;
            flex: 1 1 30%;
        }
        .badge {
            display: block;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            color: white;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }
        .linkedin {background-color: #0077B5;}
        .github {background-color: #100000;}
        .portfolio {background-color: #FF5722;}
        @media (max-width: 600px) {
            .social-badges {
                flex-direction: column;
            }
            .social-badges a {
                flex: 1 1 100%;
                margin: 5px 0;
            }
        }
        </style>
        <div class="social-badges">
            <a href="https://www.linkedin.com/in/wankhede-gaurav/"><span class="badge linkedin">LinkedIn</span></a>
            <a href="https://github.com/Gaurav-Wankhede"><span class="badge github">GitHub</span></a>
            <a href="https://gaurav-wankhede.vercel.app/"><span class="badge portfolio">Portfolio</span></a>
        </div>
    """, unsafe_allow_html=True)
    

with col2:
    if st.session_state.current_page == 'City Performance':
        st.markdown("## 🏙️ City Performance")
        tab1, tab2, tab3 = st.tabs([
            "Top and Bottom Performing Cities", 
            "Average Fare per Trip by City", 
            "Average Ratings by City and Passenger Type"
        ])
        with tab1:
            city_metrics, summary_stats = CityPerformanceService.analyze_city_performance()
            if st.session_state.view_mode == 'Charts':
                CityPerformanceService.show_charts(city_metrics)
            elif st.session_state.view_mode == 'Dataframes':
                CityPerformanceService.show_dataframes(city_metrics)
            elif st.session_state.view_mode == 'Insights':
                CityPerformanceService.show_insights(city_metrics)
        with tab2:
            if st.session_state.view_mode == 'Charts':
                FareAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                FareAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                FareAnalysisService.show_insights()
        with tab3:
            if st.session_state.view_mode == 'Charts':
                RatingAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                RatingAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                RatingAnalysisService.show_insights()

    elif st.session_state.current_page == 'Demand Analysis':
        st.markdown("## 📈 Demand Analysis")
        tab1, tab2 = st.tabs([
            "Peak and Low Demand Months by City", 
            "Weekend vs. Weekday Trip Demand by City"
        ])
        with tab1:
            monthly_trips, results_df = DemandAnalysisService.analyze_demand()
            if st.session_state.view_mode == 'Charts':
                DemandAnalysisService.show_charts(monthly_trips)
            elif st.session_state.view_mode == 'Dataframes':
                DemandAnalysisService.show_dataframes(results_df)
            elif st.session_state.view_mode == 'Insights':
                DemandAnalysisService.show_insights(results_df)
        with tab2:
            day_type_pivot = DayTypeAnalysisService.analyze_day_types()
            if st.session_state.view_mode == 'Charts':
                DayTypeAnalysisService.show_charts(day_type_pivot)
            elif st.session_state.view_mode == 'Dataframes':
                DayTypeAnalysisService.show_dataframes(day_type_pivot)
            elif st.session_state.view_mode == 'Insights':
                DayTypeAnalysisService.show_insights(day_type_pivot)

    elif st.session_state.current_page == 'Passenger Analysis':
        st.markdown("## 👥 Passenger Analysis")
        tab1, tab2 = st.tabs([
            "Repeat Passenger Frequency and City Contribution Analysis", 
            "Highest and Lowest RPR by City and Month"
        ])
        with tab1:
            trip_freq_pct, high_freq_analysis = RepeatPassengerAnalysisService.analyze_repeat_passengers()
            if st.session_state.view_mode == 'Charts':
                RepeatPassengerAnalysisService.show_charts(trip_freq_pct, high_freq_analysis)
            elif st.session_state.view_mode == 'Dataframes':
                RepeatPassengerAnalysisService.show_dataframes(trip_freq_pct, high_freq_analysis)
            elif st.session_state.view_mode == 'Insights':
                RepeatPassengerAnalysisService.show_insights(high_freq_analysis)
        with tab2:
            if st.session_state.view_mode == 'Charts':
                RPRAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                RPRAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                RPRAnalysisService.show_insights()

    elif st.session_state.current_page == 'Target Achievement':
        st.markdown("## 📊 Target Achievement")
        if st.session_state.view_mode == 'Charts':
            TargetAnalysisService.show_charts()
        elif st.session_state.view_mode == 'Dataframes':
            TargetAnalysisService.show_dataframes()
        elif st.session_state.view_mode == 'Insights':
            TargetAnalysisService.show_insights()

    elif st.session_state.current_page == 'Additional Insights':
        st.markdown("## 💡 Additional Insights")
        tab1, tab2, tab3, tab4 = st.tabs([
            "Factors Influencing RPR",
            "Tourism vs. Business Demand Impact",
            "Emerging Mobility Trends",
            "Partnership Opportunities with Local Businesses"
        ])
        with tab1:
            if st.session_state.view_mode == 'Charts':
                RPRFactorsAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                RPRFactorsAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                RPRFactorsAnalysisService.show_insights()
        with tab2:
            if st.session_state.view_mode == 'Charts':
                TourismBusinessAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                TourismBusinessAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                TourismBusinessAnalysisService.show_insights()
        with tab3:
            if st.session_state.view_mode == 'Charts':
                MobilityTrendsAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                MobilityTrendsAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                MobilityTrendsAnalysisService.show_insights()
        with tab4:
            if st.session_state.view_mode == 'Charts':
                PartnershipAnalysisService.show_charts()
            elif st.session_state.view_mode == 'Dataframes':
                PartnershipAnalysisService.show_dataframes()
            elif st.session_state.view_mode == 'Insights':
                PartnershipAnalysisService.show_insights()
    elif st.session_state.current_page == 'Data Collection Suggestion':
            DataCollectionAnalysisService.show_insights()

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

background_image = get_base64_image(DataPaths.BACKGROUND_IMAGE)

st.markdown(
    f"""
    <style>
    .main .block-container {{
        padding-top: 2rem;
        max-width: 100%;
    }}
    [data-testid="stAppViewContainer"] {{
        background-image: url('data:image/png;base64,{background_image}');
        background-size: cover;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    .menu .container-xxl[data-v-5af006b8] {{
    background-color: 000000;
    border-radius: .5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)