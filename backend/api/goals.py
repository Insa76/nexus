from fastapi import APIRouter
from goals.goals_manager import create_goal, list_goals

router = APIRouter()


@router.post("/goals/create")
async def create(data:dict):

    goal = data.get("goal")

    goal_id = create_goal(goal)

    return {"goal_id":goal_id}


@router.get("/goals")
async def goals():

    return list_goals()