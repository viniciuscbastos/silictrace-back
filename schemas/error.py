from pydantic import BaseModel, Field

# Schema padrão para retorno de mensagens de erro da API
class MensagemErroSchema(BaseModel):
    mensagem: str = Field(..., description="Descrição do erro ocorrido")

# Aliases mantidos para compatibilidade com versões anteriores
ErrorSchema = MensagemErroSchema
ErrorViewSchema = MensagemErroSchema