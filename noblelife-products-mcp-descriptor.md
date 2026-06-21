{
  "mcpVersion": "1.0",
  "server": {
    "name": "noblelife-product-service",
    "version": "2.0.0",
    "description": "Read-only MCP-сервер для получения информации о туристических продуктах платформы NobleLife. Охватывает продукты, варианты, аддоны, медиа, информационные блоки, цены и корзину.",
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

    // {
    //   "name": "list_products",
    //   "description": "Получить постраничный список всех туристических продуктов. Можно фильтровать по агентскому каналу (B2B/B2C).",
    //   "inputSchema": {
    //     "type": "object",
    //     "properties": {
    //       "agent": {
    //         "type": "string",
    //         "enum": ["B2B", "B2C"],
    //         "description": "Фильтр по каналу продаж"
    //       },
    //       "locale": {
    //         "type": "string",
    //         "default": "en",
    //         "description": "Язык ответа (Content-Language), например 'en', 'ru', 'ar'"
    //       },
    //       "page": { "type": "integer", "default": 0, "minimum": 0 },
    //       "size": { "type": "integer", "default": 100, "minimum": 1 },
    //       "sort": {
    //         "type": "array",
    //         "items": { "type": "string" },
    //         "description": "Поля сортировки, например ['name,asc']"
    //       }
    //     }
    //   },
    //   "http": {
    //     "method": "GET",
    //     "path": "/api/v2/products",
    //     "queryParams": ["agent", "page", "size", "sort"],
    //     "headers": { "Content-Language": "{locale}" }
    //   }
    // },

    {
      "name": "list_products_brief",
      "description": "Получить постраничный список продуктов для сайта (B2C). Поддерживает фильтрацию по городу и тегу, сортировку и выбор валюты.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "page": { "type": "integer", "default": 0, "minimum": 0 },
          "size": { "type": "integer", "default": 100, "minimum": 1 },
          "sort": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Поля сортировки, например ['name,asc']"
          },
          "cityId": { "type": "integer", "description": "Фильтр по ID города" },
          "tagId": { "type": "string", "format": "uuid", "description": "Фильтр по UUID тега" },
          "displayCurrency": { "type": "string", "default": "AED", "description": "Валюта отображения цен" },
          "locale": { "type": "string", "default": "en", "description": "Язык ответа (Accept-Language)" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/website/products",
        "queryParams": ["page", "size", "sort", "cityId", "tagId", "displayCurrency"],
        "headers": { "Accept-Language": "{locale}" }
      },
      "responseFields": {
        "content": ["id", "name", "cityName", "foodIncluded", "hasGuide", "transportation", "freeCancellationHours", "duration", "displayPrice"]
      }
    },

    {
      "name": "get_product",
      "description": "Получить основные данные продукта по его UUID: название, варианты с включениями, параметры участников, отмена. Поле id в ответе — это productId, который необходимо использовать во всех последующих вызовах: get_availability, list_product_addons, list_addon_groups_for_product, list_product_media, list_product_information, add_to_cart.",
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
      },
      "responseFields": {
        "":                    ["id", "name", "cityName", "foodIncluded", "hasGuide", "transportation", "minParticipants", "maxParticipants", "freeCancellationHours", "duration", "variants"],
        "variants":            ["id", "name", "description", "isDefault", "inclusions"],
        "variants.inclusions": ["name"]
      }
    },

    // ─────────────────────────────────────────
    // АДДОНЫ
    // ─────────────────────────────────────────

    {
      "name": "list_addon_groups_for_product",
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

    {
      "name": "list_product_addons",
      "description": "Получить список аддонов продукта по его UUID.",
      "inputSchema": {
        "type": "object",
        "required": ["productId"],
        "properties": {
          "productId": { "type": "string", "format": "uuid", "description": "UUID продукта" }
        }
      },
      "http": {
        "method": "GET",
        "path": "/api/v2/products/{productId}/addons",
        "pathParams": ["productId"]
      },
      "responseFields": {
        "": ["id", "addonGroup", "addonSubGroup", "name", "description", "pricingEffect", "variantLinks"]
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
      "name": "list_product_information",
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
      },
      "responseFields": {
        "":           ["variantId", "addonId", "conditions", "entries"],
        "conditions": ["conditionType", "conditionValue"],
        "entries":    ["categoryType", "currencyCode", "rateType", "sellPrice", "wasPrice"]
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
      },
      "responseFields": {
        "":            ["dates"],
        "dates.slots": ["slotId", "timeSlotId", "productVariantId", "startTime", "available"]
      }
    },

    // ─────────────────────────────────────────
    // КОРЗИНА / ЗАКАЗ
    // ─────────────────────────────────────────

    {
      "name": "add_to_cart",
      "description": "Добавить продукт в корзину. Возвращает cart_id. Вызывать после подтверждения клиентом всех деталей заказа.",
      "inputSchema": {
        "type": "object",
        "required": ["product_id", "product_variant_id", "availability_slot_id", "time_slot_id", "event_date", "categories", "addons"],
        "properties": {
          "product_id": { "type": "string", "format": "uuid", "description": "UUID продукта" },
          "product_variant_id": { "type": "integer", "description": "ID варианта продукта (из get_product)" },
          "availability_slot_id": { "type": "integer", "description": "ID слота доступности (из get_availability)" },
          "time_slot_id": { "type": "integer", "description": "ID временного слота (из get_product)" },
          "event_date": { "type": "string", "format": "date", "description": "Дата мероприятия, YYYY-MM-DD" },
          "is_resident": { "type": "boolean", "default": false, "description": "Признак резидента ОАЭ" },
          "categories": {
            "type": "array",
            "minItems": 1,
            "description": "Участники по категориям. Обязательно хотя бы одна категория. Пример: [{\"type\": \"ADULT\", \"quantity\": 2}]",
            "items": {
              "type": "object",
              "required": ["type", "quantity"],
              "properties": {
                "type": { "type": "string", "enum": ["ADULT", "CHILD", "INFANT", "GROUP"], "description": "Поле называется 'type', не 'categoryType'. Обязательно." },
                "quantity": { "type": "integer", "minimum": 1 }
              }
            }
          },
          "addons": {
            "type": "array",
            "description": "Аддоны. Передавать пустой массив [] если аддонов нет.",
            "items": {
              "type": "object",
              "required": ["addon_id", "quantity"],
              "properties": {
                "addon_id": { "type": "integer" },
                "quantity": { "type": "integer", "minimum": 1 }
              }
            }
          }
        }
      },
      "http": {
        "baseUrl": "https://noblelife.ae/api/sales",
        "method": "POST",
        "path": "/sales/api/v3/cart/items",
        "body": "all"
      }
    },

    {
      "name": "checkout",
      "description": "Оформить заказ по cart_id. Принимает контактные данные клиента и возвращает ссылку на оплату. Вызывать после add_to_cart.",
      "inputSchema": {
        "type": "object",
        "required": ["cart_id", "customer_info"],
        "properties": {
          "cart_id": { "type": "string", "format": "uuid", "description": "ID корзины, полученный из add_to_cart" },
          "customer_info": {
            "type": "object",
            "required": ["first_name", "last_name", "email", "phone"],
            "properties": {
              "first_name": { "type": "string" },
              "last_name": { "type": "string" },
              "email": { "type": "string", "format": "email" },
              "phone": { "type": "string", "description": "Телефон с кодом страны, например '+971123456789'" },
              "marketing_consent": { "type": "boolean", "default": false },
              "pickup_location": { "type": "string", "description": "Место подбора клиента (отель, адрес)" }
            }
          },
        }
      },
      "http": {
        "baseUrl": "https://sales-prod.noblelife.ae",
        "method": "POST",
        "path": "/sales/api/v3/order/checkout",
        "body": "all",
        "bodyConstants": {
          "provider": "STRIPE",
          "success_url": "https://noblelife.ae/success?cartId={cart_id}",
          "cancel_url": "https://noblelife.ae/personal",
          "failure_url": "https://noblelife.ae/personal"
        }
      }
    },

  ],

  // ─────────────────────────────────────────
  // WORKFLOW HINTS ДЛЯ LLM
  // ─────────────────────────────────────────

  "workflowHints": {
    "salesFlow": [
      "Полный сценарий продажи:",
      "1. Поиск продуктов — list_products_brief.",
      "2. Детали продукта (описание, варианты, включения) — get_product(id), list_product_information(productId)",
      "3. После выбора продукта клиентом: get_product(id) — получить variant IDs (в базе знаний их нет).",
      "4. Параллельно: list_price_lists + list_addon_groups_for_product + list_product_addons — живые цены и аддоны.",
      "5. При упоминании даты: get_availability(productId, from, to) — окно ±1 день; 7 дней если дата гибкая.",
      "6. Предложить аддоны если list_addon_groups_for_product вернул группы. Применять правило подгрупп.",
      "7. Итоговое резюме → явное подтверждение клиента → add_to_cart.",
      "8. add_to_cart вызывать ТОЛЬКО после явного подтверждения клиента.",
      "9. Собрать контактные данные: имя, фамилию, email, телефон, pickup_location → вызвать checkout(cart_id, customer_info)."
    ],
    "getProductDetails": [
      "get_product(id) — возвращает: product, variants (с IDs), addons, timeSlots, media, priceLists.",
      "Variant IDs доступны только через этот вызов — в базе знаний их нет.",
      "Передать locale для получения данных на нужном языке."
    ],
    "pricingAndAddons": [
      "list_price_lists(productId) — все прайс-листы продукта.",
      "  addonId=null → цены вариантов; addonId≠null → цены конкретного аддона.",
      "list_addon_groups_for_product(productId) — группы аддонов.",
      "list_product_addons(productId) — полный список аддонов.",
      "Если группа имеет подгруппы — сначала выбрать подгруппу, затем показывать только её аддоны."
    ],
    "availability": [
      "get_availability(productId, from, to, productVariantId?) — публичный календарь доступности (B2C).",
      "Окно запроса: ±1 день от названной даты; 7 дней если клиент гибок.",
      "list_availability_slots — НЕ использовать в sales flow (admin-only)."
    ],
    "addToCart": [
      "add_to_cart — POST /sales/api/v3/cart/items на https://noblelife.ae/api/sales.",
      "Обязательные поля: product_id, product_variant_id, availability_slot_id, time_slot_id, event_date, categories[], addons[].",
      "categories: массив {type: ADULT|CHILD|INFANT|GROUP, quantity}. Минимум одна категория, никогда не передавать пустой массив.",
      "addons: массив {addon_id, quantity}. Передавать [] если аддонов нет.",
      "Возвращает cart_id. Передать cart_id в checkout.",
      "Пример успешного запроса: {\"product_id\": \"7c0f3154-a5f4-4fbb-9b1f-4a337edbe7bb\", \"product_variant_id\": 71, \"availability_slot_id\": 50509, \"time_slot_id\": 42, \"event_date\": \"2026-07-30\", \"is_resident\": false, \"categories\": [{\"type\": \"ADULT\", \"quantity\": 2}, {\"type\": \"CHILD\", \"quantity\": 1}], \"addons\": [{\"addon_id\": 45, \"quantity\": 1}, {\"addon_id\": 41, \"quantity\": 1}]}"
    ],
    "checkout": [
      "checkout — POST /sales/api/v3/order/checkout на https://sales-prod.noblelife.ae.",
      "Обязательные поля: cart_id (из add_to_cart), customer_info.first_name, last_name, email, phone.",
      "Перед вызовом собрать у клиента: имя, фамилию, email, телефон, pickup_location (если применимо).",
      "provider, success_url, cancel_url, failure_url — подставляются автоматически, не запрашивать у клиента.",
      "Возвращает checkoutUrl — ссылка на оплату для отправки клиенту.",
      "Пример успешного запроса: {\"cart_id\": \"92b063f2-b596-4747-acb3-c03c146c96d2\", \"customer_info\": {\"first_name\": \"MyFirstName\", \"last_name\": \"MyLastName\", \"email\": \"user@gmail.com\", \"phone\": \"+971123456789\", \"marketing_consent\": true, \"pickup_location\": \"MyLocation\"}}"
    ],
    "productContent": [
      "list_product_information(productId) — информационные блоки продукта (описание, маршрут, FAQ).",
      "list_product_media(productId) — медиафайлы продукта (изображения, видео)."
    ]
  }
}