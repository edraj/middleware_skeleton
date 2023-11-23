from pydantic import BaseModel,Field

class VoteCreateRequest(BaseModel):
    voteCount:int =Field(examples=[1,2,3])