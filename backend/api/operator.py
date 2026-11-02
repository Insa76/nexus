from fastapi import APIRouter

from core.operator_agent import (
    OperatorAgent
)

router = APIRouter(
    prefix="/operator"
)

agent = OperatorAgent()


@router.post("/run")
async def run_operator(
    data: dict
):

    goal = data.get(
        "goal",
        ""
    )

    result = await agent.execute_goal(
        goal
    )

    return result