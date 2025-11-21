#!/bin/bash
echo "🔧 Combining all script parts into FULL_ACKWARE.py..."

# Combine all parts
cat main.py APPEND_TO_MAIN.py UI_SECTION.py > FULL_ACKWARE.py

# Count lines
LINES=$(wc -l < FULL_ACKWARE.py)

echo "✅ Complete script created!"
echo "📄 File: FULL_ACKWARE.py"
echo "📊 Total lines: $LINES"
echo ""
echo "🎯 All features included:"
echo "   ✅ Remember Me for KeyAuth Login"
echo "   ✅ Silent Aim (no mouse movement)"
echo "   ✅ Mouse-Following FOV Circle"
echo "   ✅ All original aimbot/ESP/triggerbot features"
echo "   ✅ Complete movement system"
echo "   ✅ Spectate & teleport"
echo "   ✅ Full UI with all panels"
echo ""
echo "▶️  To use: python FULL_ACKWARE.py"
