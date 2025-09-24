import os
import json
from typing import List

USE_LLM = os.environ.get("USE_LLM", "0").lower() in ("1", "true", "yes")


def _heuristic_summarize(logs: List[str]) -> str:
    if not logs:
        return ""
    # simple heuristic: return the most frequent error-like lines or join first 3 lines
    errors = [l for l in logs if "error" in l.lower() or "fail" in l.lower()]
    candidates = errors or logs
    summary = "; ".join(candidates[:3])
    if len(summary) > 400:
        summary = summary[:397] + "..."
    return summary


def _llm_summarize(logs: List[str]) -> str:
    try:
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain import LLMChain
            from langchain.prompts import PromptTemplate
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        except Exception:
            from langchain import OpenAI
            from langchain import LLMChain
            from langchain.prompts import PromptTemplate
            llm = OpenAI(temperature=0)

        # load prompt from config if present
        template_text = None
        try:
            cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "prompt_config.json")
            cfg_path = os.path.abspath(cfg_path)
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                template_text = cfg.get("log_summary_prompt")
        except Exception:
            template_text = None

        if not template_text:
            template_text = (
                "请将下面的日志按要点总结成一句话中文摘要（简短）：\n\n{logs}\n\n只需输出一句话摘要。"
            )

        prompt = PromptTemplate(input_variables=["logs"], template=template_text)
        chain = LLMChain(llm=llm, prompt=prompt)
        resp = chain.run(logs="\n".join(logs))
        return resp.strip()
    except Exception:
        return _heuristic_summarize(logs)


def summarize_logs(logs: List[str]) -> str:
    if not logs:
        return ""
    if USE_LLM and os.environ.get("OPENAI_API_KEY"):
        return _llm_summarize(logs)
    return _heuristic_summarize(logs)
