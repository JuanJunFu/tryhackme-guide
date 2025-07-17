#!/bin/bash
# 查詢 awswaf-* 最近 24 小時符合特定攻擊條件的紀錄，送到 n8n

OPENSEARCH_DOMAIN="https://search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com"
N8N_WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"

read -r -d '' QUERY <<'EOF'
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
EOF

RESPONSE=$(curl -s -u admin:your-password-here \
  -H "Content-Type: application/json" \
  -X POST "$OPENSEARCH_DOMAIN/awswaf-*/_search" \
  -d "$QUERY")

PAYLOAD=$(cat <<EOF
{
  "source": "aws-cloudshell",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "query": "waf_attack_24h",
  "result": $RESPONSE
}
EOF
)

curl -X POST "$N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
