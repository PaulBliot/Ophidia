import json
import pathlib
import types
import ast
import pytest


def _load_codon_optimize_seq():
    nb_path = pathlib.Path(__file__).resolve().parents[1] / "Updated Code from Nature Paper.ipynb"
    nb = json.loads(nb_path.read_text())
    func_def = None
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "codon_optimize_seq":
                func_def = node
                break
        if func_def is not None:
            break
    if func_def is None:
        raise RuntimeError("codon_optimize_seq not found in notebook")
    module = types.ModuleType("notebook_module")
    module.DNACHISEL_AVAILABLE = False
    class _Logger:
        def info(self, *args, **kwargs):
            pass
        def warning(self, *args, **kwargs):
            pass
    module.logger = _Logger()
    code = ast.Module(body=[func_def], type_ignores=[])
    exec(compile(code, filename="<ast>", mode="exec"), module.__dict__)
    return module.codon_optimize_seq


codon_optimize_seq = _load_codon_optimize_seq()


def test_codon_mapping_without_dnachisel():
    assert codon_optimize_seq("MA") == "ATGGCT"


def test_unknown_amino_acid_raises_value_error():
    with pytest.raises(ValueError):
        codon_optimize_seq("Z")
