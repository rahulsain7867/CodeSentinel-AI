"""
Test Runner Agent — Generates and executes test validation suites using safe code execution.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.utils import instructions_utils
from code_review_assistant.config import config


async def test_runner_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamic instruction provider injecting code under test and execution rules."""
    template = """You are CodeSentinel AI's Automated Test Specialist.

THE CODE TO TEST IS:
```
{code_to_review}
```

YOUR TASK:
1. Determine the apparent intent and language of the code.
2. Generate comprehensive unit and edge-case test suites (15-20 assertions).
3. Execute tests safely using your built-in code executor.
4. Analyze pass/fail/crash rates and identify root cause issues.
5. Output detailed JSON analysis.

Output ONLY this JSON structure:
{{
    "test_summary": {{
        "total_tests_run": <number>,
        "tests_passed": <number where code worked correctly>,
        "tests_failed": <number where code gave wrong results>,
        "tests_with_errors": <number where code crashed>,
        "critical_issues_found": <number of fundamental problems>
    }},
    "critical_issues": [
        {{
            "type": "interface_bug|logic_error|crash|security_risk",
            "description": "Clear explanation of the issue",
            "example_input": "Input that triggers the issue",
            "expected_behavior": "What should happen",
            "actual_behavior": "What actually happened",
            "severity": "high|medium|low"
        }}
    ],
    "test_categories": {{
        "basic_functionality": {{"passed": 0, "failed": 0, "errors": 0}},
        "edge_cases": {{"passed": 0, "failed": 0, "errors": 0}},
        "error_handling": {{"passed": 0, "failed": 0, "errors": 0}}
    }},
    "function_behavior": {{
        "apparent_purpose": "What this function seems designed to do",
        "actual_interface": "How it actually needs to be called",
        "unexpected_requirements": []
    }},
    "verdict": {{
        "status": "WORKING|BUGGY|BROKEN",
        "confidence": "high|medium|low",
        "recommendation": "Ready to use|Needs minor fixes|Needs major fixes"
    }}
}}

Do NOT output the raw test source code, only the JSON summary."""

    return await instructions_utils.inject_session_state(template, context)


test_runner_agent = Agent(
    name="TestRunner",
    model=config.worker_model,
    description="Generates and executes automated tests using safe sandbox code execution.",
    instruction=test_runner_instruction_provider,
    code_executor=BuiltInCodeExecutor(),
    output_key="test_execution_summary"
)
