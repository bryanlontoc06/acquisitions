from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def sample():
    return {"message": "This is a sample endpoint"}
