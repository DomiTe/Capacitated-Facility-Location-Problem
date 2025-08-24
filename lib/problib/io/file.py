import json
from typing import Iterator

import yaml
from pydantic import BaseModel


def read_json(file_path: str) -> dict:
    """Reads a JSON file and returns its content as a Python object.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Union[Dict, List]: Parsed JSON data.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_jsonl(
    file_path: str, model_type: type[BaseModel] | None = None
) -> Iterator[BaseModel | dict]:
    """Generator for reading a JSON Lines file.
    Each line is parsed as a separate JSON object.
    If a Pydantic model type is provided, each line is validated against that model.
    If no model type is provided, the line is returned as a dictionary.

    Args:
        file_path (str): Path to the JSON Lines file.
        model_type (type[BaseModel] | None, optional): Pydantic model type to validate each line.. Defaults to None.

    Yields:
        Iterator[BaseModel | dict]: Parsed and validated Pydantic model or dict for each line.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if not model_type:
                yield json.loads(line.strip())
            else:
                yield model_type.model_validate_json(line.strip())


def write_json(
    file_path: str,
    data: dict | list,
    indent: int | None = 4,
) -> None:
    """Writes a Python object to a JSON file.

    Args:
        file_path (str): Path to the output JSON file.
        data (Union[Dict, List]): Data to write to the file.
        indent (Optional[int], optional): Indentation level for pretty printing. Defaults to 4.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=indent)


def write_jsonl(file_path: str, data: Iterator[BaseModel | dict]) -> None:
    """Writes Pydantic models or dictionaries to a JSON Lines file.
    Each item in the iterator is written as a separate line in the file.

    Args:
        file_path (str): Path to the output JSON Lines file.
        data (Iterator[BaseModel  |  dict]): Data to write to the file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        for item in data:
            if isinstance(item, BaseModel):
                file.write(item.model_dump_json() + "\n")
            else:
                file.write(json.dumps(item) + "\n")


def read_yaml(file_path: str) -> dict:
    """Reads a YAML file and returns its content as a Python object.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        Union[Dict, List]: Parsed YAML data.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def write_yaml(
    file_path: str,
    data: dict | list,
    indent: int | None = 4,
) -> None:
    """Writes a Python object to a YAML file.

    Args:
        file_path (str): Path to the output YAML file.
        data (Union[Dict, List]): Data to write to the file.
        indent (Optional[int], optional): Indentation level for pretty printing. Defaults to 4.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, indent=indent)
