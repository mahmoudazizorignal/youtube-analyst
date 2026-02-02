import os
import json
import asyncio
import subprocess
from logging import Logger
from typing import List, Coroutine, Any
from helpers.config import Settings
from core.types import (JobSubmissionResult, JobSubmissionInfo, JobResult,
                        JobProgressResult, JobResultOrNone, VideosPath,
                        VideoPath, VideosInfo, VideoInfo, SigleTranscript)

class YouTubeScrapper:
    
    def __init__(self, settings: Settings, logger: Logger):
        self.settings = settings
        self.logger = logger
        self.save_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "transcripts",
        )
        
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    async def _save_transcipt(self, video_info: VideoInfo) -> VideoPath:
        
        video_id = video_info["shortcode"]
        
        file_save_path = os.path.join(
            self.save_path,
            f"{video_id}.txt",
        )
        
        with open(file_save_path, "w") as f:
            transcript = video_info["formatted_transcript"]
            for single_transcript in transcript:
                text = single_transcript["text"]
                start_time = single_transcript["start_time"]
                end_time = single_transcript["end_time"]
                f.write(f"({start_time:.2f}-{end_time:.2f}): {text}\n")
                
        return file_save_path
    
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
            "-d", json.dumps(payload),
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

    async def get_job_result(
        self, 
        snapshot: JobSubmissionInfo
    ) -> JobResultOrNone:
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
        videos_path_operation: List[Coroutine[Any, Any, VideoPath]] = []
        
        for content in contents:
            
            if "url" not in content:
                continue
            
            video_transcript: List[SigleTranscript] = content["formatted_transcript"]
            
            video_info = VideoInfo(
                url=content["url"],
                shortcode=content["shortcode"],
                formatted_transcript=video_transcript,
            )
            
            videos_path_operation.append(self._save_transcipt(video_info=video_info))
            
            videos_info.append(video_info)

        videos_path: VideosPath = await asyncio.gather(*videos_path_operation)
        
        job_result = JobResult(
            videos_info=videos_info,
            videos_path=videos_path,
        )        
        
        return job_result
