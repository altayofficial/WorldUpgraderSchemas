import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator


class SchemaValidator:
    def __init__(self, schema_dir: Path, meta_schema_file: Path):
        self.schema_dir = schema_dir
        self.validator = Draft7Validator(json.loads(meta_schema_file.read_text()))

    def run(self) -> bool:
        files = sorted(self.schema_dir.glob("*.json"))
        if not files:
            print(f"no JSON files found in {self.schema_dir}")
            return False

        ok = True
        for file in files:
            if not self.validate_file(file):
                ok = False

        print(f"{len(files)} files checked")
        return ok

    def validate_file(self, file: Path) -> bool:
        try:
            data = json.loads(file.read_text())
        except json.JSONDecodeError as e:
            print(f"FAIL {file.name}: invalid JSON: {e}")
            return False

        errors = list(self.validator.iter_errors(data))
        for error in errors:
            path = "/".join(str(p) for p in error.absolute_path)
            print(f"FAIL {file.name}: {path}: {error.message}")

        if not errors:
            print(f"OK   {file.name}")
        return not errors


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <schema_dir> <meta_schema_file>")
        sys.exit(2)

    validator = SchemaValidator(Path(sys.argv[1]), Path(sys.argv[2]))
    sys.exit(0 if validator.run() else 1)


if __name__ == "__main__":
    main()
