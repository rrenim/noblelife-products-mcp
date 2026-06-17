import inspect
import json
import keyword
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse


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
DEFAULT_UPSTREAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://product-new-prod.noblelife.ae/",
}

mcp = FastMCP(
    SERVER_NAME,
    instructions="Read-only MCP server for NobleLife products.",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
)

APP_VERSION = os.getenv("APP_VERSION", "2026-06-17T12:00:00Z")


@mcp.custom_route("/version", methods=["GET"])
async def version_endpoint(request: Request) -> JSONResponse:
    """Return the current build/version marker for the deployed service."""
    return JSONResponse({"version": APP_VERSION, "service": SERVER_NAME})


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

    base = http_cfg.get("baseUrl", BASE_URL).rstrip("/")

    query_params = http_cfg.get("queryParams", [])
    query = urllib.parse.urlencode(
        [(name, args[name]) for name in query_params if name in args and args[name] is not None],
        doseq=True,
    )

    url = base + path
    if query:
        url = f"{url}?{query}"

    headers = dict(DEFAULT_UPSTREAM_HEADERS)
    headers.update(COMMON_HEADERS)
    headers.update({k: _resolve_header_value(v, args) for k, v in http_cfg.get("headers", {}).items()})

    auth_cfg = SPEC.get("server", {}).get("auth", {})
    if auth_cfg.get("type") == "bearer":
        token = _read_env_token()
        if token:
            headers[auth_cfg.get("headerName", "Authorization")] = f"Bearer {token}"

    data = None
    if http_cfg.get("body") == "all":
        constants = {k: _resolve_header_value(v, args) for k, v in http_cfg.get("bodyConstants", {}).items()}
        body = {**args, **constants}
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    return request


def _project_at_path(data: object, path_parts: list, fields: list) -> object:
    """Recursively navigate path_parts into data, then filter to fields.
    Lists at any level are traversed automatically without being named in the path."""
    if isinstance(data, list):
        return [_project_at_path(item, path_parts, fields) for item in data]
    if not isinstance(data, dict):
        return data
    if not path_parts:
        field_set = set(fields)
        return {k: v for k, v in data.items() if k in field_set}
    key, rest = path_parts[0], path_parts[1:]
    if key not in data:
        return data
    result = dict(data)
    result[key] = _project_at_path(data[key], rest, fields)
    return result


def _execute_tool(tool: dict, args: dict):
    request = _build_request(tool, args)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            try:
                data = json.loads(raw)
                response_fields = tool.get("responseFields")
                if isinstance(response_fields, dict):
                    for path, fields in response_fields.items():
                        data = _project_at_path(data, path.split(".") if path else [], fields)
                return data
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


def _clean_tool_parameters(tool_obj) -> None:
    """Remove null defaults from the runtime MCP schema to avoid agents sending useless null fields."""
    parameters = getattr(tool_obj, "parameters", None)
    if not isinstance(parameters, dict):
        return

    for prop in parameters.get("properties", {}).values():
        if isinstance(prop, dict) and prop.get("default") is None:
            prop.pop("default", None)


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
        if safe_name != param_name:
            annotation = f"Annotated[{annotation}, Field(alias={param_name!r})]"
        if param_name in required:
            signature_lines.append(f"{safe_name}: {annotation}")
            params.append(inspect.Parameter(safe_name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation))
        else:
            default = repr(param_schema.get("default", None))
            signature_lines.append(f"{safe_name}: {annotation} = {default}")
            params.append(inspect.Parameter(safe_name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation, default=param_schema.get("default", None)))

    function_source = "def tool_impl(**kwargs):\n"
    function_source += "    args = {name: kwargs[name] for name in tool_arg_names if name in kwargs}\n"
    function_source += "    return _execute_tool(tool, args)\n"

    namespace = {
        "_execute_tool": _execute_tool,
        "tool": tool,
        "tool_arg_names": list(properties.keys()),
        "Annotated": Annotated,
        "Field": Field,
    }
    exec(function_source, namespace)
    tool_impl = namespace["tool_impl"]
    tool_impl.__name__ = re.sub(r"[^0-9a-zA-Z_]+", "_", name)
    tool_impl.__doc__ = tool.get("description", "")
    tool_impl.__signature__ = inspect.Signature(params)
    return tool_impl


for tool in SPEC.get("tools", []):
    mcp.tool(name=tool["name"], description=tool.get("description", ""))(_tool_impl_factory(tool))

for tool_obj in mcp._tool_manager._tools.values():
    _clean_tool_parameters(tool_obj)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
