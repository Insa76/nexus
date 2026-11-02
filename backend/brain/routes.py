from fastapi import APIRouter
from brain.patterns import analyze_patterns
from brain.suggester import generate_suggestion

router = APIRouter(prefix="/ai")

@router.get("/suggestions")
def suggestions():
    return analyze_patterns()

@router.post("/suggestions/generate")
def generate(data: dict):
    return generate_suggestion(data["pattern"])