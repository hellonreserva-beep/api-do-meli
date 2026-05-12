import requests
from fastapi import FastAPI, Query, HTTPException

# FastAPI pra criar a API.
app = FastAPI()

# Função separada para buscar reviews de um item.
# Se der erro aqui, vai dar pra corrigir legal sem quebrar o resto.
def buscar_reviews(item_id: str) -> list:
    try:
        url = f"https://api.mercadolibre.com/reviews/item/{item_id}"
        resposta = requests.get(url, timeout=5)  # timeout evita travar
        if resposta.status_code != 200:
            return []   # se não tiver reviews ele vai retornar vazio sem quebrar a aplicação
        dados = resposta.json()
        return dados.get("reviews", [])  # .get() com default [] = nunca vai quebrar
    except Exception:
        return []   # qualquer erro de rede → lista vazia

# O endpoint principal. Se alguém acessar /search?query=iphone&limit=5
# o FastAPI vai chamar essa função automaticamente.
@app.get("/search")
def search(
    query: str = Query(..., description="Termo de busca"),
    limit: int = Query(5, ge=1, le=50, description="Máximo de itens")
):
    # Busca na API do Mercado Livre
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit={limit}"
    
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()  # levanta erro se status != 200
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao buscar no Mercado Livre: {str(e)}")
    
    resultados = resposta.json().get("results", [])
    
    # Monta uma lista de itens com reviews
    itens = []
    for item in resultados:
        reviews = buscar_reviews(item["id"])
        itens.append({
            "titulo": item.get("title"),
            "preco": item.get("price"),
            "url_imagem": item.get("thumbnail"),
            "reviews": reviews
        })
    
    # Retorna o contrato de saída.
    return {
        "query": query,
        "limit": limit,
        "items": itens
    }