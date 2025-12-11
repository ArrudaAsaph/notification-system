import pika
import json
import logging
import time
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdminConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = 'queue_admin'
        
    def connect(self):
        """Estabelece conexão com RabbitMQ"""
        credentials = pika.PlainCredentials(
            username=os.getenv('RABBITMQ_USER', 'admin'),
            password=os.getenv('RABBITMQ_PASSWORD', 'admin123')
        )
        
        while True:
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
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                self.channel.basic_qos(prefetch_count=1)
                
                logger.info(f"✅ Consumer Administrativo conectado à fila '{self.queue_name}'")
                return True
                
            except Exception as e:
                logger.error(f"❌ Falha ao conectar ao RabbitMQ: {e}")
                logger.info("🔄 Tentando reconectar em 5 segundos...")
                time.sleep(5)
    
    def process_admin_notification(self, message):
        """Processa notificações administrativas"""
        try:
            action = message.get('action', 'unknown').upper()
            user = message.get('user', 'unknown')
            severity = message.get('severity', 'info')
            details = message.get('details', '')
            
            logger.info(f"📊 Notificação Administrativa Recebida:")
            logger.info(f"   Ação: {action}")
            logger.info(f"   Usuário: {user}")
            logger.info(f"   Severidade: {severity}")
            logger.info(f"   Detalhes: {details}")
            
            # Registrar no log com formatação apropriada
            log_message = f"[{action}] User: {user} - {details}"
            
            if severity == 'error' or severity == 'critical':
                logger.error(log_message)
                # Aqui poderia enviar para um serviço de monitoramento (Sentry, etc.)
            elif severity == 'warning':
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            # Simular processamento adicional
            time.sleep(0.5)
            
            logger.info(f"✅ Notificação administrativa processada: {message.get('message_id')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar notificação administrativa: {e}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Callback chamado quando uma mensagem é recebida"""
        try:
            message = json.loads(body.decode())
            
            if self.process_admin_notification(message):
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao decodificar JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"❌ Erro inesperado no callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Inicia o consumo de mensagens"""
        if not self.connect():
            logger.error("❌ Não foi possível iniciar o consumer administrativo")
            return
        
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False
            )
            
            logger.info("🔄 Admin Consumer aguardando mensagens...")
            logger.info("Pressione CTRL+C para sair")
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("👋 Encerrando Admin Consumer...")
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"❌ Erro no consumer administrativo: {e}")
            if self.connection:
                self.connection.close()


if __name__ == "__main__":
    consumer = AdminConsumer()
    consumer.start_consuming()