from api.schemas.response import ApiException,Error
from api.votes.votesDummy import votes


class VotesService:
 def get_vote_count(city_id):
    for item in votes.get("items", []):
        if item.get("cityId") == city_id:
            return item
    return []  
 def create_vote_count(city_id):
    for item in votes.get("items", []):
        if item.get("cityId") == city_id:
            vote=int(item["voteCount"])+1
            item["voteCount"]=vote
            return item
    return []
  

