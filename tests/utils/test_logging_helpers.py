import os
import sys
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.Config import token
from api.routers import legacy
from api.utils import logging_helpers


request_path = f"/discord/get_linked_accounts/{token}/1"


def test_build_route_log_string(test_client):
    """
    Tests if verify_token within legacy.get_discord_linked_accounts
    gets called with the proper log string passed into it.
    """

    with patch.object(legacy, 'verify_token', return_value=None) as mock:
        test_client.get(request_path)

        expected_log_str = '[GET] Path: /discord/get_linked_accounts/***/1 Query Params: '

        mock.assert_called_once_with(token, verification="verify_players", route=expected_log_str)


def test_censor_log_entry():
    """
    Tests if censor_log_entry replaces the specified substrings with '***'
    """

    censored_str = logging_helpers.censor_log_entry(request_path, [token, "discord"])

    expected_str = "/***/get_linked_accounts/***/1"

    assert token not in censored_str
    assert "discord" not in censored_str

    assert censored_str == expected_str
