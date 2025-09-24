from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..core.extractor import extract_event
from ..core.rules import diagnose
from ..integrations.log_adapter import fetch_logs
from ..integrations.chatops import notify
from ..core.llm_utils import summarize_logs

app = FastAPI(title="SRE Intelligent Ticket Agent (MVP)")


class IncomingEvent(BaseModel):
    source: str
    raw: str


@app.post("/webhook/event")
async def receive_event(event: IncomingEvent):
    structured = extract_event(event.raw)
    if not structured:
        raise HTTPException(status_code=400, detail="failed to extract event")

    logs = fetch_logs(structured.get("request_id"))

    # Summarize logs via LLM (if enabled) or heuristic
    log_summary = summarize_logs(logs)

    # include summary in structured data for diagnosis and return
    if log_summary:
        structured["log_summary"] = log_summary

    rc = diagnose(structured, logs)
    # attach the summary to diagnosis for visibility
    rc["log_summary"] = log_summary

    notify(rc)
    return {"status": "accepted", "structured": structured, "diagnosis": rc}
