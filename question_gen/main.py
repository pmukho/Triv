import wikipediaapi
from openai import OpenAI, RateLimitError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import time

# wiki_wiki = wikipediaapi.Wikipedia(user_agent= 'SWEats (geoffreyxu@g.ucla.edu)', language='en')
# llm = OpenAI()

wiki_wiki = None
llm = None

tags_metadata = [
    {
        "name": "questions",
        "description": "Get a NAQT style trivia given an article title from the cache.\
            If OPENAI_USER_AGENT is set to 'DUMMY', the response will be a dummy response\
                instead of calling the chatbot."
    },
    {
        "name": "health",
        "description": "Health check for the API"
    }
]

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
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=os.environ['OPENAI_USER_AGENT'], language='en')
    llm = OpenAI()
    yield


app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

DUMMY_MODE = os.getenv("DUMMY_MODE", "False").lower() == "true"

@app.post("/questions", tags=["questions"])
def read_questions(articles: Articles)-> Questions:
    print("=== read_questions CALLED ===")
    """
    Given a list of article titles, generate a NAQT style trivia question for each article.
    
    Parameters
    ----------
    articles: A list of article titles.

    Returns
    -------
    questions: A list of NAQT style trivia questions.
    """

    questions = []
    ok = True
    error = ""
    print("reading questions")
    # FOR TESTING PURPOSES WITHOUT USING OPENAI OR WIKIPEDIA
    if DUMMY_MODE:
        print("Testing in DUMMY MODE")
        for title in articles.article_names:
            question = Question(prompt1="prompt1", prompt2="prompt2", prompt3="prompt3", answer=title)
            questions.append(question)
        time.sleep(len(articles.article_names) * 7) # Simulate a long wait time

        return Questions(questions=questions, ok=ok, error=error)
    
    for article_name in articles.article_names:
        print(f"Generating question for article {article_name}")
        page = wiki_wiki.page(article_name)
        if not page.exists():
            error = f"Article {article_name} does not exist."
            ok = False
            break
        

        prompt = "Create a NAQT style triva prompt using 3 clues which contain one fact each in decreasing obscurity given the following abstract:\n" + page.summary
        prompt += "\n Each clue should be less than 15 words long. The first clue should be prefaced with '1.', the second with '2.', and the third with '3.'. The answer should be prefaced with 'ANSWER:'."
        
        # NOTE: The following line actually makes the question generation significantly worse if used instead of the above line.
        # This is likely because the weird symbol makes the prompt out of distribution.

        # prompt += "\n The first clue should be prefaced with '*|*', the second with '*|*', and the third with *|*.'. The answer should be prefaced with '*|*'."

        if os.environ['OPENAI_USER_AGENT'] == 'DUMMY':
            question = Question(prompt1="1. Clue 1", prompt2="2. Clue 2", prompt3="3. Clue 3", answer="ANSWER: Answer")
            print(f"Dummy question for article {article_name}", flush=True)
            questions.append(question)
            continue

        while True:
            print("Hitting LLM")
            try: 
                completion = llm.chat.completions.create(
                    model="gpt-3.5-turbo",
                    # model="gpt-4.5-preview",
                    messages=[
                        {"role": "developer", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                # print(completion.choices[0].message, flush=True)
                print(completion.choices[0].message.content, flush=True)
                content = completion.choices[0].message.content
                print("=== LLM Raw Output ===", flush=True)
                print(content, flush=True)

                prompt1 = content.split("1.")[1].split("\n2.")[0].strip()
                prompt2 = content.split("\n2.")[1].split("\n3.")[0].strip()
                prompt3 = content.split("\n3.")[1].split("ANSWER:")[0].strip()
                answer = content.split("ANSWER:")[1].strip()

                if len(prompt1) and len(prompt2) and len(prompt3) and len(answer):
                    question = Question(prompt1=prompt1, prompt2=prompt2, prompt3=prompt3, answer=answer)
                    questions.append(question)
                    break
                else:
                    print(f"Invalid completion for article {article_name}. Trying again.", flush=True)
            
            except RateLimitError as e:
                if e.type == 'insufficient_quota':
                    error = "Out of money"
                    ok = False
                    break
                else:
                    print("Rate limit error. Trying again.", flush=True)

            except Exception as e:
                print("❌ Exception from LLM or missing fields:", e)
                break


        if not ok:
            break
    return Questions(questions=questions, ok=ok, error=error)

@app.get("/health", tags=["health"])
def health_check():
    if os.environ['OPENAI_USER_AGENT'] == 'DUMMY':
        return {"status": "healthy", "message": "Dummy mode is enabled."}
    return {"status": "healthy"}