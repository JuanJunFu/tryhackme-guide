#!/bin/bash

# === 1. 今日日期
TODAY=$(date +%Y-%m-%d)
INDEX_NAME="awswaf-$TODAY"

# === 2. 查詢 OpenSearch 資料
OPENSEARCH_DOMAIN="https://search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com"
QUERY_RESULT=$(curl -s -X POST "$OPENSEARCH_DOMAIN/$INDEX_NAME/_search" \
  -H "Content-Type: application/json" \
  -u admin:your-password-here \
  -d '{
    "size": 10,
    "query": {
      "match_all": {}
    }
  }')

# === 3. 發送到正式 n8n Webhook（非 webhook-test）
curl -X POST https://n8n.forestrealty.org/webhook/02545a87-de3f-42f7-8504-9bbce10c3ccb \
  -H "Content-Type: application/json" \
  -d "{
    \"source\": \"aws-cloudshell\",
    \"index\": \"$INDEX_NAME\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"result\": $QUERY_RESULT
  }"
