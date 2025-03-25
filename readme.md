## Fastapi middleware/backend component

- Leverages DMART as the backend data store.
- Access to DMART api is made with privileged user defined on the backend component
- Declares own initial set of apis to register/create user and login/logout with forgot/reset password


## Setup
- clone the repo
- cd to the project folder
- `pip install -r requirements.txt`
- create the logs folder `mkdir ../logs`
- run the server `./main.py`
- _Optional:_ After seeding you can run Dmart tests (Dmart side) to make sure everything configured successfully 
- - Locally: `./curl.sh` and/or `cd tests && pytest` 
- - Podman: `podman exec -it -w /home/dmart/backend dmart ./curl.sh`

# Seeding

## Running from local

- Point dmart service to the project spaces by updating the `SPACES_FOLDER` in `config.env`.
- Run `json_to_db` script to seed the database with the json files in the project spaces.
- Note: revert the `SPACES_FOLDER` to the original value after seeding.

## Running from podman
- Using podman copy command:
- - `podman cp [options] [container:]src_path [container:]dest_path`
- - `podman cp spaces dmart:/home/dmart/sample/`
- `podman exec -it -w /home/dmart/backend dmart /home/venv/bin/python3 ./migrate.py json_to_db`
- Run `json_to_db` script to seed the database with the json files in the project spaces.
- Note: You can safely ignore the error messages that are related to duplicated entries.