from fastapi import FastAPI

app = FastAPI(title="Immo Prédictif API",
              description="API para fornecer dados do mercado imobiliário da Bélgica, Portugal e França",
              version="1.0")

# Dados simulados para teste inicial
dados_imobiliarios = {
    "Bélgica": {
        "Bruxelas": {"preco_m2": 4500, "tendencia": "+6% ao ano"},
        "Antuérpia": {"preco_m2": 3800, "tendencia": "+4.5% ao ano"}
    },
    "Portugal": {
        "Lisboa": {"preco_m2": 5000, "tendencia": "+8% ao ano"},
        "Porto": {"preco_m2": 4000, "tendencia": "+7% ao ano"}
    },
    "França": {
        "Paris": {"preco_m2": 11000, "tendencia": "+5% ao ano"},
        "Marselha": {"preco_m2": 3500, "tendencia": "+3.8% ao ano"}
    }
}

@app.get("/precos")
def obter_precos(pais: str, cidade: str):
    pais = pais.capitalize()
    cidade = cidade.capitalize()
    if pais in dados_imobiliarios and cidade in dados_imobiliarios[pais]:
        return {"pais": pais, "cidade": cidade, "dados": dados_imobiliarios[pais][cidade]}
    return {"erro": "Localidade não encontrada"}

@app.get("/tendencias")
def obter_tendencias(pais: str, cidade: str):
    pais = pais.capitalize()
    cidade = cidade.capitalize()
    if pais in dados_imobiliarios and cidade in dados_imobiliarios[pais]:
        return {"pais": pais, "cidade": cidade, "tendencia": dados_imobiliarios[pais][cidade]["tendencia"]}
    return {"erro": "Localidade não encontrada"}
