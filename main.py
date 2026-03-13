from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI(
    title="SmartGov AI Assistant",
    description="AI chatbot to help citizens understand Indian government schemes",
    version="1.0"
)


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


gov_schemes = {
    "pm kisan": {
        "name": "PM-Kisan",
        "info": "Direct income support of ₹6000 per year for small and marginal farmers."
    },
    "ayushman bharat": {
        "name": "Ayushman Bharat",
        "info": "Health insurance scheme covering up to ₹5 lakh per family per year."
    },
    "pm awas": {
        "name": "Pradhan Mantri Awas Yojana",
        "info": "Affordable housing scheme for urban and rural poor."
    },
    "ujjwala": {
        "name": "Pradhan Mantri Ujjwala Yojana",
        "info": "Provides free LPG connections to women from BPL households."
    }
}


class Question(BaseModel):
    question: str
    response_type: str = "concise"
    language: str = "english"


def format_local_response(info, response_type):
    if response_type == "bullet":
        return f"• Scheme: {info['name']}\n• Benefit: {info['info']}\n• Apply through: Government portal or nearest CSC"
    elif response_type == "paragraph":
        return f"{info['name']} is a government scheme in India. {info['info']} Citizens can apply through official government portals or through Common Service Centers (CSC)."
    else:
        return f"{info['name']}: {info['info']}"


@app.post("/ask")
async def ask_question(q: Question): # Added 'async' for better FastAPI performance
    user_question = q.question.lower()
    response_type = q.response_type
    language = q.language

    
    for scheme in gov_schemes:
        if scheme in user_question:
            answer = format_local_response(gov_schemes[scheme], response_type)
            return {"answer": answer}

   
    try:
        prompt = f"""
        You are an AI assistant that helps citizens understand Indian government schemes.
        User question: {q.question}
        Respond in {response_type} format.
        Language: {language}
        """
       
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert on Indian government schemes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.5
        )
        answer = response.choices[0].message.content

    except Exception as e:
        print(f"Error details: {e}")
        answer = "Sorry, I am having trouble connecting to the AI service. Please try again later."

    return {"answer": answer}

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartGov AI Assistant. Use POST /ask to interact."}




