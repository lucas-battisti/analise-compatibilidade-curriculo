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

1. Dentro da pasta `app`, crie um arquivo `.env`.  
2. Adicione sua chave da OpenAI:
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
- **OpenAI GPT-4** – LLM utilizada
- **Pydantic** – Validação e estruturação de dados  
- **PyMuPDF (fitz)** – Extração de texto de PDFs 

---

## Estrutura e Fluxo do Sistema

O sistema organiza as informações em cinco categorias principais: **Experiência, Formação, Hard Skills, Soft Skills e Idiomas**.

A arquitetura combina:

- LLM para extração estruturada
- LLM para avaliação de compatibilidade e 
- Regras determinísticas para cálculo de score

O fluxo é dividido em três camadas: Extração → Correspondência e Perguntas  → Pontuação.

### 1. Extração de Dados (`resume_profile.py` e `description.py`)

**Currículo:** `resume_profile.py`

- Extração de texto do PDF via PyMuPDF
- Retorno em JSON estruturado contendo:
  * Experiências
  * Formação
  * Hard skills
  * Soft skills
  * Idiomas
 
**Descrição da vaga:** `description.py`

- Retorno em JSON estruturado contendo:
  * Experiências
  * Formação
  * Hard skills
  * Soft skills
  * Idiomas
 
Para mais detalhes sobre a estrutura, acesse: [resume_profile.py](resume_profile.py) e [description.py](description.py)

### 2. Correspondência e perguntas para a entrevista

Analisa a correspondência entre o candidato e a descrição da vaga, utilizando LLM para avaliar isso e gerando um score baseado na classificação (Alta, Razoável ou Nenhuma) para cada uma das cinco categorias. O módulo de Educação (`education.py`) verifica o nível de escolaridade e se a formação foi concluída; o módulo de Experiência (`experience.py`) avalia a compatibilidade entre experiências anteriores e os requisitos da vaga e se o candidato tem o tempo mínimo exigido; e o módulo de Skills e Idiomas (`skills.py`) compara o nível de proficiência declarado com o exigido, além de analisar evidências práticas relacionadas às competências solicitadas.

Além de atribuir uma nota, tamém são trazido os pontos fortes e fracos identificados na análise, fornecendo uma interpretação qualitativa do score. Ou seja, destaca onde o candidato está bem alinhado, onde há lacunas e quais aspectos merecem aprofundamento em entrevista. O modelo também gera perguntas direcionadas para entrevista (`questions.py`), auxiliando recrutadores a aprofundar pontos críticos ou validar competências específicas do candidato.

Para mais detalhes, acesse: [education.py](education.py), [experience.py](experience.py), [skills.py](skills.py), [questions.py](questions.py)

O score geral é calculado como uma média ponderada das categorias:

| Categoria      | Peso  |
|----------------|-------|
| Experiência    | 40%   |
| Hard Skills    | 25%   |
| Formação       | 20%   |
| Soft Skills    | 10%   |
| Idiomas        | 5%    |

Cada item recebe uma nota baseada na correspondência (Alta, Razoável ou Nenhuma).

## Saídas do Sistema

O endpoint `/analisar_curriculo` retorna:

- **Escores detalhados** – Nota de 0 a 10 para cada categoria e nota geral  
- **Pontos Fortes** – Ex: "Experiência muito alinhada com a vaga"  
- **Pontos Fracos** – Ex: "Não possui o tempo mínimo de experiência exigido"  
- **Perguntas de Entrevista** – Geradas automaticamente para gaps, experiências curtas ou informações faltantes 
