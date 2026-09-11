"""Validate a local JSON Lines file without sending or rewriting its contents."""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path


def reject_constant(value):
    raise ValueError("non-finite JSON constant")


def check_file(path, *, objects_only=False, max_errors=20):
    if max_errors < 1:
        raise ValueError("max_errors must be positive")
    report = {"lines": 0, "valid": 0, "invalid": 0, "errors": []}
    with Path(path).open("rb") as source:
        for number, raw in enumerate(source, 1):
            report["lines"] += 1
            error = None
            if raw.startswith(b"\xef\xbb\xbf"):
                error = {"code": "bom", "message": "UTF-8 BOM is not allowed."}
            else:
                try:
                    line = raw.decode("utf-8")
                except UnicodeDecodeError:
                    error = {"code": "encoding", "message": "Line is not valid UTF-8."}
                else:
                    if not line.strip(" \t\r\n"):
                        error = {"code": "blank", "message": "Blank lines are not JSON values."}
                    else:
                        try:
                            value = json.loads(
                                line, parse_constant=reject_constant,
                                parse_float=Decimal, parse_int=Decimal,
                            )
                        except json.JSONDecodeError as exc:
                            error = {
                                "code": "json", "column": exc.colno,
                                "message": "Invalid JSON syntax.",
                            }
                        except ValueError:
                            error = {"code": "constant", "message": "NaN and Infinity are not JSON values."}
                        except RecursionError:
                            error = {"code": "depth_limit", "message": "Nesting exceeds this Python runtime's limit."}
                        else:
                            if objects_only and not isinstance(value, dict):
                                error = {"code": "object_required", "message": "Expected a JSON object."}
            if error:
                report["invalid"] += 1
                if len(report["errors"]) < max_errors:
                    report["errors"].append({"line": number, **error})
            else:
                report["valid"] += 1
    report["errors_omitted"] = report["invalid"] - len(report["errors"])
    report["ok"] = report["invalid"] == 0
    return report


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local UTF-8 JSONL file")
    parser.add_argument("--objects-only", action="store_true", help="Require one object per line")
    parser.add_argument("--max-errors", type=positive_int, default=20, help="Maximum reported errors; all lines are counted")
    args = parser.parse_args(argv)
    try:
        report = check_file(args.input, objects_only=args.objects_only, max_errors=args.max_errors)
    except OSError:
        print(json.dumps({"ok": False, "error": "Cannot read the input file."}))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
