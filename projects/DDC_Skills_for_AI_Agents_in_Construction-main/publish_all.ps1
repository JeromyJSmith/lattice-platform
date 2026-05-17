$basePath = "C:\Users\Artem Boiko\Documents\GitHub\DDC_Skills_for_AI_Agents_in_Construction"
$logFile = "$basePath\publish_log.txt"

$skillDirs = Get-ChildItem -Path $basePath -Recurse -Filter "SKILL.md" | ForEach-Object { $_.DirectoryName } | Sort-Object

$total = $skillDirs.Count
$success = 0
$failed = 0
$errors = @()

"Publishing $total skills to ClawHub..." | Tee-Object -FilePath $logFile
"Started: $(Get-Date)" | Tee-Object -FilePath $logFile -Append
"" | Tee-Object -FilePath $logFile -Append

foreach ($dir in $skillDirs) {
    $i = $skillDirs.IndexOf($dir) + 1
    $skillName = Split-Path $dir -Leaf

    Write-Host "[$i/$total] Publishing: $skillName" -NoNewline

    $result = & npx clawhub publish $dir --version "1.0.0" 2>&1 | Out-String

    if ($result -match "OK") {
        $success++
        Write-Host " -> OK" -ForegroundColor Green
        "[$i/$total] OK: $skillName" | Out-File -FilePath $logFile -Append
    } else {
        $failed++
        Write-Host " -> FAILED" -ForegroundColor Red
        $errors += "$skillName : $result"
        "[$i/$total] FAILED: $skillName -> $result" | Out-File -FilePath $logFile -Append
    }
}

"" | Tee-Object -FilePath $logFile -Append
"=== SUMMARY ===" | Tee-Object -FilePath $logFile -Append
"Total: $total" | Tee-Object -FilePath $logFile -Append
"Success: $success" | Tee-Object -FilePath $logFile -Append
"Failed: $failed" | Tee-Object -FilePath $logFile -Append
"Finished: $(Get-Date)" | Tee-Object -FilePath $logFile -Append

if ($errors.Count -gt 0) {
    "" | Tee-Object -FilePath $logFile -Append
    "=== ERRORS ===" | Tee-Object -FilePath $logFile -Append
    $errors | ForEach-Object { $_ | Tee-Object -FilePath $logFile -Append }
}
