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


class PedidosConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = 'queue_pedidos'
        
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
                
                logger.info(f"✅ Consumer de Pedidos conectado à fila '{self.queue_name}'")
                return True
                
            except Exception as e:
                logger.error(f"❌ Falha ao conectar ao RabbitMQ: {e}")
                logger.info("🔄 Tentando reconectar em 5 segundos...")
                time.sleep(5)
    
    def process_pedido(self, message):
        """Processa um pedido"""
        try:
            pedido_id = message.get('pedido_id')
            cliente = message.get('cliente')
            itens = message.get('itens', [])
            valor_total = message.get('valor_total', 0)
            status = message.get('status', 'pendente')
            
            logger.info(f"🛒 Processando Pedido #{pedido_id}")
            logger.info(f"   Cliente: {cliente}")
            logger.info(f"   Itens: {len(itens)} itens")
            logger.info(f"   Valor Total: R$ {valor_total:.2f}")
            logger.info(f"   Status: {status}")
            
            # Simular etapas de processamento do pedido
            logger.info("   📦 Separando itens do estoque...")
            time.sleep(1)
            
            logger.info("   🏷️ Gerando etiquetas de envio...")
            time.sleep(0.5)
            
            logger.info("   📋 Atualizando sistema de inventário...")
            time.sleep(0.5)
            
            # Atualizar status do pedido (em um sistema real, salvaria no banco)
            new_status = "processado"
            logger.info(f"   ✅ Pedido #{pedido_id} {new_status.upper()} com sucesso")
            
            # Gerar comprovante
            recibo = {
                "pedido_id": pedido_id,
                "cliente": cliente,
                "itens": itens,
                "valor_total": valor_total,
                "status": new_status,
                "data_processamento": datetime.now().isoformat(),
                "recibo_id": f"REC-{pedido_id}-{int(time.time())}"
            }
            
            logger.info(f"   🧾 Comprovante gerado: {recibo['recibo_id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar pedido: {e}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Callback chamado quando uma mensagem é recebida"""
        try:
            message = json.loads(body.decode())
            
            if self.process_pedido(message):
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"✅ Pedido {message.get('pedido_id')} processado com sucesso")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Reenfileira em caso de falha
                logger.error(f"❌ Falha no processamento do pedido {message.get('pedido_id')}. Reenfileirando...")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao decodificar JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"❌ Erro inesperado no callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Inicia o consumo de mensagens"""
        if not self.connect():
            logger.error("❌ Não foi possível iniciar o consumer de pedidos")
            return
        
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False
            )
            
            logger.info("🔄 Pedidos Consumer aguardando mensagens...")
            logger.info("Pressione CTRL+C para sair")
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("👋 Encerrando Pedidos Consumer...")
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"❌ Erro no consumer de pedidos: {e}")
            if self.connection:
                self.connection.close()


if __name__ == "__main__":
    consumer = PedidosConsumer()
    consumer.start_consuming()