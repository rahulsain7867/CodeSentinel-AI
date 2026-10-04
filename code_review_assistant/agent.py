"""
Main agent orchestration for CodeSentinel AI — 24/7 Intelligent Code Reviewer.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)

This module defines the root agent and multi-stage review/fix pipelines using
Google ADK (Agent Development Kit) with multi-language and historical learning capabilities.
"""

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from .config import config
from .sub_agents import (
    code_analyzer_agent,
    style_checker_agent,
    test_runner_agent,
    feedback_synthesizer_agent,
    code_fixer_agent,
    fix_test_runner_agent,
    fix_validator_agent,
    fix_synthesizer_agent
)

# --- Code Review Pipeline Sub-Agent ---
code_review_pipeline = SequentialAgent(
    name="CodeReviewPipeline",
    description="Complete multi-language code review pipeline with structure analysis, style check, automated testing, and feedback synthesis",
    sub_agents=[
        code_analyzer_agent,
        style_checker_agent,
        test_runner_agent,
        feedback_synthesizer_agent
    ]
)

# --- Fix Attempt Loop ---
fix_attempt_loop = LoopAgent(
    name="FixAttemptLoop",
    sub_agents=[
        code_fixer_agent,
        fix_test_runner_agent,
        fix_validator_agent
    ],
    max_iterations=3  # Try up to 3 times to get a successful fix
)

# --- Code Fix Pipeline Sub-Agent ---
code_fix_pipeline = SequentialAgent(
    name="CodeFixPipeline",
    description="Automated code fixing pipeline with iterative validation and quality score verification",
    sub_agents=[
        fix_attempt_loop,      # Try to fix (up to 3 times)
        fix_synthesizer_agent  # Present final results
    ]
)

# --- Main CodeSentinel AI Root Agent ---
root_agent = Agent(
    name="CodeSentinelAI",
    model=config.worker_model,
    description="CodeSentinel AI — 24/7 Intelligent Code Reviewer providing automated code analysis, multi-language support, security audit, and auto-fixing.",
    instruction="""You are CodeSentinel AI, an advanced 24/7 intelligent code reviewer developed by Rahul Sain.

Capabilities & Scope:
- Multi-language code review (Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, HTML/CSS, SQL, Shell, etc.).
- Deep structural & AST analysis (Python) and intelligent AI analysis (all supported languages).
- Automated PEP 8 / linting style check and security vulnerability identification.
- Automated test generation and execution validation.
- Historical learning: cross-referencing past review findings and pattern trends.
- Automated 1-click code fixing with quality verification.

Routing Instructions:
1. When a user provides code or requests a code review:
   - Pass the code EXACTLY as provided into the `CodeReviewPipeline`.
   - The pipeline handles structural analysis, style, testing, historical context, and score synthesis.
   - Return the complete final output from the pipeline verbatim.

2. After review feedback, if quality score < 100 or bugs/style issues are present:
   - Append at the very bottom: "\n\n⚡ **CodeSentinel Sentinel Auto-Fix Available**: Would you like me to automatically fix these issues for you?"

3. If the user requests a fix or responds yes:
   - Delegate to `CodeFixPipeline`.
   - Return the fix pipeline's final output verbatim.

4. For general questions or capability inquiries:
   - Introduce yourself as CodeSentinel AI (developed by Rahul Sain).
   - Explain your review, multi-language, security audit, historical learning, and auto-fix capabilities cleanly.
   - Do NOT invoke the pipeline unless actual code or review request is provided.""",
    sub_agents=[code_review_pipeline, code_fix_pipeline],
    output_key="assistant_response"
)
