@ECHO OFF
SETLOCAL

PUSHD "%~dp0"

IF EXIST "build.user.bat" (CALL "build.user.bat")

IF DEFINED MSYS SET "PATH=%MSYS%\bin;%PATH%"

rem Prefer Git for Windows Bash over a possible WSL bash.exe on PATH.
FOR /F "delims=" %%G IN ('where git.exe 2^>NUL') DO IF EXIST "%%~dpG..\bin\bash.exe" SET "GIT_BASH=%%~dpG..\bin\bash.exe"
IF DEFINED GIT_BASH GOTO GitBash

GOTO FindBash

:GitBash
"%GIT_BASH%" ./version.sh
SET "BUILD_RESULT=%ERRORLEVEL%"
GOTO END

:FindBash
FOR %%G IN (bash.exe) DO (SET FOUND=%%~$PATH:G)
IF NOT DEFINED FOUND GOTO MissingVar

bash.exe ./version.sh
SET "BUILD_RESULT=%ERRORLEVEL%"
GOTO END


:END
POPD
ENDLOCAL & EXIT /B %BUILD_RESULT%


:MissingVar
ECHO Git for Windows Bash wasn't found. Install Git for Windows or set MSYS in build.user.bat.
ECHO.
ECHO SET "MSYS=H:\progs\MSYS"
ECHO. & ECHO.
SET "BUILD_RESULT=1"
GOTO END
