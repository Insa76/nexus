from fastapi import APIRouter
from simulation.workflow_simulator import simulate_workflow

router = APIRouter()


@router.post("/simulate")

async def simulate(data:dict):

    name = data.get("workflow")

    result = simulate_workflow(name)

    return result