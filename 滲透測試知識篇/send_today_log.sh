#!/bin/bash

# === 1. 設定變數 ===
TODAY=$(date +%Y-%m-%d)
INDEX_NAME="awswaf-$TODAY"
OPENSEARCH_DOMAIN="https://search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com"
N8N_WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"

# === 2. 查詢 OpenSearch ===
QUERY_RESULT=$(curl -s -X POST "$OPENSEARCH_DOMAIN/$INDEX_NAME/_search" \
  -H "Content-Type: application/json" \
  -u admin:your-password-here \
  -d '{
    "size": 10,
    "query": {
      "match_all": {}
    }
  }')

# === 3. 組合 POST 給 n8n 的 JSON ===
PAYLOAD=$(cat <<EOF
{
  "source": "aws-cloudshell",
  "index": "$INDEX_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "result": $QUERY_RESULT
}
EOF
)

# === 4. 發送到 n8n Webhook ===
curl -X POST "$N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
