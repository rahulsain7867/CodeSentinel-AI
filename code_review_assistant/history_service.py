"""
Historical Learning and Persistence Service for CodeSentinel AI.

Author: Rahul Sain
Based on: Code Review Assistant by Ayo Adedeji (Apache-2.0)

This module provides persistent storage and historical pattern learning using
Google Cloud Firestore, with an automatic in-memory / JSON-backed fallback
for local development when GCP Firestore is not available.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from code_review_assistant.config import config

logger = logging.getLogger(__name__)

# Fallback file path for local persistence without GCP Firestore
LOCAL_STORAGE_FILE = ".code_sentinel_history.json"


class HistoryService:
    """
    Manages review history, pattern analytics, and historical context retrieval.
    Uses Google Cloud Firestore when available, falling back to local JSON storage.
    """

    def __init__(self, collection_name: str = "codesentinel_reviews"):
        self.collection_name = collection_name
        firestore_flag = os.getenv("FIRESTORE_ENABLED")
        if firestore_flag is not None:
            self.use_firestore = firestore_flag.strip().lower() in {"1", "true", "yes", "on"}
        else:
            self.use_firestore = bool(getattr(config, "google_cloud_project", None))
        self.db = None
        self._local_cache: List[Dict[str, Any]] = []

        if self.use_firestore:
            try:
                from google.cloud import firestore

                project_id = getattr(config, "google_cloud_project", None) or None
                self.db = firestore.Client(project=project_id)
                logger.info(f"Initialized Firestore client for project: {project_id or 'default'}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Firestore ({e}). Falling back to local persistent storage."
                )
                self.use_firestore = False

        if not self.use_firestore:
            self._load_local_storage()

    def _load_local_storage(self) -> None:
        """Loads historical records from local JSON file if present."""
        if os.path.exists(LOCAL_STORAGE_FILE):
            try:
                with open(LOCAL_STORAGE_FILE, "r", encoding="utf-8") as f:
                    self._local_cache = json.load(f)
                logger.info(f"Loaded {len(self._local_cache)} local history records.")
            except Exception as e:
                logger.error(f"Error reading local history file ({e}). Starting fresh.")
                self._local_cache = []
        else:
            self._local_cache = []

    def _save_local_storage(self) -> None:
        """Saves current history records to local JSON file."""
        try:
            with open(LOCAL_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._local_cache, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save local history: {e}")

    def save_review_record(
        self,
        code_snippet: str,
        filename: str = "code_snippet.py",
        language: str = "python",
        summary: str = "",
        quality_score: float = 100.0,
        issues_found: Optional[List[Dict[str, Any]]] = None,
        severity_counts: Optional[Dict[str, int]] = None,
        fixed_code: Optional[str] = None,
        fixes_applied: Optional[List[str]] = None,
        author: str = "Rahul Sain",
    ) -> Dict[str, Any]:
        """
        Saves a completed code review record to Firestore / local store.
        """
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        record = {
            "id": record_id,
            "timestamp": now_iso,
            "filename": filename,
            "language": language,
            "code_length": len(code_snippet),
            "summary": summary,
            "quality_score": round(quality_score, 1),
            "issues_found": issues_found or [],
            "severity_counts": severity_counts or {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "fixed_code": fixed_code or "",
            "fixes_applied": fixes_applied or [],
            "author": author,
            "version": "1.0.0",
        }

        if self.use_firestore and self.db:
            try:
                self.db.collection(self.collection_name).document(record_id).set(record)
                logger.info(f"Saved review record {record_id} to Firestore.")
            except Exception as e:
                logger.error(f"Firestore save failed ({e}), saving to local cache.")
                self._local_cache.append(record)
                self._save_local_storage()
        else:
            self._local_cache.append(record)
            self._save_local_storage()
            logger.info(f"Saved review record {record_id} to local storage.")

        return record

    def get_review_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent review records sorted by timestamp descending."""
        if self.use_firestore and self.db:
            try:
                docs = (
                    self.db.collection(self.collection_name)
                    .order_by("timestamp", direction="DESCENDING")
                    .limit(limit)
                    .stream()
                )
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Failed to fetch history from Firestore ({e}). Using local cache.")
                return sorted(self._local_cache, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

        return sorted(self._local_cache, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

    def get_historical_context(
        self, filename: Optional[str] = None, language: Optional[str] = None, limit: int = 10
    ) -> str:
        """
        Retrieves historical learning context to inform new reviews.
        Synthesizes recurring issues, average quality scores, and past fixes.
        """
        history = self.get_review_history(limit=50)

        matching = []
        for r in history:
            if filename and r.get("filename") == filename:
                matching.append(r)
            elif language and r.get("language", "").lower() == language.lower():
                matching.append(r)

        if not matching:
            matching = history[:limit]

        if not matching:
            return "No historical review data available yet for context."

        total_reviews = len(matching)
        avg_score = sum(r.get("quality_score", 100) for r in matching) / total_reviews

        recurring_issues: List[str] = []
        past_fixes: List[str] = []

        for r in matching:
            for issue in r.get("issues_found", []):
                if isinstance(issue, dict):
                    msg = issue.get("message") or issue.get("description")
                    if msg:
                        recurring_issues.append(msg)
                elif isinstance(issue, str):
                    recurring_issues.append(issue)

            for fix in r.get("fixes_applied", []):
                past_fixes.append(str(fix))

        context_lines = [
            f"--- HISTORICAL LEARNING CONTEXT ({total_reviews} prior reviews analyzed) ---",
            f"Average Quality Score in prior runs: {avg_score:.1f}/100",
        ]

        if recurring_issues:
            context_lines.append("Frequent Issues in Past Reviews:")
            for issue in recurring_issues[:5]:
                context_lines.append(f"  • {issue}")

        if past_fixes:
            context_lines.append("Successful Fix Patterns Applied Previously:")
            for fix in past_fixes[:5]:
                context_lines.append(f"  • {fix}")

        return "\n".join(context_lines)

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Calculates aggregated metrics and analytics for the web dashboard."""
        records = self.get_review_history(limit=200)

        total_reviews = len(records)
        if total_reviews == 0:
            return {
                "total_reviews": 0,
                "avg_quality_score": 100.0,
                "total_issues_found": 0,
                "total_fixes_applied": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "language_breakdown": {},
                "recent_reviews": [],
            }

        avg_score = sum(r.get("quality_score", 100) for r in records) / total_reviews
        total_issues = sum(len(r.get("issues_found", [])) for r in records)
        total_fixes = sum(len(r.get("fixes_applied", [])) for r in records)

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        language_counts: Dict[str, int] = {}

        for r in records:
            sev = r.get("severity_counts", {})
            if isinstance(sev, dict):
                for k, v in sev.items():
                    severity_counts[k] = severity_counts.get(k, 0) + int(v)

            lang = r.get("language", "python").capitalize()
            language_counts[lang] = language_counts.get(lang, 0) + 1

        return {
            "total_reviews": total_reviews,
            "avg_quality_score": round(avg_score, 1),
            "total_issues_found": total_issues,
            "total_fixes_applied": total_fixes,
            "severity_breakdown": severity_counts,
            "language_breakdown": language_counts,
            "recent_reviews": records[:10],
        }

    def get_quality_trend(self, limit: int = 30) -> Dict[str, Any]:
        """Returns score trend data for charting."""
        records = self.get_review_history(limit=limit)
        trend_points = [
            {
                "timestamp": record.get("timestamp"),
                "quality_score": record.get("quality_score", 100.0),
            }
            for record in reversed(records)
        ]
        return {
            "points": trend_points,
            "count": len(trend_points),
        }

    def get_recurring_issues(self, limit: int = 10) -> Dict[str, Any]:
        """Returns most frequent issue messages from recent history."""
        issue_counts: Dict[str, int] = {}
        for record in self.get_review_history(limit=200):
            for issue in record.get("issues_found", []):
                if isinstance(issue, dict):
                    text = issue.get("message") or issue.get("description") or ""
                else:
                    text = str(issue)
                text = text.strip()
                if text:
                    issue_counts[text] = issue_counts.get(text, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)[:limit]
        return {
            "items": [{"issue": issue, "count": count} for issue, count in top_issues],
            "count": len(top_issues),
        }

    def clear_history(self) -> bool:
        """Clears local cache and file for testing/reset."""
        self._local_cache = []
        if os.path.exists(LOCAL_STORAGE_FILE):
            try:
                os.remove(LOCAL_STORAGE_FILE)
            except Exception as e:
                logger.error(f"Error removing local history file: {e}")
        return True


# Global singleton instance
history_service = HistoryService()
ReviewHistoryService = HistoryService
