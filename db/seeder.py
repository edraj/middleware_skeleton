#!/usr/bin/env python3

from datetime import datetime
from io import TextIOWrapper
import json
import os
import shutil
from typing import Any
from uuid import uuid4

"""Steps
    1- create ../../spaces folder
    2- copy management space from sample to ../../spaces/management
    3- create `acme` space
    4- create `schema` folder under `acme` space
    5- create `user`, schema under `schema` folder
    6- create `users` folders under `acme` space
"""


def create_json_entry_meta(
    path: str, shortname: str, schema_shortname: str, has_payload: bool = True
):
    entry_meta = open(path, "w")
    data: dict[str, Any] = {
        "uuid": str(uuid4()),
        "shortname": shortname,
        "is_active": True,
        "tags": [],
        "created_at": str(datetime.now()),
        "owner_shortname": "dmart",
    }
    if has_payload:
        data["payload"] = {
            "content_type": "json",
            "schema_shortname": schema_shortname,
            "body": f"{shortname}.json",
        }
    entry_meta.write(json.dumps(data))
    entry_meta.close()


def create_json_entry_payload(path: str, data_file_path: str) -> None:
    entry_meta = open(path, "w")

    data_file: TextIOWrapper = open(data_file_path, "r")
    data = json.dumps(json.load(data_file))
    data_file.close()

    entry_meta.write(data)

    entry_meta.close()


if __name__ == "__main__":
    # copy management space from sample to ../../spaces/management
    shutil.copytree("sample/management", "../../spaces/management")

    # create `acme` space
    os.makedirs("../../spaces/acme/.dm")
    space_meta = open("../../spaces/acme/.dm/meta.space.json", "w")
    space_meta.write(
        json.dumps(
            {
                "uuid": str(uuid4()),
                "shortname": "acme",
                "is_active": True,
                "created_at": str(datetime.now()),
                "owner_shortname": "dmart",
                "indexing_enabled": True,
                "capture_misses": True,
                "check_health": True,
                "active_plugins": ["action_log", "redis_db_update"],
            }
        )
    )
    space_meta.close()

    # create `schema` folder
    os.makedirs("../../spaces/acme/schema/.dm")
    create_json_entry_meta(
        path="../../spaces/acme/schema/.dm/meta.folder.json",
        shortname="schema",
        schema_shortname="folder_rendering",
    )
    create_json_entry_payload(
        path="../../spaces/acme/schema.json",
        data_file_path="sample/schema_folder.json",
    )

    # create `user` schema under schema folder
    os.makedirs("../../spaces/acme/schema/.dm/user")
    create_json_entry_meta(
        path="../../spaces/acme/schema/.dm/user/meta.schema.json",
        shortname="user",
        schema_shortname="meta_schema",
    )
    create_json_entry_payload(
        path="../../spaces/acme/schema/user.json",
        data_file_path="sample/user_schema.json",
    )

    # create `users` folder
    os.makedirs("../../spaces/acme/users/.dm")
    create_json_entry_meta(
        path="../../spaces/acme/users/.dm/meta.folder.json",
        shortname="users",
        schema_shortname="folder_rendering",
    )
    create_json_entry_payload(
        path="../../spaces/acme/users.json",
        data_file_path="sample/users_folder.json",
    )
