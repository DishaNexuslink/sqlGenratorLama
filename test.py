import json

with open(r"data\datajson", "r") as f:
    schema = json.load(f)


if schema:
    print("ok")