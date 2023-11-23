from typing import Annotated
from fastapi import Query
from fastapi.routing import APIRouter
from api.schemas.response import ApiException, ApiResponse, Error
from models.enums import Status
from api.votes.votesDummy import votes
from api.votes.service import VotesService



router = APIRouter()


@router.post('',description="create vote")
async def create_vote(city_id:int):
    data=VotesService.create_vote_count(city_id=city_id)
    if len(data):
        return ApiResponse(status=Status.success,data={"data":data})
    return ApiException(status_code=404,error=Error(type='vote',message='city_id not exist',code=404))
        


@router.get('',summary="return list of votes for all cities or pass city_id for  specific  city ")
async def get_votes(city_id: Annotated[int, Query(example="1",description=" city id  "),] = None):
    if city_id:
        data=VotesService.get_vote_count(city_id)
        if len(data):
            return ApiResponse(status=Status.success,data={"items":data})
        else:return ApiException(status_code=404,error=Error(type='vote',message='city_id not exist',code=404))
    return ApiResponse(status=Status.success,data={"items":votes["items"]})