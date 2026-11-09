"""Compile production MRU functions and source-linked Unicode/startup contracts."""
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def test_native_contracts(request, tmp_path):
    arch = request.config.getoption("--architecture")
    config = request.config.getoption("--configuration")
    for source in (ROOT / "src").iterdir():
        if source.suffix in (".c", ".cpp", ".h"):
            source.read_bytes().decode("utf-8", errors="strict")
    ns = {"m": "http://schemas.microsoft.com/developer/msbuild/2003"}
    project = ET.parse(ROOT / "src/Notepad2.vcxproj")
    compilers = project.findall("m:ItemDefinitionGroup/m:ClCompile", ns)
    assert len(compilers) == 4
    for compiler in compilers:
        options = compiler.findtext("m:AdditionalOptions", namespaces=ns)
        assert "/source-charset:utf-8" in options
        assert "/execution-charset" not in options and "/utf-8" not in options
    source = (ROOT / "src/Notepad2.c").read_text(encoding="utf-8")
    elevation = source[source.index("BOOL RelaunchElevated() {"):]
    show = re.search(r"sei\.nShow\s*=\s*([^;]+);", elevation).group(1)
    edit = (ROOT / "src/Edit.c").read_text(encoding="utf-8")
    punctuation = re.search(r'StrChr\((L"[^"]+"),pszTextW\[i\]\)', edit).group(1)
    (tmp_path / "fork-contracts.h").write_text(
        f"static int StartupShowState(STARTUPINFO si) {{ return {show}; }}\n"
        f"static const wchar_t titlePunctuation[] = {punctuation};\n", encoding="utf-8"
    )
    vswhere = Path(os.environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio/Installer/vswhere.exe"
    vs = subprocess.check_output([
        str(vswhere), "-latest", "-version", "[17.0,18.0)", "-products", "*",
        "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"
    ], text=True).strip()
    assert vs
    runtime = "/MTd" if config == "Debug" else "/MT"
    batch = tmp_path / "run.bat"
    batch.write_text(
        f'@echo off\nchcp 65001 >nul\ncall "{vs}\\Common7\\Tools\\VsDevCmd.bat" -no_logo -arch={arch}\n'
        'if errorlevel 1 exit /b 1\n'
        f'cd /d "{tmp_path}"\n'
        f'cl /nologo /TC {runtime} /Gy /DUNICODE /D_UNICODE /D_CRT_SECURE_NO_WARNINGS /source-charset:utf-8 '
        f'/I"{ROOT / "src"}" /I"{ROOT / "scintilla/include"}" /I"{tmp_path}" '
        f'"{ROOT / "build/test-fork-helpers.c"}" "{ROOT / "src/Helpers.c"}" /Fe:contracts.exe '
        '/link /OPT:REF /INCREMENTAL:NO shlwapi.lib shell32.lib user32.lib comctl32.lib ole32.lib comdlg32.lib gdi32.lib advapi32.lib\n'
        'if errorlevel 1 exit /b 1\ncontracts.exe\nexit /b %errorlevel%\n',
        encoding="utf-8", newline="\r\n"
    )
    result = subprocess.run(["cmd.exe", "/d", "/c", str(batch)], capture_output=True, timeout=60)
    assert result.returncode == 0, (result.stdout + result.stderr).decode("utf-8", errors="replace")
