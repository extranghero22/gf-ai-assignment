#!/bin/bash

# Combine all Marp slide files into one comprehensive presentation
# and generate as PDF

echo "🔄 Combining all slide files into one presentation..."

# Create the combined presentation file
COMBINED_FILE="COMPLETE_LLM_ARCHITECTURE_PRESENTATION.md"

# Start with the main architecture slides
echo "📊 Adding main architecture overview..."
cp LLM_ARCHITECTURE_SLIDES.md "$COMBINED_FILE"

# Add separator and component slides
echo "🔋 Adding Energy Analyzer slides..."
echo "" >> "$COMBINED_FILE"
echo "---" >> "$COMBINED_FILE"
echo "" >> "$COMBINED_FILE"
cat ENERGY_ANALYZER_SLIDES.md >> "$COMBINED_FILE"

echo "🛡️ Adding Safety Monitor slides..."
echo "" >> "$COMBINED_FILE"
echo "---" >> "$COMBINED_FILE"
echo "" >> "$COMBINED_FILE"
cat SAFETY_MONITOR_SLIDES.md >> "$COMBINED_FILE"

echo "🔍 Adding Response Analyzer slides..."
echo "" >> "$COMBINED_FILE"
echo "---" >> "$COMBINED_FILE"
echo "" >> "$COMBINED_FILE"
cat RESPONSE_ANALYZER_SLIDES.md >> "$COMBINED_FILE"

echo "💕 Adding Girlfriend Agent slides..."
echo "" >> "$COMBINED_FILE"
echo "---" >> "$COMBINED_FILE"
echo "" >> "$COMBINED_FILE"
cat GIRLFRIEND_AGENT_SLIDES.md >> "$COMBINED_FILE"

echo "📖 Adding Script Manager slides..."
echo "" >> "$COMBINED_FILE"
echo "---" >> "$COMBINED_FILE"
echo "" >> "$COMBINED_FILE"
cat SCRIPT_MANAGER_SLIDES.md >> "$COMBINED_FILE"

echo "✅ Combined presentation created: $COMBINED_FILE"

# Generate PDF from the combined file
echo "📄 Generating PDF presentation..."
marp "$COMBINED_FILE" --pdf --output "COMPLETE_LLM_ARCHITECTURE_PRESENTATION.pdf"

# Also generate HTML version
echo "🌐 Generating HTML presentation..."
marp "$COMBINED_FILE" --html --output "COMPLETE_LLM_ARCHITECTURE_PRESENTATION.html"

echo "🎉 Complete presentation generated successfully!"
echo ""
echo "📁 Files created:"
echo "   - $COMBINED_FILE (Combined Markdown)"
echo "   - COMPLETE_LLM_ARCHITECTURE_PRESENTATION.pdf (PDF)"
echo "   - COMPLETE_LLM_ARCHITECTURE_PRESENTATION.html (HTML)"
echo ""
echo "📊 Total slides: ~130+ slides covering all LLM components"
