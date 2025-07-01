from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/analisar_curriculo")
async def analisar_curriculo(
    arquivo_pdf: UploadFile = File(...), contexto_vaga: str = Form(...)
):
    # Aqui vai o processamento futuro: leitura PDF, Langchain, etc.
    # Utilizar OPENAI_API_KEY para acessar a chave de API da Open AI

    return JSONResponse(
        {
            "mensagem": "Recebido com sucesso.",
            "nome_arquivo": arquivo_pdf.filename,
            "contexto_vaga": contexto_vaga,
        }
    )
