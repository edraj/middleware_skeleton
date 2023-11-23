import random
from typing import Set
from api.number.dummy import availableNumberLIst, dummyNumberList


async def generate_randomNumber() -> int:
    randomNumber = random.randint(10**7, (10**8)-1)
    result = int(f"78{randomNumber}")
    return result


async def available_numbers(param: str = None) -> Set[str]:
    matching_numbers = []
    for obj in availableNumberLIst:
        if param and param in str(obj.values()):
            matching_numbers.append(obj)

    if len(matching_numbers):
        return matching_numbers
    return availableNumberLIst


async def check(number) -> bool:
    return number in dummyNumberList
