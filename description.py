import fitz

import json

from fastapi import UploadFile
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os

from typing import List, Optional
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv(dotenv_path="app/.env")
key = os.getenv("OPENAI_API_KEY")


class Education(BaseModel):
    text: str
    requirement: bool


class Experience(BaseModel):
    text: str
    requirement: bool


class HardSkill(BaseModel):
    text: str
    requirement: bool


class SoftSkill(BaseModel):
    text: str
    requirement: bool


class Language(BaseModel):
    text: str
    requirement: bool


class Certification(BaseModel):
    text: str
    requirement: bool


class JobDescription(BaseModel):
    education: Optional[List[Education]] = []
    experience: Optional[List[Experience]] = []
    hard_skills: Optional[List[HardSkill]] = []
    soft_skills: Optional[List[SoftSkill]] = []
    languages: Optional[List[Language]] = []
    certifications: Optional[List[Certification]] = []


def create_description(text: str) -> dict:

    # Criando prompt
    prompt_template = PromptTemplate(
        input_variables=["job_text"],
        template="""
You are an expert at analyzing job descriptions.

Your task is to extract structured data from the job posting text below. For each category, list the requirements and differentiators (nice-to-haves) mentioned in the text.

Important instructions:
- For each item, extract a separate and distinct entry, even when multiple items are mentioned in the same sentence.
- Ensure that each individual skill, qualification, experience or requirement results in a unique instance in the corresponding list.
- Set `"requirement": True` if it is a mandatory requirement.
- Set `"requirement": False` if it is explicitly a nice-to-have item

Only return a valid Python **dictionary object** (not a JSON string, no comments, no explanstringations).

Expected Python dictionary schema:

{{
  "education": [{{"text": str, "requirement": bool}}],
  "experience": [{{"text": str, "requirement": bool}}],
  "hard_skills": [{{"text": str, "requirement": bool}}],
  "soft_skills": [{{"text": str, "requirement": bool}}],
  "languages": [{{"text": str, "requirement": bool}}],
  "certifications": [{{"text": str, "requirement": bool}}]
}}

Job description:
{job_text}
""",
    )

    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(job_text=text)

    # Se a resposta vier como string, decodifica em dicionário
    if isinstance(response, str):
        response_dict = (
            eval(response) if response.strip().startswith("{") else json.loads(response)
        )
    else:
        response_dict = response

    # Forçando a tipagem dos atributos
    return JobDescription(**response_dict).model_dump()
