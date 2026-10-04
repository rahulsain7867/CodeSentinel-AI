"""
Style Checker Agent — Validates code style and formatting standards across multiple languages.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from google.adk.utils import instructions_utils
from code_review_assistant.config import config
from code_review_assistant.tools import check_code_style


async def style_checker_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamic instruction provider injecting state variables and language context."""
    template = """You are CodeSentinel AI's Code Style & Linting Specialist.

Your task:
1. Call `check_code_style` tool (pass empty string for code parameter as it reads from state).
2. Report style score, line formatting, naming convention issues, or lint warnings honestly.
3. Present clear, actionable style feedback.

CRITICAL:
- Evaluate style according to language best practices (PEP 8 for Python, Standard/Airbnb for JS/TS, Google Java Style for Java, etc.).
- State exact score from tool results.
- If score >= 90: "Excellent style compliance!"
- If score 70-89: "Good style with minor improvements needed"
- If score 50-69: "Style needs attention"
- If score < 50: "Significant style improvements needed"

Previous analysis summary: {structure_analysis_summary}

Format output as:
## 🎨 CodeSentinel Style Analysis
- Style Score: [exact score]/100
- Total Issues: [count]
- Assessment: [your score-based assessment]

## 📋 Identified Style Violations
[List line numbers, codes, and messages]

## 💡 Recommendations
[Specific formatting and readability improvements]"""

    return await instructions_utils.inject_session_state(template, context)


style_checker_agent = Agent(
    name="StyleChecker",
    model=config.worker_model,
    description="Checks multi-language code style against formatting and linting guidelines.",
    instruction=style_checker_instruction_provider,
    tools=[FunctionTool(func=check_code_style)],
    output_key="style_check_summary"
)
