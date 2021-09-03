from pathlib import Path
from typing import Dict, Text
import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError

import rasa.shared.utils.io
import rasa.utils.io as io_utils


@pytest.mark.parametrize("actual_path", ["", "file.json", "file"])
def test_file_path_validator_with_invalid_paths(actual_path):
    test_error_message = actual_path

    validator = io_utils.file_type_validator([".yml"], test_error_message)

    document = Document(actual_path)
    with pytest.raises(ValidationError) as e:
        validator.validate(document)

    assert e.value.message == test_error_message


@pytest.mark.parametrize("actual_path", ["domain.yml", "lala.yaml"])
def test_file_path_validator_with_valid_paths(actual_path):
    validator = io_utils.file_type_validator([".yml", ".yaml"], "error message")

    document = Document(actual_path)
    # If the path is valid there shouldn't be an exception
    assert validator.validate(document) is None


@pytest.mark.parametrize("user_input", ["", "   ", "\t", "\n"])
def test_non_empty_text_validator_with_empty_input(user_input):
    test_error_message = "enter something"

    validator = io_utils.not_empty_validator(test_error_message)

    document = Document(user_input)
    with pytest.raises(ValidationError) as e:
        validator.validate(document)

    assert e.value.message == test_error_message


@pytest.mark.parametrize("user_input", ["utter_greet", "greet", "Hi there!"])
def test_non_empty_text_validator_with_valid_input(user_input):
    validator = io_utils.not_empty_validator("error message")

    document = Document(user_input)
    # If there is input there shouldn't be an exception
    assert validator.validate(document) is None


def test_create_validator_from_callable():
    def is_valid(user_input) -> None:
        return user_input == "this passes"

    error_message = "try again"

    validator = io_utils.create_validator(is_valid, error_message)

    document = Document("this passes")
    assert validator.validate(document) is None

    document = Document("this doesn't")
    with pytest.raises(ValidationError) as e:
        validator.validate(document)

    assert e.value.message == error_message


@pytest.mark.parametrize(
    "input,kwargs,expected",
    [({(1, 2): 3}, {}, {repr((1, 2)): 3}), ({(1, 2): 3}, {"keys": True}, {(1, 2): 3}),],
)
def test_write_and_load_dict_via_jsonpickle(
    tmp_path: Path, input: Dict, kwargs: Dict[Text, bool], expected: Dict
):
    file_name = tmp_path / "bla.pkl"
    rasa.utils.io.json_pickle(file_name=file_name, obj=input, **kwargs)
    loaded = rasa.utils.io.json_unpickle(file_name=file_name, **kwargs)
    assert loaded == expected
