import pytest
import os
from app.services.file_processing.csv_processor import parse_csv_generic, _normalize_header, _infer_type

@pytest.fixture
def temp_csv_file(tmp_path):
    csv_content = "head_er1,  header2  ,header3\nval1,123,true\nval2,45.6,false\n\"val,3\",,"
    file_path = tmp_path / "test.csv"
    file_path.write_text(csv_content)
    return str(file_path)

@pytest.fixture
def empty_csv_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")
    return str(file_path)

def test_parse_csv_generic_success(temp_csv_file):
    result = parse_csv_generic(temp_csv_file)
    assert result["success"]
    assert result["count"] == 3
    assert len(result["data"]) == 3
    assert result["data"][0] == {"head_er1": "val1", "header2": 123, "header3": True}
    assert result["data"][1] == {"head_er1": "val2", "header2": 45.6, "header3": False}
    assert result["data"][2] == {"head_er1": "val,3", "header2": "", "header3": ""}

def test_parse_csv_file_not_found():
    result = parse_csv_generic("non_existent_file.csv")
    assert not result["success"]
    assert "File not found" in result["error"]
    assert result["data"] == []

def test_parse_csv_empty_file(empty_csv_file):
    result = parse_csv_generic(empty_csv_file)
    assert result["success"]
    assert result["count"] == 0
    assert result["data"] == []

def test_normalize_header():
    assert _normalize_header("  Header Name  ") == "Header Name"
    assert _normalize_header("Header Name", make_identifier=True) == "Header_Name"
    assert _normalize_header(None) == ""

def test_infer_type():
    assert _infer_type("123") == 123
    assert _infer_type("  45.6  ") == 45.6
    assert _infer_type("true") is True
    assert _infer_type("False") is False
    assert _infer_type("  some string  ") == "some string"
    assert _infer_type(None) == ""
    assert _infer_type("") == ""
    assert _infer_type("1,234.56") == 1234.56
