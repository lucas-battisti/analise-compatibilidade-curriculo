import json

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os

from typing import List, Optional
from pydantic import BaseModel

import numpy as np

from dotenv import load_dotenv
load_dotenv(dotenv_path="app/.env")
key = os.getenv("OPENAI_API_KEY")

class EducationEvaluation(BaseModel):
    degree_level: str
    requirement: bool
    correspondence: int
    completed: Optional[bool]

def evaluate_education_requirements(
    requirement_texts: List[dict],
    profile: dict
) -> List[dict]:

    prompt_template = PromptTemplate(
    input_variables=["requirements", "education_history"],
    template="""
You are an assistant that analyzes how well a candidate's educational background matches a list of job education requirements.

Input:
- A list of requirements, where each item includes:
  - "text": the required or desired education
  - "requirement": True (mandatory) or False (nice-to-have)
- The candidate's education history (structured data).

Task:
For each item in the requirements list:
1. Extract the **required degree level** (e.g., "Graduação", "Mestrado", "Doutorado", "Ensino Técnico").
2. Evaluate whether the candidate has:
   - Strong correspondence → 3
   - Partial correspondence → 2
   - No correspondence → 1
3. Check whether the corresponding education in the candidate's history is completed (`completed`: true/false/null).

Return a **valid Python list of dictionaries**. Each dictionary must include:
- `"degree_level"`: the level of education required (not the field)
- `"requirement"`: same as input
- `"correspondence"`: 1, 2 or 3
- `"completed"`: true, false, or null

⚠️ Only return the list. Do not explain anything. Keep the output order the same as the input.

Requirements:
{requirements}

Candidate education history:
{education_history}
"""
)

    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(
        requirements=json.dumps(requirement_texts, ensure_ascii=False),
        education_history=json.dumps(profile, ensure_ascii=False),
    )

    return json.loads(response)



def compute_education(info_dict: List[dict]):
    score_array = np.array([])      # Guarda os escores finais por item
    req_weights = np.array([])      # Guarda os pesos conforme seja requisito (0.8) ou diferencial (0.2)
    pontos_fortes_list = []         # Lista de pontos fortes da formação acadêmica
    pontos_fracos_list = []         # Lista de pontos fracos da formação acadêmica

    for i in info_dict:

        b = 0  # b = bônus ou penalidade aplicada ao escore base `a`

        # Define peso do item (requisito obrigatório ou desejável)
        if i["requirement"] == True:
            req_weights = np.append(req_weights, 0.8)
        else:
            req_weights = np.append(req_weights, 0.2)
        
        # Se não possui a formação requerida
        if i["correspondence"] == 1:
            pontos_fracos_list.append("Candidato não tem a formação de {} requerida".format(i["degree_level"]))
            a = 3  # escore base mínimo

        # Se não completou a formação
        elif i["completed"] == False:
            pontos_fracos_list.append("Candidato não completou a formação de {} requerida".format(i["degree_level"]))
            b += -2  # penalidade
          
        # Formação parcialmente compatível
        if i["correspondence"] == 2:
            a = 6  # escore base intermediário

        # Formação muito compatível
        if i["correspondence"] == 3:
            a = 9  # escore base máximo
            pontos_fortes_list.append("O candidato possui uma formação que se encaixa bem nas exigências")

        # Soma escore base e bônus/penalidade, adiciona ao array
        score_array = np.append(score_array, (a + b))

    # Cálculo do escore final ponderado pelos pesos dos requisitos
    score = np.average(score_array, weights=req_weights)
    
    return score, pontos_fortes_list, pontos_fracos_list


        


