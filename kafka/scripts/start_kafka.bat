@echo off
echo =========================================
echo Demarrage de l'infrastructure Kafka
echo =========================================

:: 1. Démarrage de Zookeeper
echo [1/2] Lancement de Zookeeper...
start "Zookeeper" cmd /k "cd C:\kafka && bin\windows\zookeeper-server-start.bat config\zookeeper.properties"

:: Pause pour laisser Zookeeper s'allumer
timeout /t 5 /nobreak > NUL

:: 2. Démarrage du Broker avec notre configuration
echo [2/2] Lancement du Broker Kafka...
set PROJECT_DIR=%~dp0..\..
start "Kafka Broker" cmd /k "cd C:\kafka && bin\windows\kafka-server-start.bat "%PROJECT_DIR%\kafka\config\server.properties""

echo Les serveurs sont lances !
pause