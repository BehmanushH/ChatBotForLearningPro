"""LLM handler for BanuCode using Hugging Face Inference API."""

import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMHandler:
    """Single-model handler that talks to a real Hugging Face model."""

    def __init__(self) -> None:
        # Use a chat-compatible open model on Hugging Face Router.
        self.model_id = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")
        self.model_name = "Qwen2.5-7B-Instruct"
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.api_token = os.getenv("HF_TOKEN", "").strip()
        self.is_loaded = bool(self.api_token)
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        self.last_usage: dict[str, int] = {}

    def get_model_info(self) -> dict:
        return {
            "name": self.model_name,
            "model_id": self.model_id,
            "is_loaded": self.is_loaded,
            "status": "connected" if self.is_loaded else "missing_token",
        }

    def _build_prompt(self, prompt: str) -> str:
        # Keep for compatibility if needed by non-chat routes.
        system_context = (
            "You are BanuCode, a bilingual programming and employability skills tutor. "
            "Give practical, concise, accurate guidance. Support both English and Dari."
        )
        return f"{system_context}\n\nUser: {prompt}"

    def _extract_text(self, payload: object) -> str:
        if isinstance(payload, list) and payload:
            item = payload[0]
            if isinstance(item, dict):
                text = item.get("generated_text") or item.get("summary_text") or ""
                return text.strip()
            if isinstance(item, str):
                return item.strip()

        if isinstance(payload, dict):
            if "generated_text" in payload and isinstance(payload["generated_text"], str):
                return payload["generated_text"].strip()
            if "error" in payload:
                return ""

        return ""

    def _normalize_response_text(self, text: str) -> str:
        """Clean model output for professional chat display."""
        cleaned = text.strip()

        # Remove common role/control prefixes.
        cleaned = re.sub(r"^\s*(assistant|response)\s*:\s*", "", cleaned, flags=re.IGNORECASE)

        # Remove common markdown emphasis markers while keeping content.
        cleaned = cleaned.replace("**", "")
        cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)

        # Convert markdown list prefixes to a cleaner bullet marker.
        cleaned = re.sub(r"^\s*[-*]\s+", "• ", cleaned, flags=re.MULTILINE)

        # Collapse excessive blank lines.
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()

    def get_last_usage(self) -> dict[str, int]:
        """Return token usage from the latest model call."""
        return dict(self.last_usage)

    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        language: str = "en",
    ) -> str:
        self.last_usage = {}

        if not self.api_token:
            return (
                "⚠️ Missing Hugging Face token. Add `HF_TOKEN=hf_...` in `.env`, then restart app."
            )

        system_context = (
            "You are BanuCode, a bilingual programming and employability skills tutor. "
            "Give practical, concise, accurate guidance. Support both English and Dari."
        )

        body = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": min(max_tokens, 512),
            "temperature": max(0.0, min(temperature, 1.5)),
            "top_p": 0.95,
        }

        try:
            resp = requests.post(self.api_url, headers=self.headers, json=body, timeout=90)

            if resp.status_code == 401:
                return "❌ Unauthorized token. Please regenerate HF token and update `.env`."
            if resp.status_code == 403:
                return "❌ Token has no access to this model. Use a standard read token."
            if resp.status_code == 429:
                return "⏳ Rate limit reached. Wait a bit and retry."
            if resp.status_code == 400:
                try:
                    details = resp.json()
                except Exception:
                    details = resp.text[:300]
                return f"❌ Request rejected by model/API: {details}"

            data = resp.json()

            if isinstance(data, dict) and data.get("error"):
                message = str(data.get("error"))
                if "loading" in message.lower():
                    return "⏳ Model is waking up. Please retry in 20-40 seconds."
                return f"❌ HF API error: {message}"

            # OpenAI-compatible router response shape.
            if isinstance(data, dict) and data.get("choices"):
                first = data["choices"][0]
                message = first.get("message", {})
                text = str(message.get("content", "")).strip()
                usage = data.get("usage", {}) if isinstance(data, dict) else {}
                if isinstance(usage, dict):
                    self.last_usage = {
                        "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                        "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
                        "total_tokens": int(usage.get("total_tokens", 0) or 0),
                    }
            else:
                text = self._extract_text(data)

            if not text:
                return "❌ No text generated by model. Try again."

            return self._normalize_response_text(text)

        except requests.exceptions.Timeout:
            return "⏳ Request timed out. Please retry."
        except requests.exceptions.ConnectionError:
            return "❌ Network connection error while reaching Hugging Face."
        except Exception as exc:
            return f"❌ Unexpected error: {exc}"


_HANDLER: Optional[LLMHandler] = None


def get_llm_handler() -> LLMHandler:
    """Return singleton handler instance."""
    global _HANDLER
    if _HANDLER is None:
        _HANDLER = LLMHandler()
    return _HANDLER


