from pydantic import BaseModel, Field
from typing import List, Optional

# Estrutura de dados de auditoria e vulnerabilidades retornada na API
class AuditoriaViewSchema(BaseModel):
    id: Optional[int] = None
    cve_id: str = Field(..., description="Código identificador do CVE")
    descricao: str = Field(..., description="Resumo técnico da vulnerabilidade")
    cvss_score: Optional[str] = Field(None, description="Pontuação de gravidade CVSS")

# Validação do payload para cadastro de um novo ativo (POST /ativo)
class AtivoSchema(BaseModel):
    tag_patrimonio: str = Field(..., description="Tag única de património")
    categoria: str = Field(..., description="Categoria do equipamento: Workstation ou Servidor")
    fabricante: str = Field(..., description="Fabricante da CPU: AMD ou Intel")
    cpu: str = Field(..., description="Modelo do processador")
    gpu: str = Field(..., description="Modelo da placa gráfica")
    memoria_ram: int = Field(..., description="Quantidade de memória RAM em GB")
    armazenamento_primario: str = Field(..., description="Unidade de armazenamento principal")
    versao_bios: str = Field(..., description="Versão da BIOS da placa-mãe")
    versao_microcodigo: str = Field(..., description="Versão AGESA (AMD) ou Microcódigo MCU (Intel)")

# Dados necessários para atualização de firmware/microcódigo (PUT /ativo)
class AtivoUpdateSchema(BaseModel):
    tag_patrimonio: str = Field(..., description="Tag de património do ativo a atualizar")
    nova_versao_bios: Optional[str] = Field(None, description="Nova versão de BIOS")
    nova_versao_microcodigo: Optional[str] = Field(None, description="Nova versão de AGESA ou MCU")

# Parâmetro de busca para consulta ou exclusão de ativo (DELETE /ativo)
class AtivoBuscaSchema(BaseModel):
    tag_patrimonio: str = Field(..., description="Tag de património do ativo a consultar ou remover")

# Estrutura completa de retorno de um ativo individual
class AtivoViewSchema(BaseModel):
    id: int
    tag_patrimonio: str
    categoria: str
    fabricante: str
    cpu: str
    gpu: str
    memoria_ram: int
    armazenamento_primario: str
    versao_bios: str
    versao_microcodigo: str
    auditorias: List[AuditoriaViewSchema] = []

# Estrutura de resposta da listagem de ativos (GET /ativos)
class ListaAtivosViewSchema(BaseModel):
    ativos: List[AtivoViewSchema]

# Alias mantido para compatibilidade de rotas anteriores
AtivoHardwareSchema = AtivoSchema