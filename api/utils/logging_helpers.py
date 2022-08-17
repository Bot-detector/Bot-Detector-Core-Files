from fastapi import Request

def build_route_log_string(request: Request) -> str:
  return f"[{request.method}] Path: {request.url.path} Query Params: {request.query_params}"