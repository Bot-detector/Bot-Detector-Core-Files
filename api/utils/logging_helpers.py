from fastapi import Request
from typing import List
from functools import reduce


def build_route_log_string(request: Request, censored_strings: List[str]) -> str:
  log_str = f"[{request.method}] Path: {request.url.path} Query Params: {request.query_params}"

  return log_str if not censored_strings else censor_log_entry(log_str, censored_strings)


def censor_log_entry(log_str: str, censored_strings: List[str]) -> str:

  [log_str := log_str.replace(censored, "***") for censored in censored_strings]

  return log_str
