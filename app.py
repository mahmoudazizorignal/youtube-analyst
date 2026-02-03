import os
import gc
import base64
import logging
import streamlit as st
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

from crewai import LLM
from core.crew import Crew
from helpers.config import get_settings
from core.scrapper import YouTubeScrapper
from utils.analyze import scrape_channels, kickoff_crew

settings = get_settings()
logger = logging.getLogger(__name__)

@st.cache_resource
def get_llm() -> LLM:
    
    llm = LLM(
        model=settings.OLLAMA_MODEL_ID,
        base_url=settings.OLLAMA_URL,
        format="json",
    )
    
    return llm

@st.cache_resource
def get_crew() -> Crew:

    crew = Crew(
        llm=get_llm(),
        verbose=True,
    )

    return crew

@st.cache_resource
def get_scrapper() -> YouTubeScrapper:

    scrapper = YouTubeScrapper(
        settings=settings,
        logger=logger,
    )

    return scrapper

st.markdown("""
    # YouTube Trend Analysis powered by <img src="data:image/png;base64,{}" width="120" style="vertical-align: -3px;"> & <img src="data:image/png;base64,{}" width="120" style="vertical-align: -3px;">
""".format(base64.b64encode(open("assets/crewai.png", "rb").read()).decode(), base64.b64encode(open("assets/brightdata.png", "rb").read()).decode()), unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat history

if "response" not in st.session_state:
    st.session_state.response = None

if "crew" not in st.session_state:
    st.session_state.crew = None      # Store the Crew object

def start_analysis():
    job_result = scrape_channels(
        scrapper=get_scrapper(),
        channels=st.session_state.youtube_channels,
        start_date=st.session_state.start_date,
        end_date=st.session_state.end_date,
        settings=settings,
    )

    if job_result:
        st.session_state.response = kickoff_crew(
            crew=get_crew(),
            job_result=job_result,
        )

with st.sidebar:
    st.header("YouTube Channels")
    
    if "youtube_channels" not in st.session_state:
        st.session_state.youtube_channels = [""]
    
    def add_channel_field():
        st.session_state.youtube_channels.append("")
    
    for i, channel in enumerate(st.session_state.youtube_channels):
        col1, col2 = st.columns([6, 1])

        with col1:
            st.session_state.youtube_channels[i] = st.text_input(
                "Channel URL",
                value=channel,
                key=f"channel_{i}",
                label_visibility="collapsed"
            )

        with col2:
            if i > 0:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.youtube_channels.pop(i)
                    st.rerun()
    
    st.button("Add Channel ➕", on_click=add_channel_field)
    st.divider()
        
    st.subheader("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
        st.session_state.start_date = start_date.strftime("%Y-%m-%d")

    with col2:
        end_date = st.date_input("End Date")
        st.session_state.end_date = end_date.strftime("%Y-%m-%d")

    st.divider()

    st.button("Start Analysis 🚀", type="primary", on_click=start_analysis)

# Main content area
if st.session_state.response:
    with st.spinner('Generating content... This may take a moment.'):
        try:
            result = st.session_state.response
            st.markdown("### Generated Analysis")
            st.markdown(result)
            
            # Add download button
            st.download_button(
                label="Download Content",
                data=result.raw,
                file_name=f"youtube_trend_analysis.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI, Bright Data and Streamlit")
