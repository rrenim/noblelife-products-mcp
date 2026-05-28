{
  "mcpVersion": "1.0",
  "server": {
    "name": "noblelife-product-service",
    "version": "2.0.0",
    "description": "Read-only MCP-сервер для получения информации о туристических продуктах платформы NobleLife. Охватывает продукты, варианты, аддоны, медиа, цены, переводы и справочники.",
    "baseUrl": "https://product-new-prod.noblelife.ae",
    "auth": {
      "type": "bearer",
      "headerName": "Authorization",
      "description": "JWT Bearer-токен. Передавать в заголовке Authorization: Bearer <token>"
    },
    "commonHeaders": {
      "Content-Type": "application/json",
      "Content-Language": "en"
    }
  },
  "tools": [

    // ─────────────────────────────────────────
    // ПРОДУКТЫ
    // ─────────────────────────────────────────

    {
      "name": "list_products",
      "description": "Получить постраничный список всех туристических продуктов. Можно фильтровать по агентскому каналу (B2B/B2C).",
      "inputSchema": {
        "type": "object",
        "properties": {
          "agent": {
            "type": "string",
            "enum": ["B2B", "B2C"],
            "description": "Фильтр по каналу продаж"
          },
          "locale": {
            "type": "string",
            "default": "en",
            "description": "Язык ответа (Content-Language), например 'en', 'ru', 'ar'"
          },
          "page": { "type": "integer", "default": 0, "minimum": 0 },
          "size": { "type": "integer", "default": 100, "minimum": 1 },
          "sort": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Поля сортировки, например ['name,asc']"
          }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products",
        "queryParams": ["agent", "page", "size", "sort"],
        "headers": { "Content-Language": "{locale}" }
      }
    },

    {
      "name": "get_product",
      "description": "Получить полные данные продукта по его UUID.",
      "inputSchema": {
        "type": "object",
        "required": ["id"],
        "properties": {
          "id": { "type": "string", "format": "uuid", "description": "UUID продукта" },
          "locale": { "type": "string", "default": "en", "description": "Язык ответа" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{id}",
        "pathParams": ["id"],
        "headers": { "Content-Language": "{locale}" }
      }
    },

    {
      "name": "get_product_editor",
      "description": "Загрузить агрегированный editor-payload для продукта: product, variants, addons, timeSlots, media, information, priceLists, availabilityRules, translations, publishReadiness. Основной источник полного состояния продукта.",
      "inputSchema": {
        "type": "object",
        "required": ["id"],
        "properties": {
          "id": { "type": "string", "format": "uuid", "description": "UUID продукта" },
          "locale": { "type": "string", "default": "en", "description": "Язык переводов в ответе" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{id}/editor",
        "pathParams": ["id"],
        "headers": { "Content-Language": "{locale}" }
      }
    },

    {
      "name": "get_product_info",
      "description": "Получить краткую публичную информацию о продукте.",
      "inputSchema": {
        "type": "object",
        "required": ["id"],
        "properties": {
          "id": { "type": "string", "format": "uuid" },
          "locale": { "type": "string", "default": "en" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{id}/info",
        "pathParams": ["id"],
        "headers": { "Content-Language": "{locale}" }
      }
    },

    {
      "name": "get_publish_readiness",
      "description": "Проверить готовность продукта к публикации. Возвращает список blocker-кодов: NO_ACTIVE_VARIANT, VARIANT_NO_ACTIVE_PRICE_LIST, PRICE_LIST_EMPTY.",
      "inputSchema": {
        "type": "object",
        "required": ["id"],
        "properties": {
          "id": { "type": "string", "format": "uuid", "description": "UUID продукта" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{id}/publish-readiness",
        "pathParams": ["id"]
      }
    },

    // ─────────────────────────────────────────
    // АДДОНЫ
    // ─────────────────────────────────────────

    {
      "name": "get_addon_groups_for_product",
      "description": "Получить список групп аддонов, доступных для продукта.",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{productId}/addons/groups",
        "pathParams": ["productId"]
      }
    },

    // ─────────────────────────────────────────
    // МЕДИА ПРОДУКТА
    // ─────────────────────────────────────────

    {
      "name": "list_product_media",
      "description": "Получить список медиафайлов продукта (изображения, видео, документы и т.д.).",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{productId}/media",
        "pathParams": ["productId"]
      }
    },

    // ─────────────────────────────────────────
    // ИНФОРМАЦИОННЫЕ БЛОКИ
    // ─────────────────────────────────────────

    {
      "name": "get_product_information",
      "description": "Получить информационные блоки продукта (описательные секции с медиа).",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{productId}/information",
        "pathParams": ["productId"]
      }
    },

    // ─────────────────────────────────────────
    // ПРАЙС-ЛИСТЫ
    // ─────────────────────────────────────────

    {
      "name": "list_price_lists",
      "description": "Получить прайс-листы продукта. Опционально фильтровать по variantId или addonId.",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" },
          "variantId": { "type": "integer", "description": "Фильтр по варианту" },
          "addonId": { "type": "integer", "description": "Фильтр по аддону" },
          "isActive": { "type": "boolean", "default": true }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/price-lists",
        "queryParams": ["productId", "variantId", "addonId", "isActive"]
      }
    },

    // ─────────────────────────────────────────
    // СЛОТЫ ДОСТУПНОСТИ
    // ─────────────────────────────────────────

    {
      "name": "get_availability",
      "description": "Получить публичный календарь доступности продукта для B2C. Возвращает доступные даты и слоты в указанном диапазоне.",
      "inputSchema": {
        "type": "object",
        "required": ["productId", "from", "to"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" },
          "from": { "type": "string", "format": "date", "description": "Начало диапазона, YYYY-MM-DD" },
          "to": { "type": "string", "format": "date", "description": "Конец диапазона, YYYY-MM-DD" },
          "productVariantId": { "type": "integer", "description": "Фильтр по варианту" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/availability",
        "queryParams": ["productId", "from", "to", "productVariantId"]
      }
    },

    {
      "name": "list_availability_slots",
      "description": "Получить детальный список слотов доступности продукта (admin-view). Фильтрация по диапазону дат или по флагу needsReview.",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid" },
          "from": { "type": "string", "format": "date" },
          "to": { "type": "string", "format": "date" },
          "needsReview": { "type": "boolean", "description": "Только слоты, требующие проверки" },
          "page": { "type": "integer", "default": 0 },
          "size": { "type": "integer", "default": 100 }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/availability-slots",
        "queryParams": ["productId", "from", "to", "needsReview", "page", "size"]
      }
    },

    // ─────────────────────────────────────────
    // ПЕРЕВОДЫ
    // ─────────────────────────────────────────

    {
      "name": "get_translations",
      "description": "Получить переводы одной сущности по типу, ID и локали. entityType: product | variant | inclusion | addon | information.",
      "inputSchema": {
        "type": "object",
        "required": ["entityType", "entityId", "locale"],
        "properties": {
          "entityType": {
            "type": "string",
            "enum": ["product", "variant", "inclusion", "addon", "information"]
          },
          "entityId": { "type": "string" },
          "locale": { "type": "string", "description": "Код языка, например 'ru', 'ar', 'en'" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/translations/{entityType}/{entityId}",
        "pathParams": ["entityType", "entityId"],
        "queryParams": ["locale"]
      }
    },

    {
      "name": "get_translations_batch",
      "description": "Batch-загрузка переводов для нескольких сущностей одного типа за один запрос.",
      "inputSchema": {
        "type": "object",
        "required": ["entityType", "entityIds", "locale"],
        "properties": {
          "entityType": {
            "type": "string",
            "enum": ["product", "variant", "inclusion", "addon", "information"]
          },
          "entityIds": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Массив UUID/ID сущностей"
          },
          "locale": { "type": "string" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/translations/{entityType}",
        "pathParams": ["entityType"],
        "queryParams": ["entityIds", "locale"]
      }
    },

    // ─────────────────────────────────────────
    // СПРАВОЧНИКИ
    // ─────────────────────────────────────────

    {
      "name": "list_countries",
      "description": "Получить список стран (справочник).",
      "inputSchema": { "type": "object", "properties": {} },
      "http": { "method": "GET", "path": "/api/v2/countries" }
    },

    {
      "name": "list_cities",
      "description": "Получить список городов. Можно фильтровать по countryId.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "countryId": { "type": "integer", "description": "ID страны для фильтрации" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/cities",
        "queryParams": ["countryId"]
      }
    },

    {
      "name": "list_tags",
      "description": "Получить список тегов (справочник).",
      "inputSchema": { "type": "object", "properties": {} },
      "http": { "method": "GET", "path": "/api/v2/tags" }
    },

    {
      "name": "list_addon_groups",
      "description": "Получить список групп аддонов (справочник).",
      "inputSchema": { "type": "object", "properties": {} },
      "http": { "method": "GET", "path": "/api/v2/addon-groups" }
    },

    {
      "name": "list_addon_sub_groups",
      "description": "Получить список подгрупп аддонов (справочник).",
      "inputSchema": { "type": "object", "properties": {} },
      "http": { "method": "GET", "path": "/api/v2/addon-sub-groups" }
    },

    {
      "name": "list_itinerary_point_types",
      "description": "Получить список типов точек маршрута (справочник).",
      "inputSchema": { "type": "object", "properties": {} },
      "http": { "method": "GET", "path": "/api/v2/itinerary-point-types" }
    },

    // ─────────────────────────────────────────
    // ЦЕНЫ (ВЫЧИСЛИТЕЛЬНЫЕ ЗАПРОСЫ)
    // ─────────────────────────────────────────

    {
      "name": "resolve_prices",
      "description": "Рассчитать актуальные цены для набора продуктов/вариантов/аддонов с учётом даты, слота и канала продаж. Данные не изменяются — только вычисление.",
      "inputSchema": {
        "type": "object",
        "required": ["products"],
        "properties": {
          "products": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["productId", "date"],
              "properties": {
                "keyId": { "type": "string" },
                "productId": { "type": "string", "format": "uuid" },
                "variantId": { "type": "integer" },
                "date": { "type": "string", "format": "date" },
                "timeSlot": { "type": "string" },
                "categories": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "type": { "type": "string", "description": "Например: ADULT, CHILD, PRIVATE" },
                      "quantity": { "type": "integer" }
                    }
                  }
                },
                "addons": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "addonId": { "type": "integer" },
                      "quantity": { "type": "integer" }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "http": {
        "method": "POST",
        "path": "/api/v2/prices/resolve",
        "body": "all"
      }
    },

    {
      "name": "fetch_prices",
      "description": "Получить цены для конкретных продуктов в B2C-витрине. Данные не изменяются — только выборка.",
      "inputSchema": {
        "type": "object",
        "required": ["products"],
        "properties": {
          "displayCurrency": { "type": "string", "description": "Код валюты, например AED, USD" },
          "products": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["productId", "date"],
              "properties": {
                "keyId": { "type": "string" },
                "productId": { "type": "string", "format": "uuid" },
                "date": { "type": "string", "format": "date" },
                "categories": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "type": { "type": "string" },
                      "tier": { "type": "integer" }
                    }
                  }
                },
                "addons": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "id": { "type": "integer" },
                      "tier": { "type": "integer" }
                    }
                  }
                },
                "isResident": { "type": "boolean" }
              }
            }
          }
        }
      },
      "http": {
        "method": "POST",
        "path": "/api/v2/prices/fetch",
        "body": "all"
      }
    }
  ],

  // ─────────────────────────────────────────
  // WORKFLOW HINTS ДЛЯ LLM
  // ─────────────────────────────────────────

  "workflowHints": {
    "readProductFull": [
      "Для полной картины по одному продукту вызвать get_product_editor — возвращает всё в одном ответе:",
      "product, variants, addons, timeSlots, media, information, priceLists, availabilityRules, translations, publishReadiness.",
      "Передать locale для получения переводов на нужном языке."
    ],
    "readProductCatalog": [
      "1. list_products — получить список продуктов с пагинацией",
      "2. get_product или get_product_info — детали конкретного продукта",
      "3. list_price_lists — цены по productId (фильтр по variantId / addonId)",
      "4. get_availability — доступные даты и слоты в диапазоне дат"
    ],
    "readTranslations": [
      "- get_translations — переводы одной сущности (entityType + entityId + locale)",
      "- get_translations_batch — переводы нескольких сущностей одного типа за один запрос",
      "- entityType: product | variant | inclusion | addon | information",
      "- Поля: product→name,description,rich_text; variant/addon/inclusion→name,description; information→name,description,rich_text"
    ],
    "pricing": [
      "- resolve_prices: рассчитать цену под конкретную дату, слот, категории участников и канал продаж",
      "- fetch_prices: получить базовые цены для витрины без детальных условий",
      "- Оба метода используют POST, но данные не изменяют"
    ],
    "referenceData": [
      "Справочники загружаются однократно и кэшируются:",
      "list_countries → list_cities (с фильтром countryId) → list_tags → list_addon_groups → list_addon_sub_groups"
    ]
  }
}