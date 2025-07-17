#!/bin/bash

# AWS WAF日志發送到n8n的腳本
# 功能：從OpenSearch獲取過去24小時的安全事件日志並發送到n8n webhook

# 配置變數
OPENSEARCH_URL="https://search-osdfw-opensearch-domain-czs6yeuy3ar7t54kvjynovakli.us-east-1.es.amazonaws.com"
N8N_WEBHOOK_URL="https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"
INDEX_PATTERN="awswaf-*"
LOG_FILE="/tmp/waf_log_$(date +%Y%m%d_%H%M%S).log"

# 顏色輸出設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

# 檢查必要工具
check_dependencies() {
    log_info "檢查系統依賴..."
    
    for cmd in curl jq; do
        if ! command -v $cmd &> /dev/null; then
            log_error "缺少必要工具: $cmd"
            log_info "請安裝 $cmd 後重新執行"
            exit 1
        fi
    done
    
    log_success "所有依賴檢查完成"
}

# 構建OpenSearch查詢JSON
build_search_query() {
    cat << 'EOF'
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
}

# 從OpenSearch獲取數據
fetch_opensearch_data() {
    log_info "開始從OpenSearch獲取WAF日志數據..."
    
    local query_json=$(build_search_query)
    local temp_response="/tmp/opensearch_response_$(date +%s).json"
    
    # 發送請求到OpenSearch
    curl -s -X GET "${OPENSEARCH_URL}/${INDEX_PATTERN}/_search" \
        -H "Content-Type: application/json" \
        -d "$query_json" \
        -o "$temp_response" \
        --connect-timeout 30 \
        --max-time 60
    
    local curl_exit_code=$?
    
    if [ $curl_exit_code -ne 0 ]; then
        log_error "OpenSearch請求失敗，退出碼: $curl_exit_code"
        rm -f "$temp_response"
        return 1
    fi
    
    # 檢查響應是否包含錯誤
    if jq -e '.error' "$temp_response" > /dev/null 2>&1; then
        log_error "OpenSearch返回錯誤:"
        jq '.error' "$temp_response" | tee -a "${LOG_FILE}"
        rm -f "$temp_response"
        return 1
    fi
    
    # 檢查是否有命中結果
    local hit_count=$(jq -r '.hits.total.value // 0' "$temp_response")
    log_info "找到 $hit_count 條匹配記錄"
    
    if [ "$hit_count" -eq 0 ]; then
        log_warning "過去24小時內沒有找到匹配的安全事件"
        rm -f "$temp_response"
        return 2
    fi
    
    echo "$temp_response"
    return 0
}

# 處理和格式化數據
process_data() {
    local response_file="$1"
    local processed_data="/tmp/processed_waf_data_$(date +%s).json"
    
    log_info "處理和格式化WAF數據..."
    
    # 提取並格式化相關欄位
    jq '{
        timestamp: now | strftime("%Y-%m-%d %H:%M:%S"),
        total_hits: .hits.total.value,
        events: [
            .hits.hits[] | {
                timestamp: ._source.timestamp,
                source_ip: ._source.httpRequest.clientIp,
                action: ._source.action,
                terminatingRule: ._source.terminatingRuleMatchDetails.conditionType,
                ruleGroups: [._source.ruleGroupList[]?.ruleGroupId],
                uri: ._source.httpRequest.uri,
                method: ._source.httpRequest.httpMethod,
                country: ._source.httpRequest.country,
                userAgent: ._source.httpRequest.headers[]? | select(.name == "User-Agent") | .value
            }
        ]
    }' "$response_file" > "$processed_data"
    
    if [ $? -eq 0 ]; then
        log_success "數據處理完成"
        echo "$processed_data"
        return 0
    else
        log_error "數據處理失敗"
        return 1
    fi
}

# 發送數據到n8n webhook
send_to_n8n() {
    local data_file="$1"
    
    log_info "發送數據到n8n webhook..."
    
    local response=$(curl -s -X POST "$N8N_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d @"$data_file" \
        --connect-timeout 30 \
        --max-time 60 \
        -w "HTTP_CODE:%{http_code}")
    
    local curl_exit_code=$?
    local http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    local response_body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
    
    if [ $curl_exit_code -ne 0 ]; then
        log_error "發送到n8n失敗，curl退出碼: $curl_exit_code"
        return 1
    fi
    
    case "$http_code" in
        200|201|202)
            log_success "數據成功發送到n8n (HTTP $http_code)"
            log_info "n8n響應: $response_body"
            return 0
            ;;
        *)
            log_error "n8n返回錯誤 HTTP $http_code"
            log_error "響應內容: $response_body"
            return 1
            ;;
    esac
}

# 清理臨時文件
cleanup() {
    log_info "清理臨時文件..."
    rm -f /tmp/opensearch_response_*.json
    rm -f /tmp/processed_waf_data_*.json
}

# 主執行函數
main() {
    log_info "========== AWS WAF日志發送腳本開始執行 =========="
    
    # 設置錯誤處理
    trap cleanup EXIT
    
    # 檢查依賴
    check_dependencies
    
    # 獲取OpenSearch數據
    local opensearch_response
    opensearch_response=$(fetch_opensearch_data)
    local fetch_result=$?
    
    case $fetch_result in
        0)
            log_success "OpenSearch數據獲取成功"
            ;;
        1)
            log_error "OpenSearch請求失敗，腳本終止"
            exit 1
            ;;
        2)
            log_warning "沒有找到匹配的安全事件，發送空報告到n8n"
            echo '{"timestamp":"'$(date '+%Y-%m-%d %H:%M:%S')'","total_hits":0,"events":[],"message":"過去24小時內沒有檢測到安全威脅"}' > /tmp/empty_report.json
            send_to_n8n "/tmp/empty_report.json"
            rm -f /tmp/empty_report.json
            exit 0
            ;;
    esac
    
    # 處理數據
    local processed_data
    processed_data=$(process_data "$opensearch_response")
    
    if [ $? -ne 0 ]; then
        log_error "數據處理失敗，腳本終止"
        exit 1
    fi
    
    # 發送到n8n
    if send_to_n8n "$processed_data"; then
        log_success "WAF日志成功發送到n8n"
        
        # 顯示摘要信息
        local event_count=$(jq -r '.total_hits' "$processed_data")
        log_info "本次處理摘要:"
        log_info "- 總事件數量: $event_count"
        log_info "- 日志文件: $LOG_FILE"
        log_info "- 執行時間: $(date '+%Y-%m-%d %H:%M:%S')"
    else
        log_error "發送到n8n失敗"
        exit 1
    fi
    
    log_info "========== 腳本執行完成 =========="
}

# 腳本入口點
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
