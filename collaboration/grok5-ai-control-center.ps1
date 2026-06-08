# 將此段加入 grok5-ai-control-center.ps1 的初始化區塊
Write-Host "[Security] 檢查 Lightning 密鑰系統..." -ForegroundColor Yellow

function Load-System-Keys {
    $keys = @("key_1", "key_2", "key_3", "key_4", "key_10")
    foreach ($k in $keys) {
        if (-not (Test-Path Env:LIGHTNING_$(($k).ToUpper()))) {
            Write-Host "⚠️ 警告: $k 未設定，系統將降級運行..." -ForegroundColor Red
        }
    }
}

# 執行選單前先載入
Load-System-Keys

