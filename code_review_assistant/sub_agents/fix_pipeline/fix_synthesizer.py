"""
Fix Synthesizer Agent — Formats CodeSentinel AI auto-fix results and metrics.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from google.adk.utils import instructions_utils
from code_review_assistant.config import config
from code_review_assistant.tools import save_fix_report


async def fix_synthesizer_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamic instruction provider injecting validation state and fixed code."""
    template = """You are CodeSentinel AI's Sentinel Fix Specialist.

Validation Report: {final_fix_report}
Fixed Code: {code_fixes}
Fix Status: {fix_status}

Format your final response cleanly:

# ⚡ CodeSentinel AI — Auto-Fix Summary

## 🔧 Fix Status & Metrics
- Validation Status: {fix_status}
- Test Pass Rate: [original]% → [new]%
- Sentinel Style Score: [original]/100 → [new]/100

## ✅ Corrections Applied
[List each fixed bug or style issue with a brief explanation]

## 📝 Corrected Source Code
```
{code_fixes}
```

## 💡 Engineering Insights & Best Practices
[Brief explanation of key improvements made]

Be sure to execute `save_fix_report` tool before delivering output."""

    return await instructions_utils.inject_session_state(template, context)


fix_synthesizer_agent = Agent(
    name="FixSynthesizer",
    model=config.critic_model,
    description="Formats the complete CodeSentinel AI auto-fix summary report.",
    instruction=fix_synthesizer_instruction_provider,
    tools=[FunctionTool(func=save_fix_report)],
    output_key="fix_summary"
)
