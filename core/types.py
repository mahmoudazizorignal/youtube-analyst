from crewai.crews.crew_output import CrewOutput
from crewai.types.streaming import CrewStreamingOutput
from typing import TypedDict, Union, Literal, List

class JobSubmissionInfo(TypedDict):
    snapshot_id: str
    
JobSubmissionResult = Union[JobSubmissionInfo, None]

class JobProgressInfo(TypedDict):
    status: Literal["ready", "failed", "running"]
    snapshot_id: str
    dataset_id: str

JobProgressResult = Union[JobProgressInfo, None]

class SigleTranscript(TypedDict):
    start_time: float
    end_time: float
    duration: float
    text: str

class VideoInfo(TypedDict):
    url: str
    shortcode: str
    formatted_transcript: List[SigleTranscript]

VideoPath = str

VideosInfo = List[VideoInfo]
VideosPath = List[VideoPath]

class JobResult(TypedDict):
    videos_info: VideosInfo
    videos_path: VideosPath

JobResultOrNone = Union[JobResult, None]

CrewResponse = Union[CrewOutput, CrewStreamingOutput]
