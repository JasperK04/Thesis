import json
import re
import sys
from typing import Any

from lxml import etree  # type: ignore

from challenge_datasets import APPSDataset

# import tiktoken
from .Base import BaseStrategy

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

        input_kb_exemplars = [
            {
                "role": "user",
                "content": f"""
Given a problem, provide relevant problems and learn the relevant algorithms behind them. 
You must identify the algorithms and explain them in a detailed tutorial including the algorithmic concepts, efficiency, and use cases.

# Problem:
{self.data.get_prompt(item)}

# Exemplars:
Recall {self.k} relevant and distinct problems (different from the given problem). For each problem:
1. Describe it concisely
2. Generate pseudocode step by step to solve that problem
3. Analyze and extract 1-3 key code generation techniques or algorithms used in the solution
4. Generate a detailed planning to solve that problem that includes the identified techniques, algorithms and efficiency

# Algorithm:

----------------
Important:
Your response must follow the following xml format:

<root>
<problem>
<description>
# Describe the problem concisely.
</description>
<pseudocode>
# Let's think step by step to solve this problem in pseudocode.
</pseudocode>
<techniques>
# Extract 1-3 key code generation techniques and algorithms used in this solution.
</techniques>
<planning>
# Detailed planning to solve this problem including the identified techniques, algorithms and efficiency.
</planning>
</problem>

# Add more problems here...

<algorithm>
# Identify the most efficient algorithm (Brute-force, Dynamic Programming, Divide-and-conquer, Greedy, Backtracking, Recursive, Binary search, etc.) that can be used to solve the original problem.
# Write a useful tutorial about the identified algorithm. Provide a high-level generic tutorial for solving this type of problem. Do not generate code.
</algorithm>

<learned_techniques>
# Summarize the key code generation techniques learned from all the examples.
</learned_techniques>
</root>
""",
            },
        ]

        print(color_text("\n\n________________________", COLOR_BLUE))
        print(color_text("Input for knowledge base and exemplars:", COLOR_BLUE))
        print(input_kb_exemplars[0]["content"], flush=True)

        response, pr_tok, com_tok = self.gpt_chat(processed_input=input_kb_exemplars)
        item["api_calls"] = item.get("api_calls", 0) + 1

        response = self.replace_tag(response, "algorithm")
        response = self.replace_tag(response, "description")
        response = self.replace_tag(response, "code")
        response = self.replace_tag(response, "planning")
        response = self.replace_tag(response, "techniques")
        response = self.replace_tag(response, "learned_techniques")

        print(color_text("\n\n________________________", COLOR_BLUE))
        print(color_text("Response from knowledge base and exemplars:", COLOR_BLUE))
        print(response, flush=True)

        response = self.parse_xml(response)
        if "error" in response:
            print(
                color_text(f"Error parsing XML: {response['error']}", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )
            print(
                color_text(f"Raw response: {response['raw']}", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )
            return str(response), pr_tok, com_tok

        problems = response.get("problem", [])
        if not problems:
            print(
                color_text("Warning: No <problem> tag found in XML.", COLOR_RED),
                file=sys.stderr,
            )
            return "no problems found in XML", pr_tok, com_tok
        if not isinstance(problems, list):
            problems = [problems]

        algorithm_prompt = f"## Relevant Algorithm: {response.get('algorithm', '')}"
        learned_techniques = f"## Learned Code Generation Techniques: {response.get('learned_techniques', '')}"
        sample_io_prompt = (
            f"## Sample Test cases: \n{self.get_sample_io_str(item['sample_io'])}\n"
        )

        plannings = []
        for example_no, example in enumerate(problems, start=1):
            if isinstance(example, str):
                example = {
                    "description": example,
                    "code": "",
                    "planning": "",
                    "techniques": "",
                }

            example_problem = example.get("description", "")
            example_planning = example.get("planning", "")
            example_techniques = example.get("techniques", "")

            input_for_problem_planning = [
                {
                    "role": "user",
                    "content": f"""
Given a competitive programming problem, generate {mapping[self.k]} unique, detailed, step-by-step plans to solve it.
# Example Problem:
{example_problem}

# Example Techniques:
{example_techniques}

# Example Planning:
{example_planning}

# Algorithm:
{algorithm_prompt}

# Learned Techniques:
{learned_techniques}

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
""",
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

            input_for_planning_verification = [
                {
                    "role": "user",
                    "content": f"""Evaluate the following plan for solving the problem. Provide a confidence score (0-100) and explain your reasoning.
# Problem:
{self.data.get_prompt(item)}

# Proposed Plan:
{planning}

# Evaluation Criteria:
1. Completeness: Does the plan cover all aspects of the problem?
2. Correctness: Is the algorithmic approach sound?
3. Feasibility: Can the plan be implemented effectively?
4. Edge Cases: Does the plan consider boundary conditions?
5. Efficiency: Does the plan consider time and space complexity?

# Your Response:
<root>
<analysis>
# Detailed analysis of the plan's strengths and weaknesses
</analysis>
<confidence>
# Confidence score (0-100 integer) based on the above criteria
</confidence>
</root>
""",
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
                continue

            confidence_score = 0
            try:
                confidence_text = verification_res.get("confidence", "0")
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
            print(f"Analysis: {verification_res.get('analysis', '')}")
            print(f"Confidence: {confidence_score}")

            plannings.append((planning, confidence_score, example))

        plannings.sort(key=lambda x: x[1], reverse=True)

        if not plannings:
            print(
                color_text("No valid plannings generated.", COLOR_RED),
                file=sys.stderr,
                flush=True,
            )
            return "no plans generated", pr_tok, com_tok

        if isinstance(self.data, APPSDataset):
            std_input_prompt = "## Note: Strictly follow the input and output format. Take input from stdin and output to stdout. If writing a function, after the function definition, take input using `input()`, call the function, and print the result. Avoid extra print statements."
        else:
            std_input_prompt = ""

        for planning_with_ex in plannings:
            planning, confidence, example = planning_with_ex

            input_for_final_code_generation = [
                {
                    "role": "user",
                    "content": f"""Generate {self.language} code to solve the following problem based on the provided plan.
# Problem:
{self.data.get_prompt(item)}

# Planning:
{planning}

# Sample Test Cases:
{sample_io_prompt}

# Learned Techniques:
{learned_techniques}

# Algorithm:
{algorithm_prompt}

# Instructions:
1. Implement the solution exactly as per the planning
2. Add comments to explain key steps
3. Handle edge cases appropriately
4. {std_input_prompt}

# Your Response:
Generate only the {self.language} code. Do not include any explanations.
""",
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
                passed, test_log = self.data.evaluate_sample_io(
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
                        "content": f"Given a competitive programming problem you have generated {self.language} code to solve the problem. But the generated code can not pass sample test cases. Improve your code to solve the problem correctly.\n{algorithm_prompt}\n## Problem to be solved:\n{self.data.get_prompt(item)}\n{response}\n## Test Report:\n{test_log}\n## Modified Planning:\n## Let's think step by step to modify {self.language} Code for solving this problem.\n\n----------------\nImportant:\n{std_input_prompt}\n## Your response must contain the modified planning and then the {self.language} code inside ``` block to solve this problem.",
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
