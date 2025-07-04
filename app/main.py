from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from resume_profile import create_profile
from description import create_description
from education import evaluate_education_requirements, compute_education
from experience import evaluate_experience_requirements, compute_experience
from skills import evaluate_skill_requirements, compute_skills
from questions import generate_interview_questions



load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/analisar_curriculo")
async def analisar_curriculo(
    arquivo_pdf: UploadFile = File(...), contexto_vaga: str = Form(...)
):
    pontos_fortes = []
    pontos_fracos = []
    
    
    profile_json = create_profile(arquivo_pdf)
    description_dict = create_description(contexto_vaga)

    perguntas = generate_interview_questions(profile_json, contexto_vaga)

    education_requirements = description_dict["education"]
    experience_requirements = description_dict["experience"]
    hard_skills_requirements = description_dict["hard_skills"]
    soft_skills_requirements = description_dict["soft_skills"]
    language_requirements = description_dict["languages"]

    if len(education_requirements) != 0:
        education_info = evaluate_education_requirements(education_requirements, profile_json)
        education_score, fortes, fracos = compute_education(education_info)
        pontos_fortes.extend(fortes)
        pontos_fracos.extend(fracos)
    
    else: education_score = 0

    if len(experience_requirements) != 0:
        experience_info = evaluate_experience_requirements(experience_requirements, profile_json)
        experience_score, fortes, fracos = compute_experience(experience_info)
        pontos_fortes.extend(fortes)
        pontos_fracos.extend(fracos)

    else: experience_score = 0

    skills_info = evaluate_skill_requirements(hard_skills_requirements,
                                        soft_skills_requirements,
                                        language_requirements,
                                        profile_json)
    
    hard_skill_score, soft_skill_score, language_score, fortes, fracos, perguntas_lista = compute_skills(skills_info)
    pontos_fortes.extend(fortes)
    pontos_fracos.extend(fracos)
    perguntas.extend(perguntas_lista)

    geral_score = 0.4*experience_score + 0.25*hard_skill_score + 0.2*education_score + 0.1*soft_skill_score + 0.05*language_score

    return JSONResponse(
    {
        "Escores": {
            "Geral": round(geral_score, 2),
            "Educação": round(education_score, 2) if len(education_requirements) != 0 else 0,
            "Experiência": round(experience_score, 2) if len(experience_requirements) != 0 else 0,
            "Hard Skills": round(hard_skill_score, 2),
            "Soft Skills": round(soft_skill_score, 2),
            "Idiomas": round(language_score, 2),
        },
        "Pontos fortes": pontos_fortes,
        "Pontos fracos": pontos_fracos,
        "Perguntas": perguntas,
    }
)




