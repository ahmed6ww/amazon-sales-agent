"""
CSV Processor Service

Responsibilities:
- Parse CSV files into a normalized list[dict]
- Provide consistent output shape: { success, data, count, error }

Notes:
- Default behavior trims whitespace in headers/values and infers simple types
- Safe for generic CSVs; specialized Helium10 parsing still exists in
  app.local_agents.research.helper_methods.parse_helium10_csv
"""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Dict, List, Optional


def _normalize_header(name: str, make_identifier: bool = False) -> str:
    if name is None:
        return ""
    n = name.strip()
    return (
        "_".join(n.split()) if make_identifier else n
    )


def _infer_type(value: str) -> Any:
    if value is None:
        return ""
    s = value.strip()
    if s == "":
        return ""

    # Booleans
    lower = s.lower()
    if lower in {"true", "false"}:
        return lower == "true"

    # Integers
    if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
        try:
            return int(s)
        except Exception:
            pass

    # Floats
    try:
        # handle numbers with commas e.g. 1,234.56
        if "," in s and any(ch.isdigit() for ch in s):
            maybe = s.replace(",", "")
            return float(maybe)
        return float(s)
    except Exception:
        pass

    return s


def parse_csv_generic(
    file_path: str,
    *,
    normalize_headers: bool = True,
    make_identifier_headers: bool = False,
    infer_types: bool = True,
    delimiter: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse a CSV file into a list of dictionaries.

    Returns a dict shaped like CSVParseResult from research.schemas:
    { success: bool, data: List[Dict[str, Any]], count: int, error?: str }
    """
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "data": [], "error": f"File not found: {file_path}"}

    try:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            # Detect dialect if not provided
            if delimiter is None:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except Exception:
                    dialect = csv.excel
            else:
                dialect = csv.excel
                dialect.delimiter = delimiter  # type: ignore[attr-defined]

            reader = csv.DictReader(f, dialect=dialect)

            # Normalize headers optionally
            if reader.fieldnames:
                fieldnames = [
                    _normalize_header(h, make_identifier_headers) if normalize_headers else (h or "")
                    for h in reader.fieldnames
                ]
            else:
                fieldnames = []

            rows: List[Dict[str, Any]] = []
            for raw in reader:
                cleaned: Dict[str, Any] = {}
                for idx, key in enumerate(reader.fieldnames or []):
                    norm_key = fieldnames[idx] if idx < len(fieldnames) else (key or "")
                    val = raw.get(key, "")
                    if isinstance(val, str):
                        val = val.strip()
                    cleaned[norm_key] = _infer_type(val) if infer_types else (val or "")
                # Include any extra keys not in fieldnames (edge CSVs)
                for k, v in raw.items():
                    if k not in (reader.fieldnames or []) and k not in cleaned:
                        cleaned[str(k).strip() if isinstance(k, str) else str(k)] = v
                if cleaned:
                    rows.append(cleaned)

        return {"success": True, "data": rows, "count": len(rows)}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}


def parse_csv_bytes(
    file_name: str,
    data: bytes,
    *,
    normalize_headers: bool = True,
    make_identifier_headers: bool = False,
    infer_types: bool = True,
    delimiter: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse CSV content from memory (bytes) and return the same shape as parse_csv_generic."""
    try:
        bio = io.StringIO(data.decode("utf-8-sig"))
        # Detect dialect if not provided
        if delimiter is None:
            sample = bio.read(4096)
            bio.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except Exception:
                dialect = csv.excel
        else:
            dialect = csv.excel
            dialect.delimiter = delimiter  # type: ignore[attr-defined]

        reader = csv.DictReader(bio, dialect=dialect)
        if reader.fieldnames:
            fieldnames = [
                _normalize_header(h, make_identifier_headers) if normalize_headers else (h or "")
                for h in reader.fieldnames
            ]
        else:
            fieldnames = []

        rows: List[Dict[str, Any]] = []
        for raw in reader:
            cleaned: Dict[str, Any] = {}
            for idx, key in enumerate(reader.fieldnames or []):
                norm_key = fieldnames[idx] if idx < len(fieldnames) else (key or "")
                val = raw.get(key, "")
                if isinstance(val, str):
                    val = val.strip()
                cleaned[norm_key] = _infer_type(val) if infer_types else (val or "")
            for k, v in raw.items():
                if k not in (reader.fieldnames or []) and k not in cleaned:
                    cleaned[str(k).strip() if isinstance(k, str) else str(k)] = v
            if cleaned:
                rows.append(cleaned)

        return {"success": True, "data": rows, "count": len(rows)}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}
