import time
import asyncio
import streamlit as st
from typing import List
from core.crew import Crew
from helpers.config import Settings
from core.models import JobProgressValues
from core.scrapper import YouTubeScrapper
from core.types import JobResultOrNone, JobResult

def scrape_channels(
    scrapper: YouTubeScrapper,
    channels: List[str],
    start_date: str,
    end_date: str,
    settings: Settings,
) -> JobResultOrNone:

    with st.spinner('Scraping videos... This may take a moment.'):
        status_container = st.empty()
        
        job_submission_info = asyncio.run(
            scrapper.submit_job(queries=channels, start_date=start_date, end_date=end_date)
        )

        if not job_submission_info:
            status_container.error(f"Scraping failed!")
            return

        job_progress_result = asyncio.run(
            scrapper.get_job_progress(job_submission_info=job_submission_info)
        )

        if not job_progress_result:
            status_container.error(f"Error while trying to track scrapping job!")
            return

        while job_progress_result['status'] != JobProgressValues.READY:

            status_container.info(f"Current status: {job_progress_result['status']}")
            time.sleep(10)

            job_progress_result = asyncio.run(
                scrapper.get_job_progress(job_submission_info=job_submission_info)
            )

            if not job_progress_result:
                status_container.error(f"Error while trying to track scrapping job!")
                return
            
            if job_progress_result['status'] == JobProgressValues.FAILED:
                status_container.error(f"Scraping failed!")
                return
        

        job_result = asyncio.run(
            scrapper.get_job_result(job_submission_info=job_submission_info)
        )

        if not job_result:
            status_container.error(f"Scraping failed!")
            return
        
        status_container.success("Scraping completed successfully!")
        
        st.markdown("## YouTube Videos Extracted")

        carousel_container = st.container()

        videos_per_row = settings.VIDEOS_PER_ROW

        with carousel_container:
            num_videos = len(job_result['videos_path'])
            num_rows = (num_videos + videos_per_row - 1) // videos_per_row

            for row in range(num_rows):
                cols = st.columns(videos_per_row)

                for col_idx in range(videos_per_row):
                    video_idx = row * videos_per_row + col_idx

                    if video_idx < num_videos:
                        with cols[col_idx]:
                            st.video(job_result['videos_info'][video_idx]['url'])

        status_container.success("Scraping complete! We shall now analyze the videos and report trends...")
    
    return job_result

def kickoff_crew(
    crew: Crew,
    job_result: JobResult,
):
    status_container = st.empty()
    with st.spinner('The agent is analyzing the videos... This may take a moment.'):
        response = crew.kickoff(file_paths=job_result['videos_path'])
    
    return response