from fastapi import FastAPI

router = FastAPI(
    tags=["order"]
)

@router.post(
    '/order'
)
async def create_new_order(

):
    pass