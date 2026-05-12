import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Serve pra corrigir um bug de ficar buscando de forma infinita o produto.
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simula um navegador real pra evitar o bloqueio 403 do Mercado Livre
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

@app.get("/")
def frontend():
    return FileResponse("index.html")

def buscar_reviews(item_id: str) -> list:
    try:
        url = f"https://api.mercadolibre.com/reviews/item/{item_id}"
        resposta = requests.get(url, timeout=5, headers=HEADERS)
        if resposta.status_code != 200:
            return []  # se não tiver reviews retorna vazio sem quebrar a aplicação
        dados = resposta.json()
        return dados.get("reviews", [])  # .get() com default [] = nunca vai quebrar
    except Exception:
        return []  # qualquer erro de rede → lista vazia

@app.get("/search")
def search(
    query: str = Query(..., description="Termo de busca"),
    limit: int = Query(5, ge=1, le=50, description="Máximo de itens")
):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit={limit}"
    
    try:
        resposta = requests.get(url, timeout=10, headers=HEADERS)
        resposta.raise_for_status()  # levanta erro se status != 200
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao buscar no Mercado Livre: {str(e)}")
    
    resultados = resposta.json().get("results", [])
    
    itens = []
    for item in resultados:
        reviews = buscar_reviews(item["id"])
        itens.append({
            "titulo": item.get("title"),
            "preco": item.get("price"),
            "url_imagem": item.get("thumbnail"),
            "reviews": reviews
        })
    
    # Retorna o contrato de saída
    return {
        "query": query,
        "limit": limit,
        "items": itens
    }