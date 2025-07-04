import json

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os

from typing import List

import numpy as np

from dotenv import load_dotenv

load_dotenv(dotenv_path="app/.env")
key = os.getenv("OPENAI_API_KEY")


def generate_interview_questions(profile: dict, job_description: str) -> List[str]:
    prompt_template = PromptTemplate(
        input_variables=["profile", "job_description"],
        template="""
You are an assistant that analyzes resumes and job descriptions to suggest relevant interview questions.

Your task:
Based on the job description and the structured resume profile provided, generate a Python **list of questions** to be asked in a job interview.

Include a question **only** if there's clear evidence from the profile and job description. Use these guidelines:

1. If the candidate has **gaps longer than 1 year** between work experiences, add:
   - "Por que você ficou esse período sem experiências?"

2. If the candidate has any experience where the **duration is less than 1 year**, add:
   - "Por que você ficou tão pouco tempo nessa experiência?"

3. If the job is **on-site/presencial** in a different city than the candidate's **residential address**, add:
   - "Como seria a questão de distância para você?"

Do not include questions if the condition is not clearly met.

Return only a **valid Python list of strings**, e.g.:
["Pergunta 1", "Pergunta 2", ...]

Job description:
{job_description}

Resume profile (structured JSON):
{profile}
""",
    )

    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(
        job_description=job_description, profile=json.dumps(profile, ensure_ascii=False)
    )

    return eval(response)  # Transforma em lista
