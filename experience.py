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


class ExperienceEvaluation(BaseModel):
    name: str
    requirement: bool
    correspondence: int
    duration_required: Optional[bool]
    relevant_results: Optional[bool]


def evaluate_experience_requirements(
    requirement_texts: List[dict], profile: dict
) -> List[dict]:

    prompt_template = PromptTemplate(
        input_variables=["requirements", "profile"],
        template="""
You are an assistant that analyzes how well a candidate's work experience matches a list of job experience requirements.

Inputs:
- A list of job experience requirements, where each item contains:
  - "text": the full description of the required or desired experience
  - "requirement": true if mandatory, false if just a nice-to-have

- The candidate's experience history (list of dicts with title, company, description, results, duration, etc.)

Task:
For each requirement:
1. Analyze the candidate's experience history and determine:
   - "name": a short, clear title summarizing the required experience (e.g. "Project management", "Data analysis with Python")
   - "requirement": copy 'true' or 'false' from input

2. Classify the **correspondence** between the requirement and the resume using the following logic:
   - 3 (strong match): the candidate has experience that directly aligns with the main skills, tasks, and context described in the requirement.
   - 2 (partial match): the candidate has experience that is somewhat related (e.g., similar skills or tasks, but not fully aligned in context, level, or domain).
   - 1 (no match): there is no clear evidence of relevant experience in the candidate's history.

3. If correspondence is 2 or 3, provide:
   - "relevant_results": true if any outcomes, impact, or results are mentioned in the relevant experiences
   - "duration_required": 
       - true if the candidate meets or exceeds the minimum duration mentioned in the requirement (if any),
       - false if they fall short,
       - null if the requirement does not specify any time/duration.

Output:
Return a **Python list of dictionaries** (one per requirement) with the following keys:
- "name": string
- "requirement": true or false
- "correspondence": 1, 2, or 3
- "duration_required": true / false / null
- "relevant_results": true / false / null

⚠️ Keep the output order the same as the input.
⚠️ Return only a valid Python list. No explanation.

Requirements:
{requirements}

Candidate complete profile:
{profile}
""",
    )

    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(
        requirements=json.dumps(requirement_texts, ensure_ascii=False),
        profile=json.dumps(profile, ensure_ascii=False),
    )

    return json.loads(response)


def compute_experience(info_dict: List[dict]):
    score_array = np.array([])  # Guarda os escores finais por item
    req_weights = np.array([])  # Guarda os pesos conforme seja requisito ou diferencial
    pontos_fortes_list = []  # Lista de pontos fortes nas experiências
    pontos_fracos_list = []  # Lista de pontos fracos nas experiências

    for i in info_dict:

        b = 0  # b = bônus que ajusta o valor base `a` conforme critérios extras

        # Define peso da experiência: 0.8 se for requisito, 0.2 se diferencial
        if i["requirement"] == True:
            req_weights = np.append(req_weights, 0.8)
        else:
            req_weights = np.append(req_weights, 0.2)

        # Se o candidato não tem a experiência
        if i["correspondence"] == 1:
            pontos_fracos_list.append(
                "Candidato não possui experiência de {}".format(i["name"])
            )
            a = 3  # escore base mínimo

        else:
            # Se não atinge o tempo mínimo exigido
            if i["duration_required"] == False:
                pontos_fracos_list.append(
                    "O candidato não possui o tempo mínimo de experiência exigido"
                )
                b += -2  # penalidade

            # Se há resultados relevantes nas experiências
            if i["relevant_results"] == True:
                pontos_fortes_list.append(
                    "As experiências do candidato evidenciam contribuições significativas e relevantes"
                )
                b += 1  # bônus positivo

        # Nível moderado de correspondência com a vaga
        if i["correspondence"] == 2:
            pontos_fortes_list.append(
                "O candidato possui experiência com {}".format(i["name"])
            )
            a = 6  # escore base intermediário

        # Nível alto de correspondência com a vaga
        if i["correspondence"] == 3:
            a = 9  # escore base máximo
            pontos_fortes_list.append(
                "O candidato possui uma experiência muito alinhada com a vaga"
            )

        # Soma escore base e bônus, armazena
        score_array = np.append(score_array, (a + b))

    # Cálculo do escore final ponderado pelos pesos dos requisitos
    score = np.average(score_array, weights=req_weights)

    return score, pontos_fortes_list, pontos_fracos_list
