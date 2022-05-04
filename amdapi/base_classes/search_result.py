"""This file contains class for parsing SearchResults retrieved from AMDAPI"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import requests

from .call import Call


@dataclass
class SearchResult:
    """A SearchResult object parsing search Results."""

    search_params: Dict
    current_page: int | None = None
    is_last_page: bool | None = None
    next_page: int | None = None
    previous_page: int | None = None
    call_list: List[Call] | None = None
    n_calls: int = 0

    def __post_init__(self):
        if self.call_list is None:
            self.call_list = []
        self.call_list = [Call.parse_call(call) for call in self.call_list]
        self.n_calls = len(self.call_list)

    @classmethod
    def parse_search_results(
        cls, response: requests.models.Response, search_params
    ) -> "SearchResult":
        data = response.json()["data"]
        if "calls" in data:
            data["call_list"] = data.pop("calls")
        if isinstance(data, list):
            data = {}
        return cls(**data, search_params=search_params)

    def __repr__(self) -> str:
        return f"< amdapi.SearchResult | current_page: {self.current_page} | is_last_page: {self.is_last_page} | n_calls {self.n_calls} >"
