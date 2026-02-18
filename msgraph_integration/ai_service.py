"""
Company Assistant AI Service
Integrates Groq (Llama 4 Scout) to synthesize search results into natural language answers.
Groq API docs: https://console.groq.com/docs/openai
Set the GROQ_API_KEY environment variable with a key from https://console.groq.com/keys
"""
import os
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI


class CompanyAssistantService:
    """
    Three-stage pipeline:
      1. Extract search keywords from user's natural language question
      2. Search across company data sources (SharePoint, Teams, Email)
      3. Synthesize results into a cited English-language answer
    """

    # Groq model — fast, cheap, strong at RAG synthesis.
    # Alternatives: "llama-3.3-70b-versatile", "qwen-qwen3-32b"
    # MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    MODEL = "llama-3.3-70b-versatile"
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1"

    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Get a free key at https://console.groq.com/keys"
            )

        self.client = OpenAI(
            base_url=self.GROQ_ENDPOINT,
            api_key=groq_api_key,
        )

        # Load static company grounding context (edit company_context.md to update)
        context_file = Path(__file__).parent / "company_context.md"
        self.company_context = context_file.read_text(encoding="utf-8") if context_file.exists() else ""

        # Extract company name for use in keyword extraction prompt
        import re
        match = re.search(r'\*\*Company name\*\*:\s*([^\n(]+)', self.company_context)
        self.company_name = match.group(1).strip() if match else "our company"

    # ------------------------------------------------------------------
    # Stage 1: Keyword extraction
    # ------------------------------------------------------------------

    def extract_search_keywords(self, question: str) -> str:
        """
        Use the configured model to convert a natural language question into a
        concise search query string suitable for Microsoft Graph Search.
        """
        response = self.client.chat.completions.create(
            model=self.MODEL,
            temperature=0,
            max_tokens=60,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You extract search keywords from questions. "
                        "Return ONLY a short search query string (no explanation, no punctuation) "
                        "that would find relevant documents in a corporate Microsoft 365 environment. "
                        "2-6 words maximum."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Stage 2: Search (called externally, results passed back in)
    # ------------------------------------------------------------------

    def flatten_hits(self, search_data: dict) -> list[dict]:
        """
        Flatten the Microsoft Search API hitsContainers structure
        into a simple list of hit dicts.
        """
        hits = []
        for request_result in search_data.get("value", []):
            for container in request_result.get("hitsContainers", []):
                for hit in container.get("hits", []):
                    hits.append(hit)
        return hits

    def build_context_from_results(
        self,
        sharepoint_data: Optional[dict],
        teams_data: Optional[dict],
        email_data: Optional[dict],
    ) -> tuple[str, list[dict]]:
        """
        Convert raw search results into:
          - a text context block for the LLM prompt
          - a sources list for the UI (used to render footnotes)

        Returns:
          context_text (str): Formatted text block passed to the LLM
          sources (list):      List of source dicts with index, title, url, type
        """
        sources = []
        context_lines = []

        def add_hits(hits: list[dict], source_type: str):
            for hit in hits:
                resource = hit.get("resource", {})
                summary = hit.get("summary", "").strip()

                if source_type == "sharepoint":
                    title = (
                        resource.get("name")
                        or resource.get("title")
                        or resource.get("displayName")
                        or "Untitled"
                    )
                    url = resource.get("webUrl", "")
                    modified_by = (
                        resource.get("lastModifiedBy", {})
                        .get("user", {})
                        .get("displayName", "")
                    )
                    date = resource.get("lastModifiedDateTime", "")
                    snippet = summary or f"Modified by {modified_by} on {date[:10]}" if modified_by else summary

                elif source_type == "teams":
                    sender = (
                        resource.get("from", {}).get("user", {}).get("displayName")
                        or resource.get("from", {}).get("emailAddress", {}).get("name")
                        or "Unknown"
                    )
                    subject = resource.get("subject") or "Teams message"
                    title = f"{sender}: {subject}"
                    url = resource.get("webLink") or resource.get("webUrl", "")
                    date = resource.get("createdDateTime", "")
                    snippet = summary or f"Teams message from {sender}"

                elif source_type == "email":
                    sender = resource.get("from", {}).get("emailAddress", {}).get("name", "Unknown")
                    title = resource.get("subject") or "Email"
                    url = resource.get("webLink", "")
                    date = resource.get("receivedDateTime", "")
                    snippet = summary or f"Email from {sender}"

                else:
                    continue

                idx = len(sources) + 1
                sources.append(
                    {
                        "index": idx,
                        "title": title,
                        "url": url,
                        "type": source_type,
                        "date": date[:10] if date else "",
                    }
                )

                context_lines.append(
                    f"[{idx}] ({source_type.upper()}) {title}\n{snippet}\n"
                )

        if sharepoint_data:
            add_hits(self.flatten_hits(sharepoint_data), "sharepoint")
        if teams_data:
            add_hits(self.flatten_hits(teams_data), "teams")
        if email_data:
            add_hits(self.flatten_hits(email_data), "email")

        context_text = "\n".join(context_lines)
        return context_text, sources

    # ------------------------------------------------------------------
    # Stage 3: Answer synthesis
    # ------------------------------------------------------------------

    def synthesize_answer(
        self,
        question: str,
        context_text: str,
        conversation_history: Optional[list] = None,
    ) -> str:
        """
        Use the configured model to generate a natural language answer grounded
        in the provided context. Returns the plain-text answer with [n] citations.
        """
        company_section = (
            f"\n\n## Company Background\n{self.company_context}\n"
            if self.company_context
            else ""
        )
        system_prompt = (
            "You are a helpful company assistant for Integral Methods. "
            "Answer the user's question using the company background below and/or "
            "the numbered search sources provided with each question. "
            "For facts from the company background, no citation is needed. "
            "For facts from search sources, cite inline using [1], [2] etc. "
            "If multiple sources support a point, cite all relevant ones. "
            "If neither the background nor the sources contain enough information, say so clearly — "
            "do not invent or infer facts not present in either. "
            "Be concise but thorough. Use plain English."
            + company_section
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Include prior turns for conversational context
        if conversation_history:
            messages.extend(conversation_history)

        # Append the current question with its retrieved context
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Sources:\n{context_text if context_text else '(No results found)'}"
                ),
            }
        )

        response = self.client.chat.completions.create(
            model=self.MODEL,
            temperature=0.2,
            max_tokens=800,
            messages=messages,
        )

        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def chat(
        self,
        question: str,
        sharepoint_data: Optional[dict] = None,
        teams_data: Optional[dict] = None,
        email_data: Optional[dict] = None,
        conversation_history: Optional[list] = None,
    ) -> dict:
        """
        Full pipeline: build context from search data and generate answer.

        Args:
            question:             The user's natural language question
            sharepoint_data:      Raw result from /api/search/global/
            teams_data:           Raw result from /api/search/teams/
            email_data:           Raw result from /api/search/email/
            conversation_history: List of prior {role, content} dicts for multi-turn

        Returns:
            {
                "answer": str,               # Natural language answer with [n] citations
                "keywords": str,             # Extracted search keywords (for debugging)
                "sources": list[dict],       # Source list for footnote rendering
            }
        """
        context_text, sources = self.build_context_from_results(
            sharepoint_data, teams_data, email_data
        )

        answer = self.synthesize_answer(question, context_text, conversation_history)

        return {
            "answer": answer,
            "sources": sources,
        }
