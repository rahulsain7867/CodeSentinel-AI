# code_review_assistant/__init__.py
"""
CodeSentinel AI — 24/7 Intelligent Code Reviewer

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)

An AI-powered multi-agent system for comprehensive code review,
quality scoring, historical learning, and automated fixes.
"""

from .agent import root_agent

__all__ = ["root_agent"]
