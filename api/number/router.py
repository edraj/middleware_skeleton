from typing import Annotated
from fastapi import Query
from fastapi.routing import APIRouter
from api.number.requests.available_request import AvailableNumberRequest
from api.number.requests.number_request import NumberRequest
from api.number.service import available_numbers, generate_randomNumber, check
from api.schemas.response import ApiResponse
from models.enums import  Status
from api.user.Requests.user_update_request import UserUpdateRequest

numberRouter = APIRouter()


@numberRouter.get('/generate',summary="generate random number")
async def generate():
    generatedNumber = await generate_randomNumber()
    return ApiResponse(status=Status.success,data={"generatedNumber":generatedNumber})


@numberRouter.get('/available-numbers',summary="return list of available numbers ")
async def get_available_numbers(request: Annotated[str, Query(example="839432",description=" numbers list that include user favorite digits  "),] = None):

    availableNumberList = await available_numbers(request)
    return ApiResponse(status=Status.success,data={"availableNumbers":availableNumberList})


@numberRouter.get('/check',summary=" Check if the chosen number is available")
async def check_request(number: Annotated[str, Query(example="78756002479")]):
    return ApiResponse(status=Status.success,data={"numberAvailable":await check(number)})
