"""Static audit of distributed notebooks. No participant datasets are loaded."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(path: Path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc.get("nbformat") == 4
    errors = []
    n_code = 0
    for index, cell in enumerate(doc.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        n_code += 1
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
        if cell.get("outputs"):
            errors.append(f"cell {index}: execution output not stripped")
        if re_magic(source):
            continue
        try:
            ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"cell {index}: {exc.msg} at line {exc.lineno}")
    return n_code, errors


def re_magic(code):
    return any(line.lstrip().startswith(("%", "!", "?")) for line in code.splitlines())


if __name__ == "__main__":
    paths = sorted((ROOT / "legacy" / "notebooks").glob("*.ipynb"))
    assert paths, "No notebooks found"
    issues = 0
    for path in paths:
        n, failures = audit(path)
        print(f"{path.name}: {n} code cells; {len(failures)} static findings")
        for failure in failures:
            print("  ", failure)
        issues += len(failures)
    raise SystemExit(bool(issues))
