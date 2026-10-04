"""
Code Fixer Agent — Generates multi-language fixes and code refactoring.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.utils import instructions_utils
from code_review_assistant.config import config


async def code_fixer_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamic instruction provider instructing agent to output corrected code in target language."""
    template = """You are CodeSentinel AI's Code Refactoring & Auto-Fix Specialist.

Original Code:
```
{code_to_review}
```

Analysis & Review Summary:
- Target Language: {code_language}
- Style Score: {style_score}/100
- Style Issues: {style_issues}
- Test Execution Summary: {test_execution_summary}

YOUR TASK:
Generate the complete, fully-corrected code addressing all identified bugs, edge cases, and style violations.

CRITICAL INSTRUCTIONS:
- Output ONLY the corrected source code.
- Do NOT wrap with markdown backticks or commentary unless required by your executor.
- Maintain the original language programming paradigms and best practices.
- Ensure all functions, error handlers, docstrings/comments, and imports are fully resolved."""

    return await instructions_utils.inject_session_state(template, context)


code_fixer_agent = Agent(
    name="CodeFixer",
    model=config.worker_model,
    description="Generates complete code fixes addressing logic bugs, edge cases, and style issues.",
    instruction=code_fixer_instruction_provider,
    code_executor=BuiltInCodeExecutor(),
    output_key="code_fixes"
)
