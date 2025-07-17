#!/bin/bash

OPENSEARCH_DOMAIN="https://search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com"
N8N_WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"   # 用 Production URL
OS_USER="admin"
OS_PASS="YourRealPassword"               # ← 請改成真密碼

read -r -d '' QUERY <<'JSON'
{
  "size": 100,
  "query": {
    "bool": {
      "filter": [
        {
          "range": {
            "timestamp": {
              "gte": "now-24h",
              "lte": "now",
              "format": "strict_date_optional_time"
            }
          }
        }
      ],
      "should": [
        { "term":    { "terminatingRuleMatchDetails.conditionType.keyword": "SQL_INJECTION" } },
        { "term":    { "terminatingRuleMatchDetails.conditionType.keyword": "CROSS_SITE_SCRIPTING" } },
        { "wildcard":{ "ruleGroupList.ruleGroupId.keyword": "*AmazonIpReputationList*" } },
        { "wildcard":{ "ruleGroupList.ruleGroupId.keyword": "*AnonymousIpList*" } },
        { "wildcard":{ "ruleGroupList.ruleGroupId.keyword": "*KnownBadInputsRuleSet*" } },
        { "wildcard":{ "ruleGroupList.ruleGroupId.keyword": "*AdminProtectionRuleSet*" } }
      ],
      "minimum_should_match": 1
    }
  }
}
JSON

# === 查詢 OpenSearch（A. Basic Auth 範例） ===
RESPONSE=$(curl -s -u "$OS_USER:$OS_PASS" \
  -H "Content-Type: application/json" \
  -X POST "$OPENSEARCH_DOMAIN/awswaf-*/_search" \
  -d "$QUERY")

# ===== 若要用 SigV4，改用下行 (把上面 -u 刪掉) =====
# RESPONSE=$(curl -s --aws-sigv4 "aws:es:us-east-1" \
#   -H "Content-Type: application/json" \
#   -X POST "$OPENSEARCH_DOMAIN/awswaf-*/_search" \
#   -d "$QUERY")

# === 組合 payload 傳給 n8n ===
PAYLOAD=$(jq -n --argjson resp "$RESPONSE" --arg src "aws-cloudshell" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
{
  source: $src,
  timestamp: $ts,
  query: "waf_attack_24h",
  result: $resp
}')

curl -s -X POST "$N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
