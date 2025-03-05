import httpx
import re
import difflib
import psycopg2
import os

CACHE_SERVICE_URL = "http://cache:8000"
MIN_ANSWER_SIMILARITY = 0.8
MIN_TOKEN_SIMILARITY = 0.5
DEFAULT_MAX_QUESTIONS = 5
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": "postgres-db",
    "port": "5432"
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


class GameMaster:
    def __init__(self, client_id, gm_instance_id, max_questions=DEFAULT_MAX_QUESTIONS):
        self.client_id = client_id
        self.current_question = 0
        self.score = 0
        self.id = gm_instance_id
        self.questions = []
        self.max_questions = max_questions
        self.downvoted_questions = []

    async def load_questions(self):
        # Load batch from cache
        if self.questions:
            return

        # Prepare payload
        payload = {
            "user_id": str(self.client_id),
            "batch_size": 2,
            "batch": [{"category": "CAT1", "count": 3}, {"category": "CAT2", "count": 3}]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{CACHE_SERVICE_URL}/getbatch/", json=payload)
                response.raise_for_status()
                self.questions = response.json()["batch"]
                print("Loaded questions:", self.questions)
            except Exception as e:
                print("Error loading questions:", e)
                self.questions = []

    async def get_hints(self):
        # Implement logic to get the next hints
        await self.load_questions()
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            hints = [q["hint1"], q["hint2"], q["hint3"]]
            return hints, True
        else:
            return [], False
    
    def _normalize_answer(self, answer):
        STOP_WORDS = set(["the", "a", "an", "of", "in", "on", "at", "and", "or", "but", "from"])
        answer = answer.lower()
        answer = re.sub(r'[^\w\s]', '', answer) # remove non-words and non-whitespace
        tokens = answer.split()
        tokens = [token for token in tokens if token not in STOP_WORDS] # filter out common words
        return tokens
    
    def _advanced_answer_check(self, user_answer, correct_answer, threshold = MIN_ANSWER_SIMILARITY):
        user_tokens = self._normalize_answer(user_answer)
        correct_tokens = self._normalize_answer(correct_answer)
        
        if not user_tokens:
            return False

        if len(user_tokens) == 1:
            if user_tokens[0] in correct_tokens:
                return True

        user_str = ' '.join(user_tokens)
        correct_str = ' '.join(correct_tokens)
        ratio = difflib.SequenceMatcher(None, user_str, correct_str).ratio() # for spelling errors
        if ratio >= threshold:
            return True

        common_tokens = set(user_tokens) & set(correct_tokens) # for partial word match
        if len(common_tokens) >= len(user_tokens) * MIN_TOKEN_SIMILARITY:
            return True 

        return False

    async def check_answer(self, answer):
        # Implement logic to check the answer
        await self.load_questions()

        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            correct_answer = q["answer"]

            if self._advanced_answer_check(answer, correct_answer):
                self.score += 1
                result = True
            else:
                result = False

            self.current_question += 1
            return result, self.score, correct_answer, [q["hint1"], q["hint2"], q["hint3"]]
        else:
            return False, self.score, "", []
        

    def downvote_question(self):
        index = self.current_question - 1
        if 0 <= index < len(self.questions):
            question = self.questions[index]
            self.downvoted_questions.append(question["id"])
            
        return question["id"]
    
    async def notify_downvoted_questions(self):
        payload = {
            "user_id": str(self.client_id),
            "batch": self.downvoted_questions
        }

        async with httpx.AsyncClient() as client:
            try:
                print("Sending downvoted questions:", payload)
                response = await client.post(f"{CACHE_SERVICE_URL}/downvote/", json=payload)
                response.raise_for_status()
            except Exception as e:
                print("Error sending downvoted questions:", e)
        
        print(f"Downvoted questions sent {self.downvoted_questions}")
    
    async def send_results(self):
        # Writing Results to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO game_results (user_id, game_id, score)
            VALUES (%s ,%s, %s)
        """, (self.client_id, self.id, self.score))
        for question in self.questions:
            cursor.execute("""
                INSERT INTO questions_in_game (game_id, question_id)
                VALUES (%s, %s)
            """, (self.id, question["id"]))
        conn.commit()

        # Test if the data was written
        cursor.execute("SELECT * FROM questions_in_game WHERE game_id = '%s'", (self.id,))
        questions = cursor.fetchall()
        print("Inserted questions:", questions, flush=True)

        cursor.execute("SELECT * FROM game_results WHERE game_id = '%s'", (self.id,))
        results = cursor.fetchall()
        print("Inserted game results:", results, flush=True)

        cursor.close()
        conn.close()