# NobleLife Products MCP Server (Python)

Этот проект содержит MCP-сервер на Python, построенный на основе файла
`noblelife-products-mcp-descriptor.md`.

## Что сделано
- Загружает descriptor из Markdown/JSON-файла с комментариями.
- Генерирует MCP-инструменты из секции `tools`.
- Реализует HTTP-вызовы к базовому продукт-сервису NobleLife.

## Запуск
1. Установите зависимости:
   `python -m pip install -r requirements.txt`
2. Укажите bearer token (опционально):
   `set NOBLELIFE_BEARER_TOKEN=...`
3. Запустите сервер:
   `python server.py`

## Примечание
Сервер использует MCP SDK (`mcp`) и на старте регистрирует все инструменты из спецификации.
