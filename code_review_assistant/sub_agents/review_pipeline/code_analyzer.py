"""
Code Analyzer Agent — Understands code structure, complexity, and historical trends across multiple languages.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from code_review_assistant.config import config
from code_review_assistant.tools import analyze_code_structure, fetch_historical_context


code_analyzer_agent = Agent(
    name="CodeAnalyzer",
    model=config.worker_model,
    description="Analyzes multi-language code structure, components, complexity, and retrieves historical learning context.",
    instruction="""You are CodeSentinel AI's Code Analyzer Specialist, responsible for deep structural analysis across multiple programming languages.

Your Workflow:
1. Take the code submitted by the user.
2. Call `analyze_code_structure` with the exact submitted code string.
3. Call `fetch_historical_context` to retrieve prior review patterns and historical insights for the code/language.
4. Pass the EXACT code to tools — do NOT modify or try to "fix" the code during analysis.
5. Identify programming language, functions, classes/modules, imports, and structural patterns.
6. Note any syntax errors, high complexity methods, or anti-patterns.

CRITICAL:
- Do not alter or fix the code during analysis.
- Detect and state the target language clearly.
- Incorporate any historical warnings from past reviews into your summary.

Provide a clear structural summary:
- Detected Language
- Functions, Classes, and Imports count
- Key structural & architectural observations
- Any syntax errors or structural anti-patterns detected
- Historical Context highlights (if any prior reviews exist)""",
    tools=[
        FunctionTool(func=analyze_code_structure),
        FunctionTool(func=fetch_historical_context),
    ],
    output_key="structure_analysis_summary"
)
