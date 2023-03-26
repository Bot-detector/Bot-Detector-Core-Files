from fastapi import Request
from typing import List


def build_route_log_string(request: Request, censored_strings: List[str] = []) -> str:
    """
    Creates a string for logging purposes that contains information about how a route was accessed.

    Parameters
    ----------
    request : Request
        A Starlette Request object containing information about the HTTP request received.

    censored_strings : List[str] (Optional)
        A list of substrings that will be replaced with '***' in the log string.

    Returns
    ----------
        A string containing information about the request.

    Example:
        "[POST] Path: /1.3.2/site/discord_user/*** Query Params: test=true"
    """
    log_str = f"[{request.method}] Path: {request.url.path} Query Params: {request.query_params}"

    return (
        log_str if not censored_strings else censor_log_entry(log_str, censored_strings)
    )


def censor_log_entry(log_str: str, censored_strings: List[str]) -> str:
    """
    Replaces instances of the substrings contained within
        censored__strings located within log_str with '***'

    Parameters
    ----------
    log_str : str
        The string to be logged prior to censorship.

    censored_strings : List[str] (Optional)
        A list of substrings that will be replaced with '***' in the log string.

    Returns
    ----------
        A log string with any censored substrings replaced with ***.

    Example:
        Params:
            log_str: "[GET] /some/route/1234abcd/players"
            censored_strings: ["1234abcd"]

        Returns:
            "[GET] /some/route/***/players"
    """

    [log_str := log_str.replace(censored, "***") for censored in censored_strings]

    return log_str
