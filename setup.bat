@echo off
REM Script de configuration de l'environnement virtuel pour Windows
REM Crée et configure l'environnement virtuel Python pour le projet

echo Configuration de l'environnement virtuel Python
echo ================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installe. Veuillez l'installer d'abord.
    exit /b 1
)

python --version
echo.

REM Nom de l'environnement virtuel
set VENV_NAME=venv

REM Vérifier si l'environnement virtuel existe déjà
if exist "%VENV_NAME%" (
    echo [WARN] L'environnement virtuel '%VENV_NAME%' existe deja.
    set /p RECREATE="Voulez-vous le recréer ? (O/N) "
    if /i "%RECREATE%"=="O" (
        echo Suppression de l'ancien environnement virtuel...
        rmdir /s /q "%VENV_NAME%"
    ) else (
        echo [INFO] Utilisation de l'environnement virtuel existant.
        echo.
        echo [OK] Pour activer l'environnement virtuel, executez :
        echo    %VENV_NAME%\Scripts\activate
        exit /b 0
    )
)

REM Créer l'environnement virtuel
echo Creation de l'environnement virtuel '%VENV_NAME%'...
python -m venv "%VENV_NAME%"

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call "%VENV_NAME%\Scripts\activate.bat"

REM Mettre à jour pip
echo Mise a jour de pip...
python -m pip install --upgrade pip

REM Installer les dépendances
echo Installation des dependances depuis requirements.txt...
pip install -r requirements.txt

echo.
echo [OK] Configuration terminee avec succes !
echo.
echo Pour activer l'environnement virtuel, executez :
echo    %VENV_NAME%\Scripts\activate
echo.
echo Pour desactiver l'environnement virtuel, executez :
echo    deactivate
echo.
echo Pour demarrer les services, executez :
echo    python app.py          # API REST
echo    python graphql_server.py  # Serveur GraphQL
echo.

