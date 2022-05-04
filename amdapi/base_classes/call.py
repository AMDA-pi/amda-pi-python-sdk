""" This file contains classes that are fundamental to creating a Call object."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from datetime import datetime
import requests


@dataclass(frozen=True)
class Segment:
    """A Segment is a section of the dialogue."""

    is_agent: bool
    start_time: float
    end_time: float
    transcript: str
    pace: float
    emotions: List[Tuple[str, float]]

    @classmethod
    def parse_segment(cls, segment: Dict[str:Any]):
        segment["is_agent"] = segment.pop("speaker").lower().strip() == "agent"
        segment["start_time"] = segment.pop("from")
        segment["end_time"] = segment.pop("to")
        segment["emotions"] = [
            (emotion["name"].lower(), emotion["score"])
            for emotion in segment["emotions"]
        ]
        return cls(**segment)

    def __repr__(self) -> str:
        return f"< amdapi.Segment | is_agent: {self.is_agent} \t| start_time: {self.start_time:08.2f} | end_time: {self.end_time:08.2f} >"


# @dataclass(frozen=True)
@dataclass
class Call:
    """A Call object contains information about a call that exists on the AMDAPi Backend."""

    uuid: str
    call_id: str
    client_id: str
    agent_id: str
    customer_id: str
    init_time: datetime
    is_analyzed: bool
    call_info: Dict[Any]
    origin: str
    language: str

    # Optional - When Analysed
    audio_duration: float = field(
        init=False,
    )
    total_speakers: int = field(init=False)
    summary: str = field(init=False)
    customer_satisfaction_score: float = field(init=False)
    speakers_stats: Dict[str, Dict[str, Any]] = field(init=False)
    is_critical: bool = field(init=False)
    critical_scores: Dict[str, bool] = field(init=False)
    segments: List[Segment] = field(init=False)

    def __post_init__(self):
        if isinstance(self.call_info, Dict):
            self.is_analyzed = True
            self.audio_duration = self.call_info["audio_duration"]
            self.total_speakers = self.call_info["total_speakers"]
            self.summary = self.call_info["summary"]
            self.customer_satisfaction_score = self.call_info[
                "customer_satisfaction_score"
            ]
            self.speakers_stats = self.call_info["speakers_stats"]
            self.is_critical = self.call_info["critical_stats"]["is_critical"]
            self.critical_scores = self.call_info["critical_stats"]["critical_scores"]
            self.segments = [
                Segment.parse_segment(segment) for segment in self.call_info["segments"]
            ]
            self.full_transcription = self.call_info["full_transcription"]
        delattr(self, "call_info")

    @classmethod
    def parse_call(cls, response: requests.models.Response | Dict[str, Any]) -> "Call":
        if isinstance(response, requests.models.Response):
            data = response.json()["data"]
        else:
            data = response

        call_data = {
            "uuid": data.get("call_uuid", None),
            "call_id": data.get("call_id", None),
            "client_id": data.get("client_id", None),
            "agent_id": data.get("agent_id", None),
            "customer_id": data.get("customer_id", None),
            "origin": data.get("origin", None),
            "language": data.get("language", None),
            "call_info": data.get("call_info", []),
            "init_time": datetime.now(),
            "is_analyzed": False,
        }

        return cls(**call_data)

    def __repr__(self) -> str:
        return f"< amdapi.Call | UUID: {self.uuid} | Analyzed: {self.is_analyzed} >"
