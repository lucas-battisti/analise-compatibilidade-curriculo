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

class PersonalInfo(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]


class Education(BaseModel):
    degree: str
    level: str
    institution: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    duration_months: Optional[int]
    completed: Optional[bool]


class Experience(BaseModel):
    title: str
    company: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    duration_months: Optional[int]
    description: Optional[str]
    results: Optional[str]
    skills_used: List[str]


class HardSkill(BaseModel):
    name: str
    experience_level: Optional[str]


class SoftSkill(BaseModel):
    name: str


class Language(BaseModel):
    language: str
    proficiency_level: Optional[str]


class ResumeProfile(BaseModel):
    personal_info: PersonalInfo
    education: List[Education]
    experience: List[Experience]
    hard_skills: List[HardSkill]
    soft_skills: List[SoftSkill]
    languages: List[Language]


def create_profile(pdf_file: UploadFile) -> dict:
    # pdf -> string
    content = pdf_file.file.read()
    with fitz.open(stream=content, filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)

    # Criando prompt
    prompt_template = PromptTemplate(
    input_variables=["resume_text"],
    template="""
You are an expert in resume parsing.

Based on the resume text below, extract a structured profile in JSON format with the following schema.

Important instructions:
- Only return a **valid JSON object** (no comments, no explanations).
- All **date fields must be in ISO 8601 format (YYYY-MM-DD)**.
- The **data types** of each field must match exactly what is specified below.
- ⚠️ For each education item, the field **"level" must be a non-null string**. 
  If not explicitly stated in the resume, set it as **"Unknown"**, but never use null or omit it.

Expected schema and data types:

{{
  "personal_info": {{
    "name": string,
    "email": string,
    "phone": string or null,
    "address": string or null
  }},
  "education": [
    {{
      "degree": string,
      "level": string,  // ⚠️ Required string, never null
      "institution": string,
      "start_date": string (format: YYYY-MM-DD) or null,
      "end_date": string (format: YYYY-MM-DD) or null,
      "duration_months": integer or null,
      "completed": boolean or null
    }}
  ],
  "experience": [
    {{
      "title": string,
      "company": string,
      "start_date": string (format: YYYY-MM-DD) or null,
      "end_date": string (format: YYYY-MM-DD) or null,
      "duration_months": integer or null,
      "description": string or null,
      "results": string or null,
      "skills_used": list of strings
    }}
  ],
  "hard_skills": [
    {{
      "name": string,
      "experience_level": string
    }}
  ],
  "soft_skills": [
    {{
      "name": string
    }}
  ],
  "languages": [
    {{
      "language": string,
      "proficiency_level": string
    }}
  ]
}}

Resume Text:
{resume_text}
"""
)
    # Criando o LLM
    llm = ChatOpenAI(api_key=key, temperature=0, model_name="gpt-4")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Executando o LLM
    response = chain.run(resume_text=text)

    # Forçando a tipagem (JSON dict e tipagem dos atributos)
    json_response = json.loads(response)
    return json.dumps(ResumeProfile(**json_response).model_dump(),
                      ensure_ascii=False) # Isso manterá os acentos e outros caracteres UTF-8

######## TESTE ###########

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/create_profile_teste")
async def create_profile_teste(
    arquivo_pdf: UploadFile = File(...)
):
    
    return create_profile(arquivo_pdf)
