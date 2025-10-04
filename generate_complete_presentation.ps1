# PowerShell script to combine all Marp slide files into one comprehensive presentation
# and generate as PDF

Write-Host "🔄 Combining all slide files into one presentation..." -ForegroundColor Cyan

# Create the combined presentation file
$CombinedFile = "COMPLETE_LLM_ARCHITECTURE_PRESENTATION.md"

# Start with the main architecture slides
Write-Host "📊 Adding main architecture overview..." -ForegroundColor Green
Copy-Item "LLM_ARCHITECTURE_SLIDES.md" $CombinedFile

# Add separator and component slides
Write-Host "🔋 Adding Energy Analyzer slides..." -ForegroundColor Green
Add-Content $CombinedFile ""
Add-Content $CombinedFile "---"
Add-Content $CombinedFile ""
Get-Content "ENERGY_ANALYZER_SLIDES.md" | Add-Content $CombinedFile

Write-Host "🛡️ Adding Safety Monitor slides..." -ForegroundColor Green
Add-Content $CombinedFile ""
Add-Content $CombinedFile "---"
Add-Content $CombinedFile ""
Get-Content "SAFETY_MONITOR_SLIDES.md" | Add-Content $CombinedFile

Write-Host "🔍 Adding Response Analyzer slides..." -ForegroundColor Green
Add-Content $CombinedFile ""
Add-Content $CombinedFile "---"
Add-Content $CombinedFile ""
Get-Content "RESPONSE_ANALYZER_SLIDES.md" | Add-Content $CombinedFile

Write-Host "💕 Adding Girlfriend Agent slides..." -ForegroundColor Green
Add-Content $CombinedFile ""
Add-Content $CombinedFile "---"
Add-Content $CombinedFile ""
Get-Content "GIRLFRIEND_AGENT_SLIDES.md" | Add-Content $CombinedFile

Write-Host "📖 Adding Script Manager slides..." -ForegroundColor Green
Add-Content $CombinedFile ""
Add-Content $CombinedFile "---"
Add-Content $CombinedFile ""
Get-Content "SCRIPT_MANAGER_SLIDES.md" | Add-Content $CombinedFile

Write-Host "✅ Combined presentation created: $CombinedFile" -ForegroundColor Yellow

# Check if Marp CLI is installed
try {
    $marpVersion = marp --version 2>$null
    Write-Host "📄 Generating PDF presentation..." -ForegroundColor Cyan
    marp $CombinedFile --pdf --output "COMPLETE_LLM_ARCHITECTURE_PRESENTATION.pdf"
    
    Write-Host "🌐 Generating HTML presentation..." -ForegroundColor Cyan
    marp $CombinedFile --html --output "COMPLETE_LLM_ARCHITECTURE_PRESENTATION.html"
    
    Write-Host "🎉 Complete presentation generated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Files created:" -ForegroundColor White
    Write-Host "   - $CombinedFile (Combined Markdown)" -ForegroundColor Gray
    Write-Host "   - COMPLETE_LLM_ARCHITECTURE_PRESENTATION.pdf (PDF)" -ForegroundColor Gray
    Write-Host "   - COMPLETE_LLM_ARCHITECTURE_PRESENTATION.html (HTML)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Total slides: ~130+ slides covering all LLM components" -ForegroundColor White
}
catch {
    Write-Host "❌ Marp CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g @marp-team/marp-cli" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📁 Combined Markdown file created: $CombinedFile" -ForegroundColor Green
    Write-Host "   You can manually generate PDF/HTML using Marp after installation." -ForegroundColor Gray
}
