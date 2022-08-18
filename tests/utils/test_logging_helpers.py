import os
import sys
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.Config import token
from api.database.functions import verify_token
from api.routers import legacy


request_path = f"/discord/get_linked_accounts/{token}/1"


def test_build_route_log_string(test_client):
    """
    Tests if verify_token within legacy.get_discord_linked_accounts
    gets called with the proper log string passed into it.
    """

    with patch.object(legacy, 'verify_token', return_value=None) as mock:
        test_client.get(request_path)

        mock.assert_called_once_with(token, "verify_players", request_path.replace(token, "***"))


def censor_log_entry():
    ...
