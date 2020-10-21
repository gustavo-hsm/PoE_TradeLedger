#!/bin/sh
# Initialize RabbitMQ broker
#docker run -d --hostname rabbitmq --name exchange_api -p 15672:15672 -p 5672:5672 rabbitmq:3-management
docker start d422c4d014cb62aa1185adba80a9cdfc0776503608986768037b998e9f566762

# Initialize venv
source /home/gustavo/Git/VirtualEnvs/PoE_TradeLedger_venv/bin/activate

# Host RPC application
cd /home/gustavo/Git/PoE_TradeLedger/src
nameko run ExchangeBillboard --broker amqp://guest:guest@localhost
