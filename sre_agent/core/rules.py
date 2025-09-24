from typing import Dict, List


RULES = [
    {"pattern": "database timeout", "diagnosis": "DB_TIMEOUT", "suggestion": "检查数据库连接与慢查询，考虑增加连接池或优化查询。"},
    {"pattern": "out of memory|oom", "diagnosis": "OOM", "suggestion": "检查内存使用，增加内存或优化内存分配；排查内存泄漏。"},
    {"pattern": "connection pool", "diagnosis": "CONN_POOL_EXHAUSTED", "suggestion": "检查连接池配置与外部依赖响应时间，考虑扩容或降级策略。"},
]


def diagnose(structured: Dict[str, str], logs: List[str]) -> Dict[str, str]:
    text = "\n".join(logs) + "\n" + (structured.get("summary") or "")
    for r in RULES:
        if r["pattern"] in text.lower():
            return {"diagnosis": r["diagnosis"], "suggestion": r["suggestion"]}

    return {"diagnosis": "UNKNOWN", "suggestion": "请人工查阅日志并执行进一步诊断。"}
