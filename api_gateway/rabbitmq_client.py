import pika
import json
import logging
import time
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connected = False
        
    def connect(self, max_retries=5, retry_delay=5):
        """Estabelece conexão com RabbitMQ com tentativas de reconexão"""
        credentials = pika.PlainCredentials(
            username=os.getenv('RABBITMQ_USER', 'admin'),
            password=os.getenv('RABBITMQ_PASSWORD', 'admin123')
        )
        
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                        port=int(os.getenv('RABBITMQ_PORT', 5672)),
                        credentials=credentials,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                
                self.channel = self.connection.channel()
                
                # Declarar filas duráveis
                self.channel.queue_declare(queue='queue_email', durable=True)
                self.channel.queue_declare(queue='queue_admin', durable=True)
                self.channel.queue_declare(queue='queue_pedidos', durable=True)
                
                self.connected = True
                logger.info("✅ Conectado ao RabbitMQ com sucesso")
                return True
                
            except Exception as e:
                logger.error(f"❌ Tentativa {attempt + 1}/{max_retries}: Falha ao conectar ao RabbitMQ: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        return False
    
    def publish_message(self, queue_name: str, message: Dict[str, Any]):
        """Publica uma mensagem na fila especificada"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Não foi possível conectar ao RabbitMQ")
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Torna a mensagem persistente
                    content_type='application/json'
                )
            )
            logger.info(f"📤 Mensagem publicada na fila '{queue_name}': {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao publicar mensagem: {e}")
            # Tentar reconectar e reenviar
            self.connected = False
            if self.connect():
                return self.publish_message(queue_name, message)
            return False
    
    def close(self):
        """Fecha a conexão com RabbitMQ"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("🔌 Conexão com RabbitMQ fechada")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar conexão: {e}")


# Instância global do cliente RabbitMQ
rabbitmq_client = RabbitMQClient()