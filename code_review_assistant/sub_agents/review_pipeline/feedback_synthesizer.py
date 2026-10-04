"""
Feedback Synthesizer Agent — Synthesizes analysis, style, test results, and historical learning into comprehensive feedback.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from google.adk.utils import instructions_utils
from code_review_assistant.config import config
from code_review_assistant.tools import search_past_feedback, update_grading_progress, save_grading_report


async def feedback_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamic instruction provider injecting structural, style, test, and historical context."""
    template = """You are CodeSentinel AI's Senior Code Reviewer and Lead Architect.

CONSOLIDATED INPUTS FROM PIPELINE AGENTS:
- Structure Analysis: {structure_analysis_summary}
- Style Check: {style_check_summary}  
- Test Execution: {test_execution_summary}

REQUIRED TOOL EXECUTION ORDER:
1. Call `search_past_feedback` with developer_id="default_user"
2. Call `update_grading_progress`
3. Analyze all findings, test results, and style scores carefully
4. Generate comprehensive CodeSentinel AI Review Feedback following the structure below
5. Call `save_grading_report` passing your generated feedback_text
6. Return the feedback text as your final agent output

OUTPUT FORMAT:

# 🛡️ CodeSentinel AI — Review & Security Audit Report

## 📊 Quality Summary & Sentinel Score
- Overall Sentinel Score: [0-100]
- Security & Vulnerability Rating: [Low | Medium | High Risk]
- Automated Test Pass Rate: [Pass %]

## ✅ Key Strengths
- 2-3 specific engineering strengths observed in the submission.

## 📈 Detailed Component Analysis
### 🏗️ Code Structure & Architecture
Key architectural, modularity, and readability insights.

### 🎨 Style & Standards Compliance
Detailed score breakdown and formatting notes.

### 🧪 Automated Testing & Sandbox Results
Detailed test execution breakdown, critical bugs, edge case handling.

## 💡 Prioritized Recommendations
Numbered list of actionable improvements from highest to lowest severity.

## 🎯 Next Steps
Actionable plan for the developer.

Remember: Complete ALL required tool calls including `save_grading_report`."""

    return await instructions_utils.inject_session_state(template, context)


feedback_synthesizer_agent = Agent(
    name="FeedbackSynthesizer",
    model=config.critic_model,
    description="Synthesizes code review results into a structured CodeSentinel AI audit report.",
    instruction=feedback_instruction_provider,
    tools=[
        FunctionTool(func=search_past_feedback),
        FunctionTool(func=update_grading_progress),
        FunctionTool(func=save_grading_report)
    ],
    output_key="final_feedback"
)
