# AWS WAF日志查詢並發送到n8n的PowerShell腳本
# 使用Python進行OpenSearch查詢，然後發送結果到n8n

param(
    [switch]$Help
)

# 配置變數
$N8N_WEBHOOK_URL = "https://n8n.forestrealty.org/webhook-test/02545a87-de3f-42f7-8504-9bbce10c3ccb"
$PYTHON_SCRIPT = "search_waf.py"
$LOG_FILE = "waf_python_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$TEMP_DATA = "waf_python_data_$([DateTimeOffset]::Now.ToUnixTimeSeconds()).json"

# 日志函數
function Write-LogInfo {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[INFO] $timestamp - $Message"
    Write-Host $logMessage -ForegroundColor Blue
    Add-Content -Path $LOG_FILE -Value $logMessage
}

function Write-LogSuccess {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[SUCCESS] $timestamp - $Message"
    Write-Host $logMessage -ForegroundColor Green
    Add-Content -Path $LOG_FILE -Value $logMessage
}

function Write-LogWarning {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[WARNING] $timestamp - $Message"
    Write-Host $logMessage -ForegroundColor Yellow
    Add-Content -Path $LOG_FILE -Value $logMessage
}

function Write-LogError {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[ERROR] $timestamp - $Message"
    Write-Host $logMessage -ForegroundColor Red
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# 檢查必要依賴
function Test-Dependencies {
    Write-LogInfo "檢查系統依賴..."
    
    # 檢查Python
    try {
        $pythonVersion = python --version 2>$null
        if (!$pythonVersion) {
            throw "Python未安裝"
        }
        Write-LogInfo "找到Python: $pythonVersion"
    }
    catch {
        Write-LogError "缺少Python"
        return $false
    }
    
    # 檢查Python腳本
    if (!(Test-Path $PYTHON_SCRIPT)) {
        Write-LogError "Python腳本不存在: $PYTHON_SCRIPT"
        return $false
    }
    
    # 檢查Python依賴
    try {
        python -c "import boto3, requests, requests_aws4auth" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "缺少Python依賴"
        }
    }
    catch {
        Write-LogWarning "缺少Python依賴，嘗試安裝..."
        try {
            pip install boto3 requests requests-aws4auth
            if ($LASTEXITCODE -ne 0) {
                throw "依賴安裝失敗"
            }
        }
        catch {
            Write-LogError "Python依賴安裝失敗"
            return $false
        }
    }
    
    Write-LogSuccess "所有依賴檢查完成"
    return $true
}

# 執行Python查詢
function Invoke-PythonQuery {
    Write-LogInfo "執行Python查詢腳本..."
    
    try {
        # 執行Python腳本並捕獲輸出
        $result = python $PYTHON_SCRIPT 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Python腳本執行失敗 (退出碼: $LASTEXITCODE)"
            Write-LogError "錯誤詳情: $result"
            return $false
        }
        
        # 保存輸出到臨時文件
        $result | Out-File -FilePath $TEMP_DATA -Encoding UTF8
        
        # 驗證JSON格式
        try {
            $jsonData = Get-Content $TEMP_DATA -Raw | ConvertFrom-Json
        }
        catch {
            Write-LogError "Python腳本輸出不是有效的JSON"
            Write-LogError "輸出內容: $result"
            return $false
        }
        
        # 檢查查詢結果
        $hitCount = if ($jsonData.total_hits) { $jsonData.total_hits } else { 0 }
        Write-LogInfo "查詢完成，找到 $hitCount 條記錄"
        
        if ($hitCount -eq 0) {
            Write-LogWarning "沒有找到匹配的安全事件"
            # 創建空報告
            $emptyReport = @{
                timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
                total_hits = 0
                events = @()
                message = "過去24小時內沒有檢測到安全威脅"
            }
            $emptyReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $TEMP_DATA -Encoding UTF8
        }
        
        return $true
    }
    catch {
        Write-LogError "執行Python查詢時發生錯誤: $_"
        return $false
    }
}

# 發送數據到n8n webhook
function Send-ToN8N {
    Write-LogInfo "發送數據到n8n webhook..."
    
    try {
        $jsonData = Get-Content $TEMP_DATA -Raw
        
        $response = Invoke-RestMethod -Uri $N8N_WEBHOOK_URL -Method Post -Body $jsonData -ContentType "application/json" -TimeoutSec 60
        
        Write-LogSuccess "數據成功發送到n8n"
        Write-LogInfo "n8n響應: $($response | ConvertTo-Json -Compress)"
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $responseBody = $_.Exception.Response | ConvertTo-Json -Compress
        
        Write-LogError "發送到n8n失敗"
        Write-LogError "HTTP狀態碼: $statusCode"
        Write-LogError "響應內容: $responseBody"
        Write-LogError "錯誤詳情: $_"
        return $false
    }
}

# 清理臨時文件
function Clear-TempFiles {
    Write-LogInfo "清理臨時文件..."
    
    if (Test-Path $TEMP_DATA) {
        Remove-Item $TEMP_DATA -Force
    }
    
    $errorFile = "$TEMP_DATA.error"
    if (Test-Path $errorFile) {
        Remove-Item $errorFile -Force
    }
}

# 顯示使用說明
function Show-Usage {
    Write-Host "AWS WAF日志查詢並發送到n8n腳本 (PowerShell + Python版本)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "功能：" -ForegroundColor White
    Write-Host "  - 使用Python和boto3查詢AWS OpenSearch" -ForegroundColor Gray
    Write-Host "  - 自動處理AWS認證" -ForegroundColor Gray
    Write-Host "  - 格式化數據並發送到n8n webhook" -ForegroundColor Gray
    Write-Host ""
    Write-Host "使用方法：" -ForegroundColor White
    Write-Host "  .\send_waf_log_today.ps1            # 執行查詢並發送到n8n" -ForegroundColor Gray
    Write-Host "  .\send_waf_log_today.ps1 -Help      # 顯示此幫助信息" -ForegroundColor Gray
    Write-Host ""
    Write-Host "依賴：" -ForegroundColor White
    Write-Host "  - Python 3.x" -ForegroundColor Gray
    Write-Host "  - boto3, requests, requests-aws4auth" -ForegroundColor Gray
    Write-Host "  - AWS認證配置 (AWS CLI或環境變數)" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# 主執行函數
function Main {
    # 檢查是否需要顯示幫助
    if ($Help) {
        Show-Usage
    }
    
    Write-LogInfo "========== AWS WAF Python查詢腳本開始執行 =========="
    
    try {
        # 檢查依賴
        if (!(Test-Dependencies)) {
            Write-LogError "依賴檢查失敗，腳本終止"
            exit 1
        }
        
        # 執行Python查詢
        if (!(Invoke-PythonQuery)) {
            Write-LogError "Python查詢失敗，腳本終止"
            exit 1
        }
        
        # 發送到n8n
        if (Send-ToN8N) {
            Write-LogSuccess "WAF日志成功發送到n8n"
            
            # 顯示摘要信息
            try {
                $jsonData = Get-Content $TEMP_DATA -Raw | ConvertFrom-Json
                $eventCount = if ($jsonData.total_hits) { $jsonData.total_hits } else { 0 }
                $queryTime = if ($jsonData.query_time_ms) { $jsonData.query_time_ms } else { 0 }
                
                Write-LogInfo "執行摘要:"
                Write-LogInfo "- 總事件數量: $eventCount"
                Write-LogInfo "- 查詢時間: ${queryTime}ms"
                Write-LogInfo "- 日志文件: $LOG_FILE"
                Write-LogInfo "- 執行時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            }
            catch {
                Write-LogWarning "無法讀取摘要信息"
            }
        }
        else {
            Write-LogError "發送到n8n失敗"
            exit 1
        }
        
        Write-LogInfo "========== 腳本執行完成 =========="
    }
    finally {
        # 清理臨時文件
        Clear-TempFiles
    }
}

# 腳本入口點
Main 
