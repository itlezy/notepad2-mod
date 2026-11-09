Scintilla vendor baseline: 3.7.6 (LongTerm3)

Source: https://www.scintilla.org/scintilla376.zip
Archive SHA256:
4FEFB8B4D4A4A66801A26B1F6258BBBAB5077BEFB984ADDBEDF23FB086CBC3CA

This is a reduced Windows source bundle, with Notepad2-mod customizations.
The 3.7.5 -> 3.7.6 update applies the upstream LexBaan.cxx fix and version
change. The other upstream changes concern omitted Cocoa code and Mercurial
metadata. Neither common editor code nor Windows code changed upstream.

Preserved differences from stock 3.7.6:
- lexers/LexAHK.cxx: custom AutoHotkey lexer.
- include/SciLexer.h and include/Scintilla.iface: AutoHotkey constants.
- src/Catalogue.cxx: selected lexer registrations, including AutoHotkey.
- src/Editor.cxx: Alt+arrow notifications for folding keyboard commands.
- scripts/LexGen.py: disabled regeneration of omitted build/platform files
  and headers. The root lexlink.js also filters lexer registrations.
- Scintilla.vcxproj and Scintilla.vcxproj.filters: fork-specific build files;
  the project is locally retargeted to VS 2022 / v143.
- src/UniConversion.h: explicit <string> include for the current compiler.

Do not replace this directory with an unmodified upstream archive: preserve
these changes and the deliberately reduced source/build layout.
