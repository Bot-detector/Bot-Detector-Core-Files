from fastapi import APIRouter, Query, status, Header, Request
from src.database.functions import verify_token
from src.utils import logging_helpers
from src.app.repositories.stg_report import stgReport as RepositorystgReport
from src.app.repositories.player import Player as RepositoryPlayer
from src.app.schemas.stg_report import StgReport as SchemaStgReport
from src.app.schemas.detection import detection
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Report"])


def get_unique_detections(data: list[detection]) -> list[detection]:
    unique_detections = {}
    for detection_item in data:
        key = (
            detection_item.reporter,
            detection_item.reported,
            detection_item.region_id,
        )
        if key not in unique_detections:
            unique_detections[key] = detection_item

    return list(unique_detections.values())


def normalize_username(username: str) -> str:
    return username.lower().replace("_", " ").replace("-", " ").strip()


@router.post(
    "/report",
    status_code=status.HTTP_201_CREATED,
)
async def insert_report(data: list[detection]):

    unique_data = get_unique_detections(data)

    unique_reporters = set(d.reporter for d in unique_data)
    unique_reporters_count = len(unique_reporters)

    if len(unique_reporters_count) != 1:
        logger.debug({"message": "Too many reporters"})
        return

    if len(unique_data) > 5000:
        logger.debug({"message": "Too many reports"})
        return

    # Normalize names & get list of unique player names
    unique_player_names = set()
    for detection_item in unique_data:
        # Normalize reporter and reported names
        detection_item.reporter = normalize_username(detection_item.reporter)
        detection_item.reported = normalize_username(detection_item.reported)

        # add unique_player name
        unique_player_names.add(detection_item.reporter)
        unique_player_names.add(detection_item.reported)

    repo_player = RepositoryPlayer()
    players = await repo_player.read_many(
        names=unique_player_names
    )  # list[SchemaPlayer]
    player_names = [player.name for player in players]

    players_to_create = []
    for name in unique_player_names:
        if name not in player_names:
            # If the player name doesn't exist in the list of players retrieved from the database,
            # create a new player object and add it to the players_to_create list.
            players_to_create.append(name)
