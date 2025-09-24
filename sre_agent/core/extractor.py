import re
import os
import json
from typing import Dict, Optional

USE_LLM = os.environ.get("USE_LLM", "0").lower() in ("1", "true", "yes")


def _heuristic_extract(raw: str) -> Optional[Dict[str, str]]:
    request_match = re.search(r"request[_-]?id[:= ]*([A-Za-z0-9-]+)", raw, re.I)
    service_match = re.search(r"service[:= ]*([A-Za-z0-9._-]+)", raw, re.I)
    summary_match = re.search(r"error[:= ]*(.+)$", raw, re.I)

    result = {}
    if request_match:
        result["request_id"] = request_match.group(1)
    if service_match:
        result["service_name"] = service_match.group(1)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()

    # fallback: if nothing extracted, try split
    if not result and raw:
        parts = raw.split("|")
        if len(parts) >= 2:
            result["service_name"] = parts[0].strip()
            result["summary"] = parts[1].strip()

    return result or None


def _llm_extract(raw: str) -> Optional[Dict[str, str]]:
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

        # Load prompt template from configuration file if available
        template_text = None
        try:
            cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "prompt_config.json")
            cfg_path = os.path.abspath(cfg_path)
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                template_text = cfg.get("llm_prompt")
        except Exception:
            template_text = None

        if not template_text:
            template_text = (
                "从以下原始告警文本中抽取结构化字段。仅输出一个 JSON，包含可选字段："
                "request_id, service_name, summary。若缺失字段请设为 null。\n\n文本:\n{text}\n\n"
                "示例输出：{\"request_id\": \"abc-123\", \"service_name\": \"auth\", \"summary\": \"数据库超时\"}"
            )

        prompt = PromptTemplate(input_variables=["text"], template=template_text)
        chain = LLMChain(llm=llm, prompt=prompt)
        resp = chain.run(text=raw)

        json_text = resp.strip()
        if "{" in json_text:
            start = json_text.find("{")
            end = json_text.rfind("}")
            json_text = json_text[start : end + 1]

        data = json.loads(json_text)
        return {k: (v if v != "" else None) for k, v in data.items()}
    except Exception:
        return None


def extract_event(raw: str) -> Optional[Dict[str, str]]:
    raw = raw or ""
    if USE_LLM and os.environ.get("OPENAI_API_KEY"):
        llm_result = _llm_extract(raw)
        if llm_result:
            return llm_result

    return _heuristic_extract(raw)
