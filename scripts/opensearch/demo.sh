#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${OPENSEARCH_URL:-http://localhost:9200}"

curl -sS -X DELETE "$BASE_URL/products" >/dev/null || true

curl -sS -X PUT "$BASE_URL/products"   -H "Content-Type: application/json"   -d '{
    "mappings": {
      "properties": {
        "sku":      {"type": "keyword"},
        "title":    {"type": "text"},
        "category": {"type": "keyword"},
        "price":    {"type": "double"}
      }
    }
  }'

printf '\n\nIndexing sample products...\n'

curl -sS -X POST "$BASE_URL/_bulk"   -H "Content-Type: application/x-ndjson"   --data-binary $'{"index":{"_index":"products","_id":"1"}}\n{"sku":"BK-1001","title":"Database Systems Handbook","category":"books","price":49.90}\n{"index":{"_index":"products","_id":"2"}}\n{"sku":"BK-1002","title":"Distributed Database Design","category":"books","price":59.00}\n{"index":{"_index":"products","_id":"3"}}\n{"sku":"VID-10","title":"Distributed Systems Course","category":"videos","price":29.00}\n'

curl -sS -X POST "$BASE_URL/products/_refresh" >/dev/null

printf '\nFull-text search:\n'
curl -sS -X POST "$BASE_URL/products/_search"   -H "Content-Type: application/json"   -d '{
    "_source": ["sku", "title", "category", "price"],
    "query": {
      "match": {
        "title": "distributed database"
      }
    }
  }'

printf '\n\nCategory aggregation:\n'
curl -sS -X POST "$BASE_URL/products/_search"   -H "Content-Type: application/json"   -d '{
    "size": 0,
    "aggs": {
      "categories": {
        "terms": {"field": "category"}
      }
    }
  }'

printf '\n'
