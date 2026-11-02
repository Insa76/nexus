from fastapi import APIRouter
from sync.models import Session, Memory
import uuid

router = APIRouter(prefix="/sync")


@router.post("/push")
def push(data: dict):

    db = Session()

    m = Memory(
        id=str(uuid.uuid4()),
        content=data["content"]
    )

    db.add(m)
    db.commit()

    return {"ok": True}


@router.get("/pull")
def pull():

    db = Session()

    rows = db.query(Memory).all()

    return {"items": [r.content for r in rows]}
