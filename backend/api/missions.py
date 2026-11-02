from fastapi import APIRouter

from core.mission_engine import (
    create_mission
)

router = APIRouter(
    prefix="/missions"
)


@router.post("/run")
async def run_mission(
    data: dict
):

    goal = data.get(
        "goal",
        ""
    )

    result = await create_mission(
        goal
    )

    return result