from fastapi import APIRouter


router = APIRouter(prefix="/profile", tags=["Profile endpoints"])


@router.get("/me")
async def get_profile():
    return {"message": "This is the profile endpoint"}

@router.patch("/me")
async def update_profile():
    return {"message": "This is the update profile endpoint"}


