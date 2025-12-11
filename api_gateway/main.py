from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging
from datetime import datetime
from rabbitmq_client import rabbitmq_client
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Modelos Pydantic
class EmailNotification(BaseModel):
    to: EmailStr
    subject: str
    body: str
    template: Optional[str] = None
    priority: Optional[str] = "normal"


class AdminNotification(BaseModel):
    action: str
    user: str
    details: str
    severity: Optional[str] = "info"  # info, warning, error, critical


class Pedido(BaseModel):
    pedido_id: str
    cliente: str
    itens: List[str]
    valor_total: float
    status: Optional[str] = "pendente"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Inicialização
    logger.info("🚀 Iniciando Notification System API Gateway...")
    if rabbitmq_client.connect():
        logger.info("✅ Sistema pronto para receber notificações")
    else:
        logger.error("❌ Falha crítica: Não foi possível conectar ao RabbitMQ")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando Notification System...")
    rabbitmq_client.close()


app = FastAPI(
    title="Notification System API Gateway",
    description="Sistema de mensageria assíncrona com RabbitMQ",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Endpoint de saúde da API"""
    return {
        "status": "online",
        "service": "Notification System API Gateway",
        "rabbitmq_connected": rabbitmq_client.connected,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Verifica saúde do sistema"""
    status_code = status.HTTP_200_OK if rabbitmq_client.connected else status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "api": "healthy",
        "rabbitmq": "connected" if rabbitmq_client.connected else "disconnected",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/notify/email", status_code=status.HTTP_202_ACCEPTED)
async def notify_email(email: EmailNotification):
    """
    Envia notificação por email de forma assíncrona
    
    - **to**: Email do destinatário
    - **subject**: Assunto do email
    - **body**: Corpo da mensagem
    - **template**: Template opcional
    - **priority**: Prioridade (normal, alta)
    """
    try:
        message = {
            **email.dict(),
            "type": "email",
            "timestamp": datetime.now().isoformat(),
            "message_id": f"email_{datetime.now().timestamp()}"
        }
        
        if rabbitmq_client.publish_message('queue_email', message):
            return {
                "status": "accepted",
                "message": "Email enqueued for processing",
                "queue": "queue_email",
                "message_id": message["message_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to publish message to queue"
            )
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /notify/email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/notify/admin", status_code=status.HTTP_202_ACCEPTED)
async def notify_admin(notification: AdminNotification):
    """
    Envia notificação administrativa de forma assíncrona
    
    - **action**: Ação realizada (login, logout, create, delete, update)
    - **user**: Usuário que realizou a ação
    - **details**: Detalhes da ação
    - **severity**: Severidade (info, warning, error, critical)
    """
    try:
        message = {
            **notification.dict(),
            "type": "admin",
            "timestamp": datetime.now().isoformat(),
            "message_id": f"admin_{datetime.now().timestamp()}"
        }
        
        if rabbitmq_client.publish_message('queue_admin', message):
            return {
                "status": "accepted",
                "message": "Admin notification enqueued",
                "queue": "queue_admin",
                "message_id": message["message_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to publish message to queue"
            )
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /notify/admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/pedidos", status_code=status.HTTP_202_ACCEPTED)
async def criar_pedido(pedido: Pedido):
    """
    Processa um novo pedido de forma assíncrona
    
    - **pedido_id**: ID único do pedido
    - **cliente**: Nome do cliente
    - **itens**: Lista de itens do pedido
    - **valor_total**: Valor total do pedido
    - **status**: Status inicial do pedido
    """
    try:
        message = {
            **pedido.dict(),
            "type": "pedido",
            "timestamp": datetime.now().isoformat(),
            "message_id": f"pedido_{pedido.pedido_id}"
        }
        
        if rabbitmq_client.publish_message('queue_pedidos', message):
            return {
                "status": "accepted",
                "message": "Pedido enqueued for processing",
                "queue": "queue_pedidos",
                "pedido_id": pedido.pedido_id,
                "valor_total": pedido.valor_total
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to publish pedido to queue"
            )
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /pedidos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)