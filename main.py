import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def frontend():
    return FileResponse("index.html")

def buscar_reviews(item_id: str) -> list:
    try:
        url = f"https://api.mercadolibre.com/reviews/item/{item_id}"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code != 200:
            return []
        dados = resposta.json()
        return dados.get("reviews", [])
    except Exception:
        return []

@app.get("/search")
def search(
    query: str = Query(..., description="Termo de busca"),
    limit: int = Query(5, ge=1, le=50, description="Máximo de itens")
):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit={limit}"
    
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
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
    
    return {
        "query": query,
        "limit": limit,
        "items": itens
    }