import wikipediaapi
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel

# wiki_wiki = None
# llm = None

wiki_wiki = wikipediaapi.Wikipedia(user_agent= 'SWEats (njwei@g.ucla.edu)', language='en')
llm = OpenAI()

class Articles(BaseModel):
    article_names: list[str]

class Question(BaseModel):
    prompt1: str
    prompt2: str
    prompt3: str
    answer: str

class Questions(BaseModel):
    questions: list[Question]
    ok: bool = True
    error: str = ""



@asynccontextmanager
async def lifespan(app: FastAPI):
    global wiki_wiki
    global llm
    wiki_wiki = wikipediaapi.Wikipedia(user_agent= 'SWEats (njwei@g.ucla.edu)', language='en')
    llm = OpenAI()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/questions")
def read_questions(articles: Articles):
    questions = []
    ok = True
    error = ""
    
    for article_name in articles.article_names:
        page = wiki_wiki.page(article_name)
        if not page.exists():
            raise Exception(f"Article {article_name} does not exist.")
        prompt = "Create a NAQT style triva prompt using 3 clues in decreasing obscurity given the following abstract:\n" + page.summary
        prompt += "\n The first clue should be prefaced with '1.', the second with '2.', and the third with '3.'. The answer should be prefaced with 'ANSWER:'."
        
        # NOTE: The following line actually makes the question generation significantly worse if used instead of the above line.
        # This is likely because the weird symbol makes the prompt out of distribution.

        # prompt += "\n The first clue should be prefaced with '*|*', the second with '*|*', and the third with *|*.'. The answer should be prefaced with '*|*'."

        completion = llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        # print(completion.choices[0].message)
        print(completion.choices[0].message.content)
        content = completion.choices[0].message.content

        prompt1 = content.split("1.")[1].split("2.")[0].strip()
        prompt2 = content.split("2.")[1].split("3.")[0].strip()
        prompt3 = content.split("3.")[1].split("ANSWER:")[0].strip()
        answer = content.split("ANSWER:")[1].strip()

        question = Question(prompt1=prompt1, prompt2=prompt2, prompt3=prompt3, answer=answer)
        questions.append(question)
    
    return Questions(questions=questions, ok=ok, error=error)

@app.get("/health")
def health_check():
    return {"status": "healthy"}