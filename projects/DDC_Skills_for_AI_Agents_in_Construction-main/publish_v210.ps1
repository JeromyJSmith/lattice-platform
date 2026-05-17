$ErrorActionPreference = "Continue"
$basePath = "C:\Users\Artem Boiko\Documents\GitHub\DDC_Skills_for_AI_Agents_in_Construction"
$logFile = "$basePath\publish_v210_log.txt"
$delay = 300  # 5 minutes between publishes

# estimate-builder already published as #1
$skills = @(
    "2_DDC_Book\3.1-Cost-Estimation\cost-estimation-resource",
    "2_DDC_Book\3.2-QTO-Auto-Estimates\auto-estimate-generator",
    "1_DDC_Toolkit\Cost-Management\bim-cost-estimation-cwicr",
    "1_DDC_Toolkit\CWICR-Database\cwicr-cost-calculator",
    "2_DDC_Book\3.1-Cost-Estimation\historical-cost-analyzer",
    "2_DDC_Book\3.1-Cost-Estimation\unit-price-database-manager",
    "5_DDC_Innovative\open-construction-estimate",
    "1_DDC_Toolkit\BIM-Analysis\ifc-qto-extraction",
    "2_DDC_Book\4.5-ML-Cost-Prediction\cost-prediction",
    "1_DDC_Toolkit\CAD-Converters\dwg-to-excel",
    "1_DDC_Toolkit\CAD-Converters\dgn-to-excel",
    "1_DDC_Toolkit\CAD-Converters\rvt-to-excel",
    "1_DDC_Toolkit\CAD-Converters\ifc-to-excel",
    "1_DDC_Toolkit\CAD-Converters\rvt-to-ifc",
    "1_DDC_Toolkit\CAD-Converters\batch-cad-converter",
    "2_DDC_Book\2.4-PDF-CAD-to-Data\pdf-to-structured",
    "2_DDC_Book\2.4-PDF-CAD-to-Data\cad-to-data",
    "2_DDC_Book\2.4-PDF-CAD-to-Data\image-to-data",
    "5_DDC_Innovative\ifc-data-extraction"
)

Set-Location $basePath
$count = 2  # Starting from 2 since estimate-builder was #1

foreach ($skill in $skills) {
    $name = Split-Path $skill -Leaf
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Publishing $count/20: $name ..."
    "[$timestamp] Publishing $count/20: $name" | Out-File $logFile -Append

    try {
        $result = npx clawhub publish $skill --version "2.1.0" 2>&1
        $resultStr = $result -join "`n"
        Write-Host $resultStr
        "  Result: $resultStr" | Out-File $logFile -Append
    } catch {
        $err = $_.Exception.Message
        Write-Host "  ERROR: $err"
        "  ERROR: $err" | Out-File $logFile -Append
    }

    $count++
    if ($count -le 20) {
        Write-Host "  Waiting $delay seconds..."
        Start-Sleep -Seconds $delay
    }
}

$timestamp = Get-Date -Format "HH:mm:ss"
Write-Host "[$timestamp] Done! Published all 20 skills."
"[$timestamp] Done! All skills published." | Out-File $logFile -Append
