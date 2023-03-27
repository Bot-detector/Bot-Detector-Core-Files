import os
import sys
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import token
from api.routers import hiscore
from src.utils import logging_helpers

request_path = f"/v1/hiscore/Latest"
request_params = {"player_id": 1, "token": token}


def test_build_route_log_string(test_client):
    """
    Tests if verify_token within legacy.get_discord_linked_accounts
    gets called with the proper log string passed into it.
    """

    with patch.object(hiscore, "verify_token", return_value=None) as mock:
        test_client.get(request_path, params=request_params)

        expected_log_str = (
            "[GET] Path: /discord/get_linked_accounts/***/1 Query Params: "
        )

        mock.assert_called_once_with(
            token, verification="verify_players", route=expected_log_str
        )


def test_censor_log_entry():
    """
    Tests if censor_log_entry replaces the specified substrings with '***'
    """

    censored_str = logging_helpers.censor_log_entry(request_path, ["Latest", "hiscore"])

    expected_str = "/v1/***/***"

    assert "hiscore" not in censored_str
    assert "Latest" not in censored_str

    assert censored_str == expected_str
