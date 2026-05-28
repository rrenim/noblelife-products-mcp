import inspect
import json
import keyword
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent
SPEC_FILE = BASE_DIR / "noblelife-products-mcp-descriptor.md"


def load_descriptor(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    # Remove line comments used in the descriptor file.
    cleaned = []
    in_string = False
    escaped = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            cleaned.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            cleaned.append(ch)
            i += 1
            continue

        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue

        cleaned.append(ch)
        i += 1

    cleaned_text = "".join(cleaned)
    cleaned_text = re.sub(r",\s*([}\]])", r"\1", cleaned_text)
    return json.loads(cleaned_text)


SPEC = load_descriptor(SPEC_FILE)
SERVER_NAME = SPEC.get("server", {}).get("name", "noblelife-product-service")
BASE_URL = SPEC.get("server", {}).get("baseUrl", "").rstrip("/")
COMMON_HEADERS = dict(SPEC.get("server", {}).get("commonHeaders", {}))

mcp = FastMCP(
    SERVER_NAME,
    instructions="Read-only MCP server for NobleLife products.",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
)


def _read_env_token() -> str | None:
    return os.getenv("NOBLELIFE_BEARER_TOKEN") or os.getenv("AUTH_TOKEN")


def _resolve_header_value(value: str, args: dict) -> str:
    if not isinstance(value, str):
        return value
    for key, candidate in args.items():
        value = value.replace("{" + key + "}", str(candidate))
    return value


def _build_request(tool: dict, args: dict):
    http_cfg = tool.get("http", {})
    method = (http_cfg.get("method") or "GET").upper()
    path = http_cfg.get("path", "")

    path_params = http_cfg.get("pathParams", [])
    for param in path_params:
        if param not in args:
            raise ValueError(f"Missing path parameter: {param}")
        path = path.replace("{" + param + "}", urllib.parse.quote(str(args[param]), safe=""))

    query_params = http_cfg.get("queryParams", [])
    query = urllib.parse.urlencode(
        [(name, args[name]) for name in query_params if name in args and args[name] is not None],
        doseq=True,
    )

    url = BASE_URL + path
    if query:
        url = f"{url}?{query}"

    headers = dict(COMMON_HEADERS)
    headers.update({k: _resolve_header_value(v, args) for k, v in http_cfg.get("headers", {}).items()})

    auth_cfg = SPEC.get("server", {}).get("auth", {})
    if auth_cfg.get("type") == "bearer":
        token = _read_env_token()
        if token:
            headers[auth_cfg.get("headerName", "Authorization")] = f"Bearer {token}"

    data = None
    if http_cfg.get("body") == "all":
        data = json.dumps(args).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    return request


def _execute_tool(tool: dict, args: dict):
    request = _build_request(tool, args)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"text": raw}
    except urllib.error.HTTPError as exc:
        return {"error": exc.code, "message": exc.read().decode("utf-8", errors="ignore")}
    except Exception as exc:
        return {"error": "request_failed", "message": str(exc)}


def _safe_param_name(name: str) -> str:
    if name.isidentifier() and not keyword.iskeyword(name):
        return name
    return f"{name}_"


def _python_annotation(schema: dict) -> str:
    schema_type = schema.get("type", "string")
    mapping = {
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }
    return mapping.get(schema_type, "str")


def _tool_impl_factory(tool: dict):
    name = tool["name"]
    input_schema = tool.get("inputSchema", {})
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))

    params = []
    signature_lines = []
    for param_name, param_schema in properties.items():
        safe_name = _safe_param_name(param_name)
        annotation = _python_annotation(param_schema)
        if param_name in required:
            signature_lines.append(f"{safe_name}: {annotation}")
            params.append(inspect.Parameter(safe_name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation))
        else:
            default = repr(param_schema.get("default", None))
            signature_lines.append(f"{safe_name}: {annotation} = {default}")
            params.append(inspect.Parameter(safe_name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation, default=param_schema.get("default", None)))

    function_source = "def tool_impl(" + ", ".join(signature_lines) + "):\n"
    function_source += "    args = {original: locals()[safe] for original, safe in tool_aliases.items() if safe in locals()}\n"
    function_source += "    return _execute_tool(tool, args)\n"

    namespace = {
        "_execute_tool": _execute_tool,
        "tool": tool,
        "tool_aliases": {name: _safe_param_name(name) for name in properties.keys()},
    }
    exec(function_source, namespace)
    tool_impl = namespace["tool_impl"]
    tool_impl.__name__ = re.sub(r"[^0-9a-zA-Z_]+", "_", name)
    tool_impl.__doc__ = tool.get("description", "")
    tool_impl.__signature__ = inspect.Signature(params)
    return tool_impl


for tool in SPEC.get("tools", []):
    mcp.tool(name=tool["name"], description=tool.get("description", ""))(_tool_impl_factory(tool))


@mcp.tool()
def list_descriptor_tools() -> list[str]:
    """List all MCP tools derived from the NobleLife descriptor."""
    return [tool["name"] for tool in SPEC.get("tools", [])]


@mcp.tool()
def describe_descriptor_tool(name: str) -> dict:
    """Return the descriptor block for one tool by name."""
    for tool in SPEC.get("tools", []):
        if tool["name"] == name:
            return tool
    return {"error": "tool_not_found", "name": name}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
