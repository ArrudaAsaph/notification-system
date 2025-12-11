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


class EmailConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = 'queue_email'
        
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
                
                # Configurar QoS para processar uma mensagem por vez
                self.channel.basic_qos(prefetch_count=1)
                
                logger.info(f"✅ Consumer de Email conectado à fila '{self.queue_name}'")
                return True
                
            except Exception as e:
                logger.error(f"❌ Falha ao conectar ao RabbitMQ: {e}")
                logger.info("🔄 Tentando reconectar em 5 segundos...")
                time.sleep(5)
    
    def process_email(self, message):
        """Simula o processamento de um email"""
        try:
            logger.info(f"📧 Processando email para: {message.get('to')}")
            logger.info(f"   Assunto: {message.get('subject')}")
            logger.info(f"   Prioridade: {message.get('priority', 'normal')}")
            logger.info(f"   ID da mensagem: {message.get('message_id')}")
            
            # Simular envio de email (em produção, integrar com SendGrid, SMTP, etc.)
            time.sleep(1)  # Simular tempo de processamento
            
            logger.info(f"✅ Email enviado com sucesso para {message.get('to')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar email: {e}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Callback chamado quando uma mensagem é recebida"""
        try:
            message = json.loads(body.decode())
            logger.info(f"📥 Nova mensagem recebida na fila de emails")
            
            if self.process_email(message):
                # Confirma o processamento da mensagem
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"✅ Mensagem {message.get('message_id')} processada com sucesso")
            else:
                # Rejeita a mensagem (não será reenfileirada)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                logger.error(f"❌ Falha no processamento da mensagem {message.get('message_id')}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao decodificar JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"❌ Erro inesperado no callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Inicia o consumo de mensagens"""
        if not self.connect():
            logger.error("❌ Não foi possível iniciar o consumer")
            return
        
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False  # Confirmação manual
            )
            
            logger.info("🔄 Email Consumer aguardando mensagens...")
            logger.info("Pressione CTRL+C para sair")
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("👋 Encerrando Email Consumer...")
            self.connection.close()
        except Exception as e:
            logger.error(f"❌ Erro no consumer: {e}")
            self.connection.close()


if __name__ == "__main__":
    consumer = EmailConsumer()
    consumer.start_consuming()