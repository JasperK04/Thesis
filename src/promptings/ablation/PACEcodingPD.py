import json
import re
import sys
from typing import Any

from lxml import etree  # type: ignore

# import tiktoken
from ..Base import BaseStrategy

mapping = {
    1: "one (01)",
    2: "two (02)",
    3: "three (03)",
    4: "four (04)",
    5: "five (05)",
    6: "six (06)",
    7: "seven (07)",
    8: "eight (08)",
    9: "nine (09)",
}

COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[34m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{COLOR_RESET}"


class PACEcoding(BaseStrategy):
    def __init__(self, k: int = 3, t: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.k = k
        self.t = t

    def xml_to_dict(self, element):
        result = {}
        for child in element:
            if len(child):
                child_data = self.xml_to_dict(child)
                if child.tag in result:
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = [result[child.tag], child_data]
                else:
                    result[child.tag] = child_data
            else:
                result[child.tag] = child.text
        return result

    def parse_xml(self, response: str, require_problem: bool = True) -> dict:
        def clean_input(text: str) -> str:
            text = text.strip()

            text = re.sub(r"```xml\s*", "", text)
            text = re.sub(r"```", "", text)

            text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;)", "&amp;", text)

            text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

            text = re.sub(r"<\?xml.*?\?>", "", text)

            return text.strip()

        def ensure_root(text: str) -> bytes:
            try:
                etree.fromstring(text.encode("utf-8"))
                return text.encode("utf-8")
            except Exception:
                return f"<root>{text}</root>".encode("utf-8")

        cleaned = clean_input(response)
        wrapped = ensure_root(cleaned)

        parser = etree.XMLParser(
            recover=True,
            remove_comments=True,
            remove_pis=True,
            strip_cdata=False,
            resolve_entities=False,
        )

        try:
            root = etree.fromstring(wrapped, parser=parser)
        except Exception:
            return {"error": "Invalid XML", "raw": response}

        result = self.xml_to_dict(root)

        print(
            color_text(
                f"Parsed XML to dict:\n{json.dumps(result, indent=2)}", COLOR_YELLOW
            ),
            flush=True,
        )

        if "root" in result and "problem" not in result:
            nested = result.get("root")
            if isinstance(nested, dict):
                result = nested

        if "problem" in result:
            if not isinstance(result["problem"], list):
                result["problem"] = [result["problem"]]
            for i, problem in enumerate(result["problem"]):
                if isinstance(problem, str):
                    result["problem"][i] = {
                        "description": problem,
                        "code": "",
                        "planning": "",
                        "techniques": "",
                    }
        else:
            if require_problem:
                print(
                    color_text("Warning: No <problem> tag found in XML.", COLOR_RED),
                    file=sys.stderr,
                )

        return result

    def parse_code(self, response: str) -> str:
        if "```" not in response:
            return response

        code_pattern = r"```(?:[a-zA-Z0-9#+]*\n)?([\s\S]*?)```"
        code_blocks = re.findall(code_pattern, response, re.DOTALL)

        if code_blocks:
            return code_blocks[-1].strip()
        return response

    @staticmethod
    def trim_text(text: str, trimmed_text: str):
        return text.replace(trimmed_text, "").strip()

    @staticmethod
    def replace_tag(text: str, tag: str):
        if f"<{tag}><![CDATA[" in text and f"]]></{tag}>" in text:
            return text
        else:
            return (
                text.replace(f"<{tag}>", f"<{tag}><![CDATA[")
                .replace(f"</{tag}>", f"]]></{tag}>")
                .strip()
            )

    @staticmethod
    def get_sample_io_str(sample_io: Any) -> str:
        if len(sample_io) > 0:
            if isinstance(sample_io[0], str):
                return "\n".join(sample_io)
            if isinstance(sample_io[0], dict):
                return "\n".join(
                    [
                        f"Input:\n{io['input']}\nExpected output:\n{io['output'][0]}"
                        for io in sample_io
                    ]
                )
        return sample_io

    def run_single_pass(self, item: dict):
        print("", flush=True)

        pr_tok = 0
        com_tok = 0

        sample_io_prompt = (
            f"## Sample Test cases: \n{self.get_sample_io_str(item['sample_io'])}\n"
        )

        plannings = []
        for example_no in range(self.k):
            input_for_problem_planning = [
                {
                    "role": "user",
                    "content": f"""
Plan {mapping[example_no + 1]}:
Given a competitive programming problem, generate one unique, detailed, step-by-step plan to solve it.

# Problem to Solve:
{self.data.get_prompt(item)}

# Sample Test Cases:
{sample_io_prompt}

# Detailed Planning:
Create a detailed, step-by-step plan to solve the problem. Structure your plan as:
1. Step 1: [Description of first step]
2. Step 2: [Description of second step]
...
n. Step n: [Description of final step]

Important: 
- Be specific and concrete in each step
- Consider edge cases and input/output handling
- Include time and space complexity considerations
- Do not generate code, only the planning
""".strip(),
                }
            ]

            print(color_text("\n\n________________________", COLOR_BLUE))
            print(
                color_text(
                    f"Input for our problem planning using example: {example_no}:",
                    COLOR_BLUE,
                )
            )
            print(input_for_problem_planning[0]["content"], flush=True)

            planning, pr_tok_1, com_tok_1 = self.gpt_chat(input_for_problem_planning)
            item["api_calls"] += 1
            pr_tok += pr_tok_1
            com_tok += com_tok_1

            print(color_text("\n\n________________________", COLOR_BLUE))
            print(color_text("Response from our problem planning:", COLOR_BLUE))
            print(planning, flush=True)

            plannings.append(planning)

        plans_prompt = "\n".join(
            f"plan {i}: {plan}" for i, plan in enumerate(plannings, start=1)
        )

        input_for_planning_verification = [
            {
                "role": "user",
                "content": f"""
Evaluate the following plans for solving the problem. 
Provide a confidence score (0-100) for each plan and explain your reasoning.
You must not assign any plan the same score as another plan such that there is a clear ranking.

# Problem:
{self.data.get_prompt(item)}

# Proposed Plans:
{plans_prompt}

# Evaluation Criteria:
1. Completeness: Does the plan cover all aspects of the problem?
2. Correctness: Is the algorithmic approach sound?
3. Feasibility: Can the plan be implemented effectively?
4. Edge Cases: Does the plan consider boundary conditions?
5. Efficiency: Does the plan consider time and space complexity?

# Your Response:
<root>
<plan>
<analysis>
# Detailed analysis of the plan's strengths and weaknesses
</analysis>
<confidence>
# Confidence score (0-100 integer) based on the above criteria
</confidence>
</plan>
# Add the other plan's analysis and confidence here...
</root>
""".strip(),
            }
        ]

        print(color_text("Input for planning verification:", COLOR_BLUE))
        print(input_for_planning_verification[0]["content"], flush=True)

        verification_res, pr_tok_1, com_tok_1 = self.gpt_chat(
            input_for_planning_verification
        )
        item["api_calls"] += 1
        pr_tok += pr_tok_1
        com_tok += com_tok_1

        verification_res = self.replace_tag(verification_res, "analysis")
        verification_res = self.replace_tag(verification_res, "confidence")
        verification_res = self.parse_xml(verification_res, require_problem=False)

        if "error" in verification_res:
            print(
                color_text(
                    f"Error parsing XML: {verification_res['error']}", COLOR_RED
                ),
                file=sys.stderr,
                flush=True,
            )
            print(
                color_text(f"Raw response: {verification_res['raw']}", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )

        if "plan" not in verification_res:
            print(
                color_text("Warning: No <plan> tag found in XML.", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )

        verified_plans = []
        for plan_dict, planning in zip(verification_res.get("plan", []), plannings):
            if "analysis" not in plan_dict:
                print(
                    color_text(
                        "Warning: Missing <analysis> tag in a <plan>.", COLOR_RED
                    ),
                    file=sys.stderr,
                    flush=True,
                )
                continue
            if "confidence" not in plan_dict:
                print(
                    color_text(
                        "Warning: Missing <confidence> tag in a <plan>.", COLOR_RED
                    ),
                    file=sys.stderr,
                    flush=True,
                )
                continue

            confidence_score = 0
            try:
                confidence_text = plan_dict.get("confidence", "0")
                confidence_score = int(re.search(r"\d+", confidence_text).group())  # type: ignore
                confidence_score = max(0, min(100, confidence_score))
            except Exception as e:
                print(
                    color_text(f"Error parsing confidence score: {e}", COLOR_RED),
                    file=sys.stderr,
                    flush=True,
                )
                confidence_score = 50

            print(color_text("Response from planning verification:", COLOR_BLUE))
            print(f"Analysis: {plan_dict.get('analysis', '')}")
            print(f"Confidence: {confidence_score}")

            verified_plans.append((planning, confidence_score))

        verified_plans.sort(key=lambda x: x[1], reverse=True)

        if not verified_plans:
            print(
                color_text("No valid plannings generated.", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )
            return "no plans generated", pr_tok, com_tok

        for planning_with_ex in verified_plans:
            planning, _ = planning_with_ex

            input_for_final_code_generation = [
                {
                    "role": "user",
                    "content": f"""
Generate {self.language} code to solve the following problem based on the provided plan.
# Problem:
{self.data.get_prompt(item)}

# Planning:
{planning}

# Sample Test Cases:
{sample_io_prompt}

# Instructions:
1. Implement the solution exactly as per the planning
2. Add comments to explain key steps
3. Handle edge cases appropriately

# Your Response:
Generate only the {self.language} code. Do not include any explanations.
""".strip(),
                }
            ]

            print(color_text("\n\n________________________", COLOR_BLUE))
            print(color_text("Input for final code generation:", COLOR_BLUE))
            print(input_for_final_code_generation[0]["content"], flush=True)

            code, pr_tok_1, com_tok_1 = self.gpt_chat(input_for_final_code_generation)
            item["api_calls"] += 1
            code = self.parse_code(code)
            pr_tok += pr_tok_1
            com_tok += com_tok_1

            print(color_text("\n\n________________________", COLOR_BLUE))
            print(color_text("Response from final code generation:", COLOR_BLUE))
            print(color_text(code, COLOR_YELLOW), flush=True)

            passed = False

            for i in range(1, self.t + 1):
                passed, test_log, failure_reason = self.data.evaluate_sample_io(
                    item, code, self.language
                )

                if passed:
                    break

                print(
                    color_text(f"Input for improving code generation: {i}", COLOR_BLUE)
                )
                input_for_improving_code = [
                    {
                        "role": "user",
                        "content": f"""
Given a competitive programming problem you have generated {self.language} code to solve the problem. 
But the generated code can not pass sample test cases. 
Improve your code to solve the problem correctly.

## Problem to be solved:
{self.data.get_prompt(item)}

## Failure Reason:
{failure_reason}
## Test Report:
{test_log}

## Modified Planning:

## Let's think step by step to modify {self.language} Code for solving this problem.

----------------
Important:
Your response must contain the modified planning and then the {self.language} code inside ``` block to solve this problem.
""".strip(),
                    }
                ]

                print(color_text("\n\n________________________", COLOR_BLUE))
                print(color_text("Input for improving code generation:", COLOR_BLUE))
                print(input_for_improving_code[0]["content"], flush=True)

                response, pr_tok_1, com_tok_1 = self.gpt_chat(input_for_improving_code)
                item["api_calls"] += 1
                # time.sleep(1)

                code = self.parse_code(response)
                pr_tok += pr_tok_1
                com_tok += com_tok_1

                print(color_text("\n\n________________________", COLOR_BLUE))
                print(
                    color_text("Response from improving code generation:", COLOR_BLUE)
                )
                print(response, flush=True)

            # got a code that passed all sample test cases
            if passed:
                break

        print(color_text("________________________\n\n", COLOR_BLUE), flush=True)
        if not code or code.strip() == "":
            code = "no code generated"
        return code, pr_tok, com_tok
