import os
import subprocess
import tempfile

from .exec_outcome import ExecOutcome


def _run_python_source(
    source_code: str, stdin_data: str, timeout: int
) -> tuple[int, str, str, bool]:
    # Write source to temp file then execute with python
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
        tf.write(source_code)
        tmp_name = tf.name

    try:
        proc = subprocess.run(
            [os.getenv("PYTHON_EXECUTABLE", "python3"), tmp_name],
            input=stdin_data.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return (
            proc.returncode,
            proc.stdout.decode(errors="replace"),
            proc.stderr.decode(errors="replace"),
            False,
        )
    except subprocess.TimeoutExpired as te:
        return -1, "", str(te), True
    finally:
        try:
            os.unlink(tmp_name)
        except Exception:
            pass


def execute_code_locally(
    language: str,
    source_code: str,
    unittests: list[dict],
    limits: dict | None = None,
    **kwargs,
) -> list[dict]:
    lang_norm = str(language).lower().replace(" ", "").replace("-", "")
    if not lang_norm.startswith("python"):
        raise ValueError(f"Local executor only supports Python3: got {language}")

    timeout = 5

    results = []
    for test in unittests:
        inp = test.get("input", "")
        expected_field = test.get("output", [])
        # Accept either a list of outputs or a single string output from datasets
        if isinstance(expected_field, list) and len(expected_field) > 0:
            expected = expected_field[0]
        elif isinstance(expected_field, str):
            expected = expected_field
        else:
            expected = str(expected_field) if expected_field is not None else ""

        returncode, stdout, stderr, timed_out = _run_python_source(
            source_code, inp, timeout
        )

        if timed_out:
            outcome = ExecOutcome.TIME_LIMIT_EXCEEDED.value
            result_text = ""
        elif returncode != 0:
            outcome = ExecOutcome.RUNTIME_ERROR.value
            result_text = stderr.strip()
        else:
            result_text = stdout.strip()
            # Normalize whitespace for comparison and compare string forms
            if result_text.strip() == str(expected).strip():
                outcome = ExecOutcome.PASSED.value
            else:
                outcome = ExecOutcome.WRONG_ANSWER.value

        results.append(
            {
                "input": inp,
                "output": [result_text],
                "result": result_text,
                "exec_outcome": outcome,
            }
        )

    return results
