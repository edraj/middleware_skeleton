## Fastapi middleware/backend component

- Leverages DMART as the backend data store.
- Access to DMART api is made with privileged user defined on the backend component
- Declares own initial set of apis to register/create user and login/logout with forgot/reset password


## Installation
- clone the repo
- cd to the project folder
- `pip install -r requirements.txt`
- run the seeders using `cd db && python seeder.py`
This step will create a new folder as a sibling to the project folder called `spaces` that holds the data
- [Called form Dmart service] configure Dmart server to deal with the new `spaces` folder by updating `SPACES_FOLDER` env var in Dmart itself
- [Called form Dmart service] recreate Redis DB by calling `./create_index.py --flushall`
- [Called form Dmart service] [Optional] run Dmart tests to make sure everything configured successfully `cd tests && pytest`
- create the logs folder `mkdir ../logs`
- run the server `./main.py`