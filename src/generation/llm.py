import os
import re
import time

from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5-5",
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.5-flash",
}
KEY_NAMES = {
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


class LLMError(Exception):
    """Raised with a user-friendly message when the LLM call fails."""


def _pick_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()
    if provider:
        if provider not in KEY_NAMES:
            raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use: {', '.join(KEY_NAMES)}.")
        return provider
    for name, env in KEY_NAMES.items():
        if os.getenv(env):
            return name
    raise LLMError("No API key found. Add ANTHROPIC_API_KEY, GROQ_API_KEY, or GEMINI_API_KEY to .env.")


class LLMClient:
    """Provider-agnostic wrapper. The rest of the app only calls .complete()."""

    def __init__(self, model: str | None = None):
        self.provider = _pick_provider()
        key = os.getenv(KEY_NAMES[self.provider])
        if not key:
            raise LLMError(f"{KEY_NAMES[self.provider]} is not set. Add it to .env (or Space secrets).")
        self.model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS[self.provider]

        if self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=key)
        elif self.provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=key)
        else:
            from google import genai
            self.client = genai.Client(api_key=key)

    def complete(self, system: str, messages: list[dict], max_tokens: int = 1500, retries: int = 5) -> str:
        """Call the model, retrying on rate limits and waiting as long as the API asks."""
        for attempt in range(retries):
            try:
                return self._complete_once(system, messages, max_tokens)
            except LLMError as e:
                msg = str(e)
                if attempt < retries - 1 and ("429" in msg or "rate limit" in msg.lower()):
                    wait = min(5 * 2 ** attempt, 60)
                    m = re.search(r"try again in ([\d.]+)(ms|s)\b", msg)
                    if m:
                        wait = float(m.group(1)) / (1000 if m.group(2) == "ms" else 1) + 1
                    time.sleep(wait)
                    continue
                raise

    def _complete_once(self, system: str, messages: list[dict], max_tokens: int = 1500) -> str:
        try:
            if self.provider == "anthropic":
                resp = self.client.messages.create(
                    model=self.model, max_tokens=max_tokens,
                    system=system, messages=messages,
                )
                return "".join(b.text for b in resp.content if b.type == "text").strip()

            if self.provider == "groq":
                resp = self.client.chat.completions.create(
                    model=self.model, max_tokens=max_tokens,
                    messages=[{"role": "system", "content": system}] + messages,
                )
                return (resp.choices[0].message.content or "").strip()

            from google.genai import types
            contents = [
                types.Content(
                    role="model" if m["role"] == "assistant" else "user",
                    parts=[types.Part(text=m["content"])],
                )
                for m in messages
            ]
            resp = self.client.models.generate_content(
                model=self.model, contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system, max_output_tokens=max_tokens,
                ),
            )
            return (resp.text or "").strip()
        except Exception as e:
            raise LLMError(f"The AI request ({self.provider}) failed: {e}")