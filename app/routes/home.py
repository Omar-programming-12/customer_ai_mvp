from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def home():

    return {
        "message": "Customer AI MVP is running!"
    }
