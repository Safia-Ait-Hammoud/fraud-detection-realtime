# 🚀 Kafka Setup Guide — Windows (WSL2)
# Bank Fraud Detection Project

## ─────────────────────────────────────────────
## STEP 1 — Install WSL2 (if not done yet)
## ─────────────────────────────────────────────
# Open PowerShell as Administrator and run:

wsl --install

# Restart your PC, then open "Ubuntu" from the Start Menu.
wsl -d Ubuntu

## ─────────────────────────────────────────────
## STEP 2 — Install Java inside WSL2/Ubuntu
## ─────────────────────────────────────────────
# Download Java 17 directly
cd ~
wget https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.11%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.11_9.tar.gz

# Extract
tar -xzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.11_9.tar.gz

# Set as default Java
echo 'export JAVA_HOME=~/jdk-17.0.11+9' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Verify — must show version 17
java -version



## ─────────────────────────────────────────────
## STEP 3 — Download & Extract Kafka
## ─────────────────────────────────────────────

cd ~
wget https://downloads.apache.org/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xzf kafka_2.13-3.7.0.tgz
mv kafka_2.13-3.7.0 kafka

# Your Kafka folder is now at: ~/kafka


## ─────────────────────────────────────────────
## STEP 6 — Start Kafka Broker (Terminal 1)
## ─────────────────────────────────────────────
# Open another NEW Ubuntu terminal and run:

cd ~/kafka
bin/kafka-server-start.sh config/server.properties

# Leave this terminal running too!


## ─────────────────────────────────────────────
## STEP 7 — Create the Topic (Terminal 2)
## ─────────────────────────────────────────────
# Open a third Ubuntu terminal and run:

cd ~/kafka
bin/kafka-topics.sh --create \
  --topic bank-transactions \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# Verify it was created:
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# Should print: bank-transactions



## ─────────────────────────────────────────────
## STEP 8 — Copy your project files to WSL2
## ─────────────────────────────────────────────
# Your Windows files are accessible at /mnt/c/ in WSL2
# Example — if your project is at C:\Users\YourName\fraud_project:

cp -r /mnt/c/Users/YourName/fraud_project ~/fraud_project
cd ~/fraud_project

# Make sure your folder structure is:
# fraud_project/
# ├── models/
# │   └── rf_fraud_model.pkl   ← your trained model
# ├── kafka_producer.py
# └── kafka_consumer.py

## ─────────────────────────────────────────────
## STEP 8 — Install Python libraries
## ─────────────────────────────────────────────
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
python3 -m venv venv
source venv/bin/activate
pip install kafka-python joblib scikit-learn numpy pandas
## for both py files in both terminal activate venv 
## ─────────────────────────────────────────────
## STEP 9 — Update stats in kafka_consumer.py
## ─────────────────────────────────────────────
# Open kafka_consumer.py and replace these 3 values
# with the real values from your training data:
#
#   AMOUNT_MEAN  = ???   ← df['amount'].mean()
#   AMOUNT_STD   = ???   ← df['amounnat'].std()
#   AMOUNT_Q75   = ???   ← df['amount'].quantile(0.75)
#   VELOCITY_MED = ???   ← df['velocity_last_24h'].median()
#
# Run this in Python to get them:
#   import pandas as pd
#   df = pd.read_csv('data/raw/credit_card_fraud_10k.csv')
#   print(df['amount'].mean(), df['amount'].std())
#   print(df['amount'].quantile(0.75))
#   print(df['velocity_last_24h'].median())


## ─────────────────────────────────────────────
## STEP 10 — Run Producer & Consumer
## ─────────────────────────────────────────────

# Terminal A — Start the consumer FIRST (it listens):
python kafka_consumer.py

# Terminal B — Start the producer (it sends transactions):
python kafka_producer.py

# You should see real-time fraud scoring like:
# TXN-482910       $543.20   0.8721  🚨 FRAUD
# TXN-173654        $12.50   0.0312  ✅ OK


## ─────────────────────────────────────────────
## TROUBLESHOOTING
## ─────────────────────────────────────────────

# Error: "NoBrokersAvailable"
#   → Kafka broker is not running. Redo Step 5.

# Error: "ModuleNotFoundError: kafka"
#   → Run: pip install kafka-python

# Error: loading pkl model
#   → Make sure models/rf_fraud_model.pkl path is correct
#   → The scikit-learn version must match the one used for training

# Kafka won't start
#   → Check Java: java -version
#   → Make sure Zookeeper is running first (Step 4)
