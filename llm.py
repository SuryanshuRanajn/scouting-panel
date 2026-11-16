"""Thin Semantic Kernel wrapper around Gemini. Needs: pip install "semantic-kernel[google]"
and the environment variable GEMINI_API_KEY. Model can be changed with GEMINI_MODEL."""
import asyncio, json, os, re, time
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
async def _ask(system, user):
    from semantic_kernel.connectors.ai.google.google_ai import (GoogleAIChatCompletion,
                                                                GoogleAIChatPromptExecutionSettings)
    from semantic_kernel.contents import ChatHistory
    key = os.environ.get("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY is not set")
    chat = GoogleAIChatCompletion(gemini_model_id=MODEL, api_key=key)
    h = ChatHistory(); h.add_system_message(system); h.add_user_message(user)
    r = await chat.get_chat_message_content(h, GoogleAIChatPromptExecutionSettings(temperature=0.0))
    return str(r)
def ask_json(system, user, retries=4):
    last = None
    for i in range(retries):
        try:
            text = asyncio.run(_ask(system, user)).strip()
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
            return json.loads(text)
        except Exception as e:           # rate limit (429), bad JSON, network...
            last = e; print(f"   LLM call failed ({type(e).__name__}); retry {i+1}/{retries}")
            time.sleep(8*(i+1))
    raise RuntimeError(f"LLM failed after {retries} tries: {last}")
