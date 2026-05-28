@echo off
set TOPIC_NAME=bank-transactions

echo Creation du topic '%TOPIC_NAME%'...
cd C:\kafka
bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic %TOPIC_NAME%

echo Topic cree. Liste des topics actifs :
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
pause