import streamlit as st
from crewai import LLM
from helpers.config import get_settings

settings = get_settings()

@st.cache_resource
def get_llm():
    
    llm = LLM(
        model=settings.OLLAMA_MODEL_ID,
        api_key=settings.OLLAMA_URL,
    )
    
    return llm
