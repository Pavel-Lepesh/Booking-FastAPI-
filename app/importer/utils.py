import codecs
from fastapi import UploadFile, Response, status
from pydantic import BaseModel, ValidationError
from app.exceptions import TokenExpiredException
import csv
import json
from ast import literal_eval
from app.importer.schemas import SCHEMAS_VALIDATE
from app.exceptions import WrongDataForImport


def generate_csv():
    data = [
        {"name": "Some name 1", "location": "Dubai", "services": ["towels", "blankets"], "rooms_quantity": 24, "image_id": 7},
        {"name": "Some name 2", "location": "Dubai", "services": ["towels", "blankets"], "rooms_quantity": 24, "image_id": 8},
        {"name": "Some name 3", "location": "Dubai", "services": ["towels", "blankets"], "rooms_quantity": 24, "image_id": 9},
    ]
    columns = ["name", "location", "services", "rooms_quantity", "image_id"]

    with open("hotels.csv", "w", encoding="utf-8", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(data)


def parse_csv(table_name: str, file: UploadFile):
    validate_schema = SCHEMAS_VALIDATE[table_name]
    reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"), delimiter=";", quotechar='"')
    rows = []
    for row in reader:
        row: dict
        try:
            if table_name == "hotels":
                row["services"] = literal_eval(row["services"])
            model = validate_schema(**row)
            rows.append(model.model_dump())
        except (ValidationError, Exception):
            raise WrongDataForImport
    return rows
