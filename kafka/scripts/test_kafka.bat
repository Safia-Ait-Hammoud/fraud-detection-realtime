@echo off
set TOPIC_NAME=bank-transactions

echo Verification de la connexion au Broker Kafka (localhost:9092)...
cd C:\kafka
bin\windows\kafka-broker-api-versions.bat --bootstrap-server localhost:9092 | findstr "id:"

echo ---------------------------------------------------
echo Etat de sante du topic '%TOPIC_NAME%' :
bin\windows\kafka-topics.bat --describe --bootstrap-server localhost:9092 --topic %TOPIC_NAME%
pause