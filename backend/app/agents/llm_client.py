import os
import json
import httpx
from typing import List, Dict, Any, Optional

class LLMClient:
    """
    Unified LLM Client interfacing with Google Gemini, Anthropic Claude Sonnet, and OpenAI GPT-4o.
    Outputs strictly formatted JSON finding arrays for Security, Performance, and Style agents.
    """
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    async def invoke_agent_llm(
        self,
        agent_type: str, # security / performance / style
        system_prompt: str,
        code_chunk: str,
        file_path: str,
        start_line: int,
        rag_context: List[str] = []
    ) -> Optional[List[Dict[str, Any]]]:
        context_str = "\n".join(rag_context) if rag_context else "No extra repository guidelines retrieved."

        user_prompt = f"""Target File: {file_path} (Starting Line: {start_line})
Repository RAG Context:
{context_str}

Code Chunk to Analyze:
```
{code_chunk}
```

Respond ONLY with a JSON array of finding objects matching this exact schema:
[
  {{
    "agent": "{agent_type}",
    "file_path": "{file_path}",
    "line_start": {start_line},
    "line_end": {start_line + 5},
    "severity": "low|medium|high|critical",
    "cvss_score": 8.5 (optional, security only),
    "cvss_vector": "CVSS:3.1/..." (optional, security only),
    "complexity_estimate": "O(n^2)" (optional, performance only),
    "description": "Clear explanation of the flaw",
    "suggested_fix": "Concrete remediation snippet"
  }}
]
If no issues are found, return an empty JSON array: [].
Do not include any conversational preamble or markdown codeblock wrappers outside the JSON array.
"""

        # 1. Try Google Gemini API if GEMINI_API_KEY is set
        if self.gemini_key and "your_" not in self.gemini_key and len(self.gemini_key) > 10:
            try:
                res = await self._call_gemini(system_prompt, user_prompt)
                if res is not None:
                    return res
            except Exception as e:
                print(f"[LLMClient Warning] Gemini API call failed: {e}")

        # 2. Try Anthropic Claude API if key is present
        if self.anthropic_key and "your_" not in self.anthropic_key and len(self.anthropic_key) > 10:
            try:
                res = await self._call_anthropic(system_prompt, user_prompt)
                if res is not None:
                    return res
            except Exception as e:
                print(f"[LLMClient Warning] Anthropic API call failed: {e}")

        # 3. Try OpenAI GPT-4o API if key is present
        if self.openai_key and "your_" not in self.openai_key and len(self.openai_key) > 10:
            try:
                res = await self._call_openai(system_prompt, user_prompt)
                if res is not None:
                    return res
            except Exception as e:
                print(f"[LLMClient Warning] OpenAI API call failed: {e}")

        return None

    async def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[List[Dict[str, Any]]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Instructions: {system_prompt}\n\nTask: {user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return self._parse_json_response(text)
            else:
                print(f"[LLMClient Error] Gemini HTTP {resp.status_code}: {resp.text}")
        return None

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Optional[List[Dict[str, Any]]]:
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["content"][0]["text"].strip()
                return self._parse_json_response(text)
        return None

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> Optional[List[Dict[str, Any]]]:
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"].strip()
                return self._parse_json_response(text)
        return None

    def _parse_json_response(self, text: str) -> Optional[List[Dict[str, Any]]]:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return None
