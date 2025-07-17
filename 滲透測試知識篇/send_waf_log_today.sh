#!/bin/bash
# ==========================================
# send_waf_log_today.sh
# 查詢 AWS WAF logs (OpenSearch) 並傳送至 n8n
# ==========================================
set -euo pipefail

# ---------- 0. 可自行調整的參數 ----------
REGION="us-east-1"
OPENSEARCH_HOST="search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.${REGION}.es.amazonaws.com"
INDEX_PATTERN="awswaf-*"
WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"
TMP_DIR="/tmp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TMP_PY="${TMP_DIR}/waf_query_${TIMESTAMP}.py"
TMP_JSON="${TMP_DIR}/waf_result_${TIMESTAMP}.json"

# ---------- 1. 安裝 / 確認 Python 依賴 ----------
python3 - <<'PYCHECK' || true
import pkg_resources, sys
required = {"boto3", "requests", "requests-aws4auth"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    sys.exit(1)
PYCHECK
if [[ $? -ne 0 ]]; then
  echo "Installing missing Python packages..."
  pip install --user boto3 requests requests-aws4auth >/dev/null
fi

# ---------- 2. 動態產生 Python 查詢腳本 ----------
cat > "${TMP_PY}" <<PYTHON
import boto3, json, sys, requests
from requests_aws4auth import AWS4Auth

region = "${REGION}"
service = "es"
host = "${OPENSEARCH_HOST}"
index = "${INDEX_PATTERN}"
url = f"https://{host}/{index}/_search"

session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)

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
        { "term": { "terminatingRuleMatchDetails.conditionType.keyword": "SQL_INJECTION" } },
        { "term": { "terminatingRuleMatchDetails.conditionType.keyword": "CROSS_SITE_SCRIPTING" } },
        { "wildcard": { "ruleGroupList.ruleGroupId.keyword": "*AmazonIpReputationList*" } },
        { "wildcard": { "ruleGroupList.ruleGroupId.keyword": "*AnonymousIpList*" } },
        { "wildcard": { "ruleGroupList.ruleGroupId.keyword": "*KnownBadInputsRuleSet*" } },
        { "wildcard": { "ruleGroupList.ruleGroupId.keyword": "*AdminProtectionRuleSet*" } }
      ],
      "minimum_should_match": 1
    }
  }
}

resp = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(query))
if resp.status_code != 200:
    print(json.dumps({"error": resp.text, "status_code": resp.status_code}))
    sys.exit(1)

hits = resp.json().get("hits", {}).get("hits", [])
summary = []
for h in hits:
    src = h.get("_source", {})
    http_req = src.get("httpRequest", {})
    rule_groups = src.get("ruleGroupList", [])
    term_details = src.get("terminatingRuleMatchDetails", [])

    summary.append({
        "timestamp": src.get("timestamp", ""),
        "action": src.get("action", ""),
        "clientIP": http_req.get("clientIp", ""),
        "uri": http_req.get("uri", ""),
        "ruleGroup": rule_groups[0].get("ruleGroupId", "") if rule_groups else "",
        "condition": term_details[0].get("conditionType", "") if term_details else ""
    })

with open("${TMP_JSON}", "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(summary)} records to ${TMP_JSON}")
PYTHON

# ---------- 3. 執行 Python 查詢 ----------
python3 "${TMP_PY}"

# ---------- 4. 送結果到 n8n Webhook ----------
curl -s -o /dev/null -w "%{http_code}\n" \
     -X POST "${WEBHOOK_URL}" \
     -H "Content-Type: application/json" \
     --data-binary @"${TMP_JSON}"

echo "✅ 已將 WAF 日誌傳送至 n8n Webhook：${WEBHOOK_URL}"
echo "📄 本地備份檔：${TMP_JSON}"

# ---------- 5. 清理臨時 Python 腳本（可選） ----------
rm -f "${TMP_PY}"
