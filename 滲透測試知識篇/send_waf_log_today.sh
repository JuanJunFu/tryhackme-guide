#!/bin/bash
set -euo pipefail

# === 0. 參數 ===
WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"
TMP_JSON="/tmp/waf_result_$(date +%Y%m%d_%H%M%S).json"

# === 1. 確保 Python 依賴已安裝 ===
pip install --user requests requests-aws4auth boto3 >/dev/null 2>&1

# === 2. 建立 Python 查詢腳本 ===
cat > /tmp/waf_query.py <<EOF
import boto3
import requests
from requests_aws4auth import AWS4Auth
import json

region = 'us-east-1'
service = 'es'
host = 'search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com'
index = 'awswaf-*'
url = f'https://{host}/{index}/_search'

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

headers = {"Content-Type": "application/json"}

query = {
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

response = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(query))
results = response.json()

summary = []
for hit in results.get("hits", {}).get("hits", []):
    src = hit["_source"]
    summary.append({
        "timestamp": src.get("timestamp", ""),
        "action": src.get("action", ""),
        "clientIP": src.get("httpRequest", {}).get("clientIp", ""),
        "uri": src.get("httpRequest", {}).get("uri", ""),
        "ruleGroup": src.get("ruleGroupList", [{}])[0].get("ruleGroupId", ""),
        "condition": src.get("terminatingRuleMatchDetails", [{}])[0].get("conditionType", "")
    })

with open("$TMP_JSON", "w") as f:
    json.dump(summary, f, indent=2)
EOF

# === 3. 執行 Python 查詢腳本 ===
python3 /tmp/waf_query.py

# === 4. 傳送結果到 n8n webhook ===
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  --data-binary @"$TMP_JSON"

echo "✅ WAF log 已發送至 n8n Webhook！"
