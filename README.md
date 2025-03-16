sistema de medico ia 


from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import uvicorn
import random
import re
import json
import numpy as np
from enum import Enum
import base64
from io import BytesIO

app = FastAPI(
    title="MediVision Bot API",
    description="API para chatbot médico assistente com análise visual de sinais clínicos",
    version="1.0"
)

# Configuração de CORS para permitir acesso de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums para categorização
class Especialidade(str, Enum):
    CLINICA_GERAL = "Clínica Geral"
    CARDIOLOGIA = "Cardiologia"
    DERMATOLOGIA = "Dermatologia"
    ORTOPEDIA = "Ortopedia"
    NEUROLOGIA = "Neurologia"
    PEDIATRIA = "Pediatria"
    GINECOLOGIA = "Ginecologia"
    UROLOGIA = "Urologia"
    PSIQUIATRIA = "Psiquiatria"
    OFTALMOLOGIA = "Oftalmologia"
    OTORRINOLARINGOLOGIA = "Otorrinolaringologia"
    ENDOCRINOLOGIA = "Endocrinologia"

class Urgencia(str, Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    EMERGENCIA = "Emergência"

class TipoSinalVisual(str, Enum):
    LESAO_PELE = "Lesão de Pele"
    CONJUNTIVITE = "Conjuntivite"
    RASH_CUTANEO = "Rash Cutâneo"
    ICTERICIA = "Icterícia"
    ERUPCAO = "Erupção"
    EDEMA = "Edema"
    CIANOSE = "Cianose"
    PALIDEZ = "Palidez"
    OUTRO = "Outro"

class StatusConsulta(str, Enum):
    AGENDADA = "Agendada"
    CANCELADA = "Cancelada"
    REALIZADA = "Realizada"
    REMARCADA = "Remarcada"

# Modelos Pydantic para dados
class SinalVisual(BaseModel):
    id: str
    tipo: TipoSinalVisual
    descricao: str
    especialidades_relacionadas: List[Especialidade]
    urgencia_sugerida: Urgencia
    caracteristicas_detectaveis: List[str]

class AnaliseImagem(BaseModel):
    sinais_detectados: List[SinalVisual]
    confianca: Dict[str, float]
    recomendacoes: List[str]
    urgencia_avaliada: Urgencia

class Sintoma(BaseModel):
    id: str
    descricao: str
    especialidades_relacionadas: List[Especialidade]
    palavras_chave: List[str]
    urgencia_sugerida: Urgencia

class Paciente(BaseModel):
    id: str
    nome: str
    email: EmailStr
    telefone: str
    data_nascimento: datetime
    genero: str
    historico_medico: Dict[str, Any] = {}
    alergias: List[str] = []
    medicamentos_atuais: List[str] = []

class Medico(BaseModel):
    id: str
    nome: str
    especialidade: Especialidade
    crm: str
    disponibilidade: Dict[str, List[str]]  # dia da semana -> lista de horários

class PreDiagnostico(BaseModel):
    sintomas_relatados: List[str]
    sinais_visuais: List[str] = []
    urgencia_avaliada: Urgencia
    especialidades_sugeridas: List[Especialidade]
    recomendacoes: List[str]
    necessita_atendimento_imediato: bool
    imagens_analisadas: List[str] = []

class Consulta(BaseModel):
    id: str
    paciente_id: str
    medico_id: str
    data_hora: datetime
    motivo: str
    pre_diagnostico: Optional[PreDiagnostico] = None
    status: StatusConsulta = StatusConsulta.AGENDADA
    notas: str = ""

class MensagemUsuario(BaseModel):
    texto: Optional[str] = None
    imagem_base64: Optional[str] = None
    usuario_id: Optional[str] = None
    contexto: Dict[str, Any] = {}

class RespostaChatbot(BaseModel):
    texto: str
    acao_sugerida: Optional[str] = None
    dados_adicionais: Dict[str, Any] = {}
    imagem_analise: Optional[str] = None

# Banco de dados simulado para sinais visuais detectáveis
sinais_visuais_db = [
    {
        "id": "sinal001",
        "tipo": TipoSinalVisual.LESAO_PELE,
        "descricao": "Mancha vermelha elevada na pele",
        "especialidades_relacionadas": [Especialidade.DERMATOLOGIA],
        "urgencia_sugerida": Urgencia.BAIXA,
        "caracteristicas_detectaveis": ["vermelhidão", "elevação", "circunscrita", "borda definida"]
    },
    {
        "id": "sinal002",
        "tipo": TipoSinalVisual.CONJUNTIVITE,
        "descricao": "Vermelhidão nos olhos com secreção",
        "especialidades_relacionadas": [Especialidade.OFTALMOLOGIA],
        "urgencia_sugerida": Urgencia.MEDIA,
        "caracteristicas_detectaveis": ["vermelhidão ocular", "secreção", "inchaço palpebral"]
    },
    {
        "id": "sinal003",
        "tipo": TipoSinalVisual.ICTERICIA,
        "descricao": "Coloração amarelada da pele e olhos",
        "especialidades_relacionadas": [Especialidade.CLINICA_GERAL, Especialidade.CARDIOLOGIA],
        "urgencia_sugerida": Urgencia.ALTA,
        "caracteristicas_detectaveis": ["coloração amarelada", "esclera amarelada", "pele amarelada"]
    },
    {
        "id": "sinal004",
        "tipo": TipoSinalVisual.RASH_CUTANEO,
        "descricao": "Erupção cutânea generalizada",
        "especialidades_relacionadas": [Especialidade.DERMATOLOGIA, Especialidade.CLINICA_GERAL],
        "urgencia_sugerida": Urgencia.MEDIA,
        "caracteristicas_detectaveis": ["múltiplas lesões", "distribuição simétrica", "vermelhidão"]
    },
    {
        "id": "sinal005",
        "tipo": TipoSinalVisual.EDEMA,
        "descricao": "Inchaço de extremidades",
        "especialidades_relacionadas": [Especialidade.CLINICA_GERAL, Especialidade.CARDIOLOGIA],
        "urgencia_sugerida": Urgencia.MEDIA,
        "caracteristicas_detectaveis": ["inchaço", "assimetria", "edema", "deformidade"]
    },
    {
        "id": "sinal006",
        "tipo": TipoSinalVisual.CIANOSE,
        "descricao": "Coloração azulada da pele e mucosas",
        "especialidades_relacionadas": [Especialidade.CARDIOLOGIA, Especialidade.CLINICA_GERAL],
        "urgencia_sugerida": Urgencia.EMERGENCIA,
        "caracteristicas_detectaveis": ["coloração azulada", "lábios azulados", "extremidades azuladas"]
    }
]

# Base de dados simulada de sintomas
sintomas_db = [
    {
        "id": "sint001",
        "descricao": "Dor de cabeça",
        "especialidades_relacionadas": [Especialidade.CLINICA_GERAL, Especialidade.NEUROLOGIA],
        "palavras_chave": ["cabeça", "dor", "enxaqueca", "cefaleia"],
        "urgencia_sugerida": Urgencia.BAIXA
    },
    {
        "id": "sint002",
        "descricao": "Dor no peito",
        "especialidades_relacionadas": [Especialidade.CARDIOLOGIA],
        "palavras_chave": ["peito", "dor", "coração", "angina"],
        "urgencia_sugerida": Urgencia.ALTA
    },
    {
        "id": "sint003",
        "descricao": "Manchas na pele",
        "especialidades_relacionadas": [Especialidade.DERMATOLOGIA],
        "palavras_chave": ["pele", "mancha", "alergia", "coceira"],
        "urgencia_sugerida": Urgencia.BAIXA
    },
    {
        "id": "sint004",
        "descricao": "Febre alta",
        "especialidades_relacionadas": [Especialidade.CLINICA_GERAL, Especialidade.PEDIATRIA],
        "palavras_chave": ["febre", "temperatura", "calafrio"],
        "urgencia_sugerida": Urgencia.MEDIA
    },
    {
        "id": "sint005",
        "descricao": "Dificuldade para respirar",
        "especialidades_relacionadas": [Especialidade.CLINICA_GERAL, Especialidade.CARDIOLOGIA],
        "palavras_chave": ["respirar", "falta de ar", "sufoco", "dispneia"],
        "urgencia_sugerida": Urgencia.ALTA
    }
]

# Base de dados simulada de médicos
medicos_db = [
    {
        "id": "med001",
        "nome": "Dr. Carlos Silva",
        "especialidade": Especialidade.CLINICA_GERAL,
        "crm": "12345-SP",
        "disponibilidade": {
            "segunda": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
            "terça": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
            "quarta": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
            "quinta": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
            "sexta": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
        }
    },
    {
        "id": "med002",
        "nome": "Dra. Ana Oliveira",
        "especialidade": Especialidade.CARDIOLOGIA,
        "crm": "23456-SP",
        "disponibilidade": {
            "segunda": ["13:00", "14:00", "15:00", "16:00"],
            "quarta": ["08:00", "09:00", "10:00", "11:00"],
            "sexta": ["13:00", "14:00", "15:00", "16:00"]
        }
    },
    {
        "id": "med003",
        "nome": "Dr. Marcos Souza",
        "especialidade": Especialidade.DERMATOLOGIA,
        "crm": "34567-SP",
        "disponibilidade": {
            "terça": ["13:00", "14:00", "15:00", "16:00"],
            "quinta": ["08:00", "09:00", "10:00", "11:00"]
        }
    },
    {
        "id": "med004",
        "nome": "Dra. Luciana Santos",
        "especialidade": Especialidade.PEDIATRIA,
        "crm": "45678-SP",
        "disponibilidade": {
            "segunda": ["08:00", "09:00", "10:00", "11:00"],
            "quarta": ["13:00", "14:00", "15:00", "16:00"],
            "sexta": ["08:00", "09:00", "10:00", "11:00"]
        }
    },
    {
        "id": "med005",
        "nome": "Dr. Roberto Mendes",
        "especialidade": Especialidade.OFTALMOLOGIA,
        "crm": "56789-SP",
        "disponibilidade": {
            "terça": ["08:00", "09:00", "10:00", "11:00"],
            "quinta": ["13:00", "14:00", "15:00", "16:00"]
        }
    }
]

pacientes_db = []
consultas_db = []
analises_imagem_db = []

# Respostas do chatbot
respostas_chatbot = {
    "saudacao": [
        "Olá! Sou o MediVision Bot, seu assistente médico virtual com análise visual. Como posso ajudar você hoje?",
        "Bem-vindo ao MediVision Bot! Estou aqui para auxiliar com suas dúvidas médicas e posso analisar imagens para identificar possíveis condições. Em que posso ajudar?"
    ],
    "despedida": [
        "Obrigado por utilizar o MediVision Bot. Cuide-se e tenha um bom dia!",
        "Até logo! Estou à disposição sempre que precisar de assistência médica ou análise visual de sintomas."
    ],
    "pergunta_sintomas": [
        "Poderia descrever quais sintomas está sentindo ou enviar uma foto da área afetada para eu analisar?",
        "Quais são os principais sintomas que você está experimentando? Você também pode enviar uma imagem para que eu possa analisar visualmente."
    ],
    "solicitacao_imagem": [
        "Para uma análise mais precisa, você poderia enviar uma foto da área afetada?",
        "Uma imagem da região com sintomas me ajudaria a fazer uma avaliação mais precisa. Poderia enviar uma foto?"
    ],
    "analise_imagem": [
        "Analisei a imagem que você enviou. {resultado_analise}",
        "Baseado na imagem que você compartilhou, {resultado_analise}"
    ],
    "emergencia": [
        "ATENÇÃO! Baseado na análise visual e nos sintomas descritos, você pode estar com uma condição que requer atendimento médico imediato. Por favor, procure o pronto-socorro mais próximo ou ligue para o SAMU (192).",
        "URGENTE! Os sinais detectados na imagem indicam uma condição que necessita de atendimento médico emergencial. Po
