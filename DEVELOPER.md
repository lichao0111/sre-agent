# 开发者快速启动

Prerequisites:

- Python 3.10+ (建议)

安装依赖：

```bash
**开发者快速启动**

- **Prerequisite**: `Python 3.10+`。

- **Install**: 创建并激活虚拟环境，然后安装依赖。
	```bash
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	```

- **Run**: 使用 `uvicorn` 启动开发服务器（已配置自动重载）。
	```bash
	uvicorn sre_agent.app.main:app --reload --port 8000
	```

- **Test**: 运行单元测试。
	```bash
	pytest -q
	```

**项目目录概览**

- **`sre_agent/app`**: 应用入口与路由。
- **`sre_agent/core`**: 业务核心逻辑（如抽取器 `extractor.py`、规则引擎 `rules.py`）。
- **`sre_agent/integrations`**: 外部适配器（`log_adapter.py`、`chatops.py`）。
- **`sre_agent/config`**: 可编辑配置（如 `prompt_config.json`），用于存放 LLM 提示模板等。
- **`tests/`**: 单元测试。

此外，为兼容旧导入路径，仓库根下保留了若干 shim 文件（例如 `sre_agent/extractor.py`），它们会将导入转发到新的模块位置，短期内可确保向后兼容。

**LLM（LangChain + OpenAI）配置**

- **配置文件**: `sre_agent/config/prompt_config.json` —— 编辑 `llm_prompt` 来修改提示模板，模板中使用 `{text}` 占位替换告警原文。
- **启用方法**:
	- 在环境中设置 `OPENAI_API_KEY`（或写入 `.env`）：
		```bash
		echo "OPENAI_API_KEY=sk-..." > .env
		export OPENAI_API_KEY=sk-...
		```
	- 启用 LLM 路径：
		```bash
		export USE_LLM=1
		```
	- 重启服务以加载新的环境与配置。

- **注意**: LLM 调用会产生网络请求与计费，请在生产环境中做好配额与审计控制。

**如何修改提示模板**

- 编辑 `sre_agent/config/prompt_config.json` 中的 `llm_prompt`，例如：
	```json
	{
		"llm_prompt": "从以下文本抽取字段并返回 JSON：{text}",
		"fields": ["request_id","service_name","summary"]
	}
	```
- 修改后重启服务使配置生效。

**兼容性说明**

- 在本次重构中，核心实现已移动到 `core`/`integrations`/`app` 等子包中。
- 为避免一次性破坏所有现有导入，保留了小型兼容 shim（在 `sre_agent/` 下），这些 shim 只是简单地从新位置重新导出函数/对象。建议后续代码与新路径一致地引用模块（例如 `from sre_agent.core.extractor import extract_event`）。

**后续建议**

- 使用 pydantic 为 LLM 输出做 schema 验证并规范化字段。
- 增加 admin 接口以便在运行时预览/验证 prompt（需鉴权）。
- 用真实的日志系统（Elasticsearch/Loki）替换 `integrations/log_adapter.py` 的 stub 实现。

若你要我实施以上某一条（例如添加 pydantic 验证或 admin 热加载端点），告诉我你优先的选项，我会继续实现。
```

修改后，重启服务使配置生效。
