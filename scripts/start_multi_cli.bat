@echo off
REM Multi-CLI Personal AI Employee Startup Script for Windows
REM Supports Claude, Qwen, and Codex with automatic fallback

setlocal enabledelayedexpansion

REM Default values
set VAULT_PATH=.\vault
set DRY_RUN=true
set PRIMARY_CLI=claude
set ENABLE_FALLBACK=true
set TEST_ONLY=false

REM Colors (limited in Windows batch)
set INFO=[INFO]
set SUCCESS=[SUCCESS]
set WARNING=[WARNING]
set ERROR=[ERROR]

echo %INFO% Starting Multi-CLI Personal AI Employee for Windows

REM Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--vault" (
    set VAULT_PATH=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--live" (
    set DRY_RUN=false
    shift
    goto parse_args
)
if "%~1"=="--primary-cli" (
    set PRIMARY_CLI=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--force-cli" (
    set PRIMARY_CLI=%~2
    set ENABLE_FALLBACK=false
    shift
    shift
    goto parse_args
)
if "%~1"=="--no-fallback" (
    set ENABLE_FALLBACK=false
    shift
    goto parse_args
)
if "%~1"=="--test-only" (
    set TEST_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Multi-CLI Personal AI Employee Startup Script for Windows
    echo.
    echo Usage: %0 [OPTIONS]
    echo.
    echo Options:
    echo   --vault PATH          Path to vault directory (default: .\vault)
    echo   --live                Run in live mode (default: dry-run)
    echo   --primary-cli CLI     Primary CLI to use (claude^|qwen^|codex)
    echo   --force-cli CLI       Force specific CLI, disable fallback
    echo   --no-fallback         Disable automatic fallback
    echo   --test-only           Only test CLIs and exit
    echo   --help                Show this help message
    echo.
    echo Examples:
    echo   %0 --vault .\vault --live --primary-cli claude
    echo   %0 --force-cli qwen --vault .\vault
    echo   %0 --test-only
    exit /b 0
)
echo %ERROR% Unknown option: %~1
exit /b 1

:end_parse

echo %INFO% Vault: %VAULT_PATH%
if "%DRY_RUN%"=="true" (
    echo %INFO% Mode: DRY-RUN
) else (
    echo %INFO% Mode: LIVE
)
echo %INFO% Primary CLI: %PRIMARY_CLI%
if "%ENABLE_FALLBACK%"=="true" (
    echo %INFO% Fallback: ENABLED
) else (
    echo %INFO% Fallback: DISABLED
)

REM Check Python dependencies
echo %INFO% Checking Python dependencies...
python -c "import sys; sys.path.append('scripts'); from multi_cli_manager import MultiCLIManager" >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Multi-CLI system not available. Please check scripts\multi_cli_manager.py
    exit /b 1
)
echo %SUCCESS% Python dependencies OK

REM Check available CLIs
echo %INFO% Checking available CLIs...
set CLAUDE_AVAILABLE=false
set QWEN_AVAILABLE=false
set CODEX_AVAILABLE=false

REM Check Claude
claude.exe --version >nul 2>&1
if not errorlevel 1 (
    echo %SUCCESS% Claude CLI found
    set CLAUDE_AVAILABLE=true
) else (
    claude --version >nul 2>&1
    if not errorlevel 1 (
        echo %SUCCESS% Claude CLI found
        set CLAUDE_AVAILABLE=true
    ) else (
        echo %WARNING% Claude CLI not found
    )
)

REM Check Qwen
qwen.exe --help >nul 2>&1
if not errorlevel 1 (
    echo %SUCCESS% Qwen CLI found
    set QWEN_AVAILABLE=true
) else (
    qwen --help >nul 2>&1
    if not errorlevel 1 (
        echo %SUCCESS% Qwen CLI found
        set QWEN_AVAILABLE=true
    ) else (
        echo %WARNING% Qwen CLI not found
    )
)

REM Check GitHub Copilot
gh.exe copilot --version >nul 2>&1
if not errorlevel 1 (
    echo %SUCCESS% GitHub Copilot CLI found
    set CODEX_AVAILABLE=true
) else (
    gh copilot --version >nul 2>&1
    if not errorlevel 1 (
        echo %SUCCESS% GitHub Copilot CLI found
        set CODEX_AVAILABLE=true
    ) else (
        echo %WARNING% GitHub Copilot CLI not found
        echo %INFO% Install with: gh extension install github/gh-copilot
    )
)

REM Check if at least one CLI is available
if "%CLAUDE_AVAILABLE%"=="false" if "%QWEN_AVAILABLE%"=="false" if "%CODEX_AVAILABLE%"=="false" (
    echo %ERROR% No CLIs available! Please install at least one:
    echo   - Claude CLI: Follow Claude Code installation guide
    echo   - Qwen CLI: pip install qwen-cli
    echo   - GitHub Copilot: gh extension install github/gh-copilot
    exit /b 1
)

REM Test CLIs if requested
if "%TEST_ONLY%"=="true" (
    echo %INFO% Testing CLI functionality...
    python scripts\multi_cli_manager.py --test
    exit /b 0
)

REM Create vault directories
echo %INFO% Setting up vault structure...
if not exist "%VAULT_PATH%" mkdir "%VAULT_PATH%"
if not exist "%VAULT_PATH%\Needs_Action" mkdir "%VAULT_PATH%\Needs_Action"
if not exist "%VAULT_PATH%\Plans" mkdir "%VAULT_PATH%\Plans"
if not exist "%VAULT_PATH%\Done" mkdir "%VAULT_PATH%\Done"
if not exist "%VAULT_PATH%\Pending_Approval" mkdir "%VAULT_PATH%\Pending_Approval"
if not exist "%VAULT_PATH%\Approved" mkdir "%VAULT_PATH%\Approved"
if not exist "%VAULT_PATH%\Rejected" mkdir "%VAULT_PATH%\Rejected"
if not exist "%VAULT_PATH%\Logs" mkdir "%VAULT_PATH%\Logs"
if not exist "%VAULT_PATH%\config" mkdir "%VAULT_PATH%\config"
echo %SUCCESS% Vault structure ready

REM Check quota status
echo %INFO% Checking quota status...
python scripts\quota_manager.py --best-cli > temp_cli.txt
set /p RECOMMENDED_CLI=<temp_cli.txt
del temp_cli.txt
echo %INFO% Recommended CLI: !RECOMMENDED_CLI!

REM Build orchestrator arguments
set ORCHESTRATOR_ARGS=--vault %VAULT_PATH% --primary-cli %PRIMARY_CLI%

if "%DRY_RUN%"=="false" (
    set ORCHESTRATOR_ARGS=!ORCHESTRATOR_ARGS! --live
)

if "%ENABLE_FALLBACK%"=="false" (
    set ORCHESTRATOR_ARGS=!ORCHESTRATOR_ARGS! --force-cli %PRIMARY_CLI%
)

echo %INFO% Starting orchestrator...
echo %INFO% Command: python orchestrator.py !ORCHESTRATOR_ARGS!

REM Start the orchestrator
python orchestrator.py !ORCHESTRATOR_ARGS!

endlocal