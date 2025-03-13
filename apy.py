from fastapi import FastAPI

app = FastAPI(title="Immo Prédictif API",
              description="API para fornecer dados do mercado imobiliário da Bélgica, Portugal e França",
              version="1.0")

# 📌 Dados simulados para teste inicial
dados_imobiliarios = {
    "Belgica": {
        "Bruxelas": {"preco_m2": 4500, "tendencia": "+6% ao ano"},
        "Antuérpia": {"preco_m2": 3800, "tendencia": "+4.5% ao ano"}
    },
    "Portugal": {
        "Lisboa": {"preco_m2": 5000, "tendencia": "+8% ao ano"},
        "Porto": {"preco_m2": 4000, "tendencia": "+7% ao ano"}
    },
    "Franca": {
        "Paris": {"preco_m2": 11000, "tendencia": "+5% ao ano"},
        "Marselha": {"preco_m2": 3500, "tendencia": "+3.8% ao ano"}
    }
}

@app.get("/precos")
def obter_precos(pais: str, cidade: str):
    pais, cidade = pais.capitalize(), cidade.capitalize()
    if pais in dados_imobiliarios and cidade in dados_imobiliarios[pais]:
        return {"pais": pais, "cidade": cidade, "dados": dados_imobiliarios[pais][cidade]}
    return {"erro": "Localidade não encontrada"}

@app.get("/tendencias")
def obter_tendencias(pais: str, cidade: str):
    pais, cidade = pais.capitalize(), cidade.capitalize()
    if pais in dados_imobiliarios and cidade in dados_imobiliarios[pais]:
        return {"pais": pais, "cidade": cidade, "tendencia": dados_imobiliarios[pais][cidade]["tendencia"]}
    return {"erro": "Localidade não encontrada"}

@app.get("/comparar")
def comparar_precos(pais1: str, cidade1: str, pais2: str, cidade2: str):
    pais1, cidade1 = pais1.capitalize(), cidade1.capitalize()
    pais2, cidade2 = pais2.capitalize(), cidade2.capitalize()
    
    if pais1 in dados_imobiliarios and cidade1 in dados_imobiliarios[pais1] and        pais2 in dados_imobiliarios and cidade2 in dados_imobiliarios[pais2]:
        return {
            "comparacao": {
                cidade1: dados_imobiliarios[pais1][cidade1]["preco_m2"],
                cidade2: dados_imobiliarios[pais2][cidade2]["preco_m2"]
            }
        }
    return {"erro": "Uma ou ambas as cidades não foram encontradas"}

# Comando para rodar o servidor localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
