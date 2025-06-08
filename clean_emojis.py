#!/usr/bin/env python3

# Script pour nettoyer les emojis du fichier interface_test_superwhisper.py

import re

# Mappings des emojis vers des équivalents ASCII
emoji_replacements = {
    "🚀": "[INIT]", "⚡": "[FAST]", "✅": "[OK]", "❌": "[ERR]", 
    "🔧": "[CONF]", "🎮": "[GPU]", "📊": "[STAT]", "⏳": "[WAIT]",
    "🔄": "[REFRESH]", "🌊": "[STREAM]", "🎙️": "[MIC]", "🛑": "[STOP]",
    "📝": "[TEXT]", "⏱️": "[TIME]", "🚫": "[BLOCK]", "🎤": "[AUDIO]",
    "📋": "[COPY]", "🔥": "[HOT]", "💾": "[SAVE]", "⚠️": "[WARN]",
    "⏹️": "[STOP]", "📖": "[READ]", "🧠": "[AI]", "🎯": "[TARGET]"
}

def clean_file():
    with open('interface_test_superwhisper.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer tous les emojis
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Remplacer d'autres caractères Unicode problématiques
    content = content.replace('é', 'e')
    content = content.replace('è', 'e')
    content = content.replace('à', 'a')
    content = content.replace('ç', 'c')
    content = content.replace('ù', 'u')
    content = content.replace('ô', 'o')
    content = content.replace('â', 'a')
    content = content.replace('ê', 'e')
    content = content.replace('î', 'i')
    content = content.replace('û', 'u')
    content = content.replace('ë', 'e')
    content = content.replace('ï', 'i')
    content = content.replace('ü', 'u')
    content = content.replace('ö', 'o')
    content = content.replace('ä', 'a')
    content = content.replace('œ', 'oe')
    
    with open('interface_test_superwhisper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Nettoyage des emojis terminé!")

if __name__ == "__main__":
    clean_file() 