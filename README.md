<div align="center">
    <h1>YouTube Trend Analysis with CrewAI and BrightData</h1>
</div>

![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-1.9.3%2B-brightgreen.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.53.1%2B-orange.svg)
![Ollama](https://img.shields.io/badge/Ollama-0.6.1%2B-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/mahmoudazizorignal/youtube-analyst.svg)

This project implements a YouTube Trend Analysis with CrewAI and BrightData.

- Bright Data is used to scrape YouTube videos.
- CrewAI is used to analyze the transcripts of the videos and generate a summary.
- Streamlit is used to create a web interface for the project.

## Setup and Installations

Paste `.env.example` to `.env` and fill in the required API keys.

```bash
cp .env.example .env
```

Get BrightData API Key:

- Go to [Bright Data](https://www.brightdata.com/) and sign up for an account.
- Once you have an account, go to the API Key page and copy your API key.
- Paste your API key into `.env` file as follows:

```
BRIGHTDATA_API_KEY=your_api_key_here
```

**Setup Ollama**

```bash
# setup ollama on linux
curl -fsSL https://ollama.com/install.sh | sh
# pull llama 3.2 model
ollama pull deepseek-r1:70b
```

**Install Dependencies:** Ensure you have Python 3.12 or later installed.

```bash
pip install uv
uv pip install -r requirements.txt
```

## Running the Application

To run the Streamlit application, use the following command:

```bash
streamlit run app.py
```
