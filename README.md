# Modelo de Análise de Compatibilidade de Currículos

Este projeto é um sistema inteligente que avalia a compatibilidade entre currículos e vagas de emprego. Utilizando técnicas de Processamento de Linguagem Natural (NLP) e inteligência artificial, o modelo identifica pontos fortes e lacunas dos candidatos, gera scores detalhados e sugere perguntas para entrevistas.

## Objetivos

- Avaliar a compatibilidade entre currículo e vaga  
- Identificar automaticamente pontos fortes e fracos do candidato em relação aos requisitos  
- Gerar um score detalhado por categoria  
- Sugerir perguntas de entrevista baseadas em gaps ou informações a esclarecer no perfil  

---

## Tutorial de Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e executar o projeto localmente.

## 1. Pré-requisitos
- **Python 3.10 ou superior**  
- Git (para clonar o repositório)  

## 2. Clonar o Repositório
```bash
git clone https://github.com/lucas-battisti/analise-compatibilidade-curriculo.git
cd analise-compatibilidade-curriculo
```

## 3. Criar e Ativar Ambiente Virtual (Recomendado)
```bash
python -m venv venv
# No Windows:
venv\\Scripts\\activate
# No Linux/macOS:
source venv/bin/activate
```

## 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

## 5. Configurar Variáveis de Ambiente
O sistema utiliza `python-dotenv` para gerenciar chaves de API.  

1. Crie uma pasta chamada `app` (caso ainda não exista).  
2. Dentro dela, crie um arquivo `.env`.  
3. Adicione sua chave da OpenAI:
```env
OPENAI_API_KEY=seu_token_aqui
```


## 6. Executar a Aplicação
Inicie o servidor FastAPI com:

```bash
uvicorn main:app --reload
```


## Tecnologias Utilizadas

- **Python** – Linguagem principal  
- **FastAPI** – Criação da API de análises  
- **LangChain** – Orquestração de modelos de linguagem (LLMs)  
- **OpenAI GPT-4** – Extração de dados e análise de compatibilidade  
- **Pydantic** – Validação e estruturação de dados  
- **Numpy** – Cálculos matemáticos e ponderação de scores  
- **PyMuPDF (fitz)** – Extração de texto de PDFs 

---

## Estrutura e Fluxo do Sistema

O sistema organiza as informações em cinco categorias principais: **Experiência, Formação, Hard Skills, Soft Skills e Idiomas**.

### 1. Extração de Dados

- **Perfil do Candidato (`resume_profile.py`)**: Converte currículos em PDF para texto e estrutura os dados em JSON, incluindo histórico profissional, acadêmico e competências  
- **Descrição da Vaga (`description.py`)**: Extrai os requisitos obrigatórios e diferenciais da vaga  

### 2. Avaliação

- **Educação (`education.py`)**: Verifica o nível de escolaridade e se a formação foi concluída  
- **Experiência (`experience.py`)**: Analisa a correspondência entre experiências anteriores e os requisitos da vaga  
- **Skills e Idiomas (`skills.py`)**: Compara o nível de proficiência com o exigido e verifica experiências práticas relacionadas  

### 3. Sistema de Pontuação

O score geral é calculado como uma média ponderada das categorias:

| Categoria      | Peso  |
|----------------|-------|
| Experiência    | 40%   |
| Hard Skills    | 25%   |
| Formação       | 20%   |
| Soft Skills    | 10%   |
| Idiomas        | 5%    |

Cada item recebe uma nota baseada na correspondência (Alta, Razoável ou Nenhuma), com bônus ou penalidades conforme requisitos atendidos ou não.

## 📋 Saídas do Sistema

O endpoint `/analisar_curriculo` retorna:

- **Escores detalhados** – Nota de 0 a 10 para cada categoria e nota geral  
- **Pontos Fortes** – Ex: "Experiência muito alinhada com a vaga"  
- **Pontos Fracos** – Ex: "Não possui o tempo mínimo de experiência exigido"  
- **Perguntas de Entrevista** – Geradas automaticamente para gaps, experiências curtas ou informações faltantes 
