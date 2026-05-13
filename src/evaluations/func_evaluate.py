# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.

from .executor_utils import function_with_timeout


def evaluate_io(
    sample_io: list[str],
    completion: str,
    timeout: int = 5,
    stop_early: bool = False,
):
    test_log = ""
    passed = True
    for io in sample_io:
        try:
            code = (
                (
                    "from typing import *\n"
                    if "from typing import *" not in completion
                    else ""
                )
                + completion
                + "\n"
                + io
                + "\n"
            )
            function_with_timeout(exec, (code, globals()), timeout)
            test_log += f"passed in test case: {io}\n"
        except TimeoutError:
            return "timeout", f"timed out in test case: {io}\n"
        except Exception:
            if stop_early:
                return "failed", f"failed in test case: {io}\n"
            passed = False
            test_log += f"failed in test case: {io}\n"

    return ("passed" if passed else "failed"), test_log


def evaluate_io_et(
    sample_io: list[str],
    completion: str,
    timeout: int = 5,
    prompt: str = "",
):
    io = "\n".join(sample_io)
    try:
        code = (
            (
                "from typing import *\n"
                if "from typing import *" not in completion
                else ""
            )
            + prompt
            + completion
            + "\n"
            + io
            + "\n"
        )
        function_with_timeout(exec, (code, globals()), timeout)
        return "passed"
    except TimeoutError:
        return "timeout"
    except Exception:
        return "failed"


def evaluate_functional_correctness(
    problem: dict,
    completion: str,
    timeout: int = 5,
    test_key: str = "test",
):
    try:
        code = (
            (
                "from typing import *\n"
                if "from typing import *" not in completion
                else ""
            )
            + completion
            + "\n"
            + problem[test_key]
            + "\n"
            + f"check({problem['entry_point']})"
        )

        function_with_timeout(exec, (code, globals()), timeout)
        return "passed"
    except TimeoutError:
        return "timeout"
    except Exception:
        return "failed"


def evaluate_functional_correctness2(
    problem: dict,
    completion: str,
    timeout: float = 5,
) -> str:

    check_program = (
        # problem["prompt"] +
        "from typing import *\n"
        + completion
        + "\n"
        + problem["test"]
        + "\n"
        + f"check({problem['entry_point']})"
    )
    # print(check_program)

    try:
        exec(check_program)
        return "passed"
    except TimeoutException:
        return "timeout"
    except BaseException:
        return "failed"


class TimeoutException(Exception):
    pass
