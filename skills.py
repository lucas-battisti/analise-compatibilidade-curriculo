import numpy as np

import json

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os

from typing import List, Optional
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv(dotenv_path="app/.env")
key = os.getenv("OPENAI_API_KEY")

class SkillEvaluation(BaseModel):
    name: str
    type: str 
    requirement: bool
    mentioned_in_resume: int
    level_comparison: Optional[int]
    mentioned_in_experience: bool


def evaluate_skill_requirements(
    hard_skills_requirements: List[dict],
    soft_skills_requirements: List[dict],
    language_requirements: List[dict],
    profile: dict
) -> List[dict]:

    prompt_template = PromptTemplate(
        input_variables=["profile", "hard_skills_requirements", "soft_skills_requirements", "language_requirements"],
        template="""
You are an assistant comparing job skill requirements with a candidate's resume.

Inputs:
- Each `..._requirements`: a list of dictionaries, each representing a required or desired skill.
  Each item has:
    - "text": a description of the requirement (e.g. "Advanced knowledge of Python")
    - "requirement": true if mandatory, false if nice-to-have

- `hard_skills_requirements`, `soft_skills_requirements`, `language_requirements`: the job description's requirements.
- `resume`: full experience descriptions from the resume.

For each requirement:
1. Extract a short title as "name" (e.g., "Python", "Leadership", "English").
2. Match it with the corresponding block ("hard_skill", "soft_skill", "language").
3. Return:
    - "name": extracted title
    - "type": "hard_skill", "soft_skill" or "language"
    - "requirement": same as input
    - "mentioned_in_resume":
        - 7 if the skill appears in the candidate's resume block
        - 3 if not
    - "level_comparison":
        - 1 if candidate's level is clearly above the job requirement
        - 0 if levels match or if the level is not specified in the requirements
        - -1 if below
        - null if the level is missing in the RESUME
    - "mentioned_in_experience":
        - true if the skill appears in any experience description
        - false otherwise

⚠️ Return only a **valid Python list of dictionaries**. Do not explain anything.

Hard Skills requirements:
{hard_skills_requirements}

Soft Skills requirements:
{soft_skills_requirements}

Language requirements:
{language_requirements}

Resume JSON:
{profile}
"""
    )

    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(
      profile=json.dumps(profile, ensure_ascii=False),
      hard_skills_requirements=json.dumps(hard_skills_requirements, ensure_ascii=False),
      soft_skills_requirements=json.dumps(soft_skills_requirements, ensure_ascii=False),
      language_requirements=json.dumps(language_requirements, ensure_ascii=False),
  )

    return json.loads(response)

def compute_skills(info_dict: List[dict]):
    score_array = np.array([])      # Guarda os escores finais por item
    req_weights = np.array([])      # Guarda os pesos das habilidades (0.8 se for requisito, 0.2 se desejável)
    type_array = np.array([])       # Guarda os tipos das habilidades (hard_skill, soft_skill, language)
    
    pontos_fortes_list = []         # Lista de pontos fortes do candidato
    pontos_fracos_list = []         # Lista de pontos fracos do candidato
    perguntas_list = []             # Lista de perguntas a serem feitas ao candidato

    for i in info_dict:

        b = 0  # b = bônus que pode ser adicionado ao escore base `a`

        # Define peso conforme seja um requisito obrigatório (0.8) ou desejável (0.2)
        if i["requirement"] == True:
            req_weights = np.append(req_weights, 0.8)
        else:
            req_weights = np.append(req_weights, 0.2)
        
        # Se a habilidade não foi mencionada no currículo (valor 3), atribui escore base mínimo
        if i["mentioned_in_resume"] == 3:
            pontos_fracos_list.append("Candidato não possui conhecimento de {}".format(i["name"]))
            perguntas_list.append("Você tem alguma experiência com {}?".format(i["name"]))
            a = 3  # escore base mais baixo

        else:
            a = 7  # escore base padrão para quando a habilidade é mencionada

            # Se o nível do candidato for inferior ao exigido
            if i["level_comparison"] == -1:
                pontos_fracos_list.append("O candidato possui conhecimento de {} em nível inferior ao exigido".format(i["name"]))
                b += -1

            # Se o nível for superior ao exigido
            elif i["level_comparison"] == 1:
                pontos_fortes_list.append("O candidato possui conhecimento de {} em nível superior ao exigido".format(i["name"]))
                b += 1

            # Nível igual ou não especificado
            else:
                pontos_fortes_list.append("O candidato possui conhecimento de {}".format(i["name"]))

                # Se o nível não for especificado e não for uma soft skill, sugerir pergunta
                if not i["level_comparison"] and i["type"] != "soft_skill":
                    perguntas_list.append("Qual seu nível de experiência com {}?".format(i["name"]))

            # Se a habilidade foi mencionada em alguma experiência prática
            if i["mentioned_in_experience"] == True:
                pontos_fortes_list.append("Utilizou {} em suas experiencias".format(i["name"]))
                b += 2  # bônus adicional

        # Atualiza arrays para cálculo dos escores por tipo de habilidade
        type_array = np.append(type_array, i["type"])
        score_array = np.append(score_array, (a + b))  # escore final é soma do base com bônus

        # Cálculo dos escores ponderados por tipo
        hard_skill_score = np.average(score_array[type_array == "hard_skill"],
                                      weights=req_weights[type_array == "hard_skill"]) if np.any(type_array == "hard_skill") else 0.0
        soft_skill_score = np.average(score_array[type_array == "soft_skill"],
                                      weights=req_weights[type_array == "soft_skill"]) if np.any(type_array == "soft_skill") else 0.0
        language_score = np.average(score_array[type_array == "language"],
                                    weights=req_weights[type_array == "language"]) if np.any(type_array == "language") else 0.0
            
    return hard_skill_score, soft_skill_score, language_score, pontos_fortes_list, pontos_fracos_list, perguntas_list
