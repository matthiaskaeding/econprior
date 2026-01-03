# /// script
# requires-python = ">=3.11"
# ///
"""Execute a Jupyter notebook in-place so outputs stay updated."""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import traceback
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute a notebook and write outputs in-place."
    )
    parser.add_argument("notebook", type=str, help="Notebook path to execute")
    return parser.parse_args()


def _split_body(module: ast.Module) -> tuple[List[ast.stmt], ast.expr | None]:
    body = list(module.body)
    last_expr: ast.expr | None = None
    if body and isinstance(body[-1], ast.Expr):
        last_expr = body[-1].value
        body = body[:-1]
    return body, last_expr


def _format_stream(text: str) -> Dict[str, Any]:
    return {"name": "stdout", "output_type": "stream", "text": text}


def _format_execute_result(value: Any) -> Dict[str, Any]:
    return {
        "output_type": "execute_result",
        "data": {"text/plain": repr(value)},
        "metadata": {},
    }


def _format_error(exc: BaseException) -> Dict[str, Any]:
    return {
        "output_type": "error",
        "ename": exc.__class__.__name__,
        "evalue": str(exc),
        "traceback": traceback.format_exception(exc.__class__, exc, exc.__traceback__),
    }


def execute_notebook(notebook_path: Path) -> None:
    data = json.loads(notebook_path.read_text())
    namespace: Dict[str, Any] = {"__name__": "__main__"}
    execution_count = 1

    try:
        for cell in data.get("cells", []):
            if cell.get("cell_type") != "code":
                continue

            source = "".join(cell.get("source", []))
            cell_outputs: List[Dict[str, Any]] = []
            cell["execution_count"] = execution_count
            execution_count += 1

            if not source.strip():
                cell["outputs"] = []
                continue

            stdout_buffer = io.StringIO()
            error: BaseException | None = None
            result: Any = None

            try:
                module = ast.parse(source, mode="exec")
                body, last_expr = _split_body(module)
                exec_module = ast.Module(
                    body=body, type_ignores=getattr(module, "type_ignores", [])
                )
                exec_code = compile(exec_module, str(notebook_path), "exec")

                with contextlib.redirect_stdout(stdout_buffer):
                    exec(exec_code, namespace)
                    if last_expr is not None:
                        expr_code = compile(
                            ast.Expression(last_expr), str(notebook_path), "eval"
                        )
                        result = eval(expr_code, namespace)
            except Exception as exc:  # noqa: BLE001 - we want to bubble up notebook failures
                error = exc

            stream_text = stdout_buffer.getvalue()
            if stream_text:
                cell_outputs.append(_format_stream(stream_text))

            if error is not None:
                cell_outputs.append(_format_error(error))
                cell["outputs"] = cell_outputs
                raise error

            if result is not None:
                cell_outputs.append(_format_execute_result(result))

            cell["outputs"] = cell_outputs
    finally:
        notebook_path.write_text(json.dumps(data, indent=2))


def main() -> None:
    args = parse_args()
    notebook_path = Path(args.notebook).expanduser().resolve()
    execute_notebook(notebook_path)


if __name__ == "__main__":
    main()
