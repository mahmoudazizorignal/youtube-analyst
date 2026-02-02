import os
import json
import subprocess
from typing import List
from logging import Logger
from helpers.config import Settings
from core.types import (JobSubmissionResult, JobSubmissionInfo,
                        JobProgressResult, VideosResult, 
                        VideosInfo, VideoInfo, SigleTranscript)

class YouTubeScrapper:
    
    def __init__(self, settings: Settings, logger: Logger):
        self.settings = settings
        self.logger = logger
    
    async def submit_job(
        self,
        queries: List[str], 
        start_date: str, 
        end_date: str,
    ) -> JobSubmissionResult:
        
        api_key = self.settings.BRIGHT_DATA_API_KEY
        num_of_posts = self.settings.BRIGHT_DATA_API_POSTS_COUNT
        order_by = self.settings.BRIGHT_DATA_API_ORDER_BY
        country = self.settings.BRIGHT_DATA_API_COUNTRY_CODE
        endpoint = self.settings.BRIGHT_DATA_API_ENDPOINT
        
        payload = [
            {
                "url": query,
                "num_of_posts": num_of_posts,
                "start_date": start_date,
                "end_date": end_date,
                "order_by": order_by,
                "country": country
            }
            for query in queries
        ]
        
        command = [
            "curl",
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),  # Convert payload to JSON string
            endpoint
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            self.logger.error(f"Error: {result.stderr}")
            return None
        
        try:
            return json.loads(result.stdout.strip())
        
        except json.JSONDecodeError:
            self.logger.error("Failed to parse JSON response.")
            return None

    async def get_job_progress(self, snapshot: JobSubmissionInfo) -> JobProgressResult:
        api_key = self.settings.BRIGHT_DATA_API_KEY
        snapshot_id = snapshot["snapshot_id"]
        
        command = [
            "curl",
            "-H", f"Authorization: Bearer {api_key}",
            f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            result = json.loads(result.stdout.strip())
            
            return {
                "status": result["status"],
                "snapshot_id": result["snapshot_id"],
                "dataset_id": result["dataset_id"],
            }
            
        else:
            self.logger.error(f"Error: {result.stderr}")
            return None

    async def get_job_result(self, snapshot: JobSubmissionInfo) -> VideosResult:
        api_key = self.settings.BRIGHT_DATA_API_KEY
        output_format = self.settings.BRIGHT_DATA_API_OUTPUT_FORMAT
        snapshot_id = snapshot["snapshot_id"]
        
        command = [
            "curl",
            "-H", f"Authorization: Bearer {api_key}",
            f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={output_format}"
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Error: {result.stderr}")
            return None
        
        contents = json.loads(result.stdout.strip())
        videos_info: VideosInfo = []
        
        for content in contents:
            
            if "url" not in content:
                continue
            
            video_transcript: List[SigleTranscript] = content["formatted_transcript"]
            
            video_info = VideoInfo(
                url=content["url"],
                shortcode=content["shortcode"],
                formatted_transcript=video_transcript,
            )
            
            videos_info.append(video_info)
        
        return videos_info
