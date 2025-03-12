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
    """
    A class to manage the game state, including loading questions, checking answers, and managing scores.
    
    Attributes
    ----------
    client_id : int
        The unique identifier for the client.
    current_question : int
        The index of the current question being asked.
    score : int
        The current score of the player.
    id : int
        The unique identifier for the game instance.
    questions : list
        A list of questions for the game.
    max_questions : int
        The maximum number of questions allowed in the game.
    downvoted_questions : list
        A list of questions that have been downvoted by the player.
        
    Methods
    -------
    load_questions()
        Loads a batch of questions from the cache service.
    get_hints()
        Retrieves hints for the current question.
    check_answer(answer: str)
        Checks the player's answer against the correct answer.
    downvote_question()
        Records a downvote for the current question.
    notify_downvoted_questions()
        Notifies the cache service of downvoted questions.
    send_results()
        Sends the game results to the database.
    """
    def __init__(self, client_id, gm_instance_id, max_questions=DEFAULT_MAX_QUESTIONS):
        self.client_id = client_id
        self.current_question = 0
        self.score = 0
        self.id = gm_instance_id
        self.questions = []
        self.scores = []
        self.hints_used = []
        self.max_questions = max_questions
        self.downvoted_questions = []
        self.category_select = None  # Store category selection

    async def load_questions(self, categorySelect=None):
        # Load batch from cache
        if self.questions:
            return

        # Update stored category selection if new one provided
        if categorySelect is not None:
            self.category_select = categorySelect
        
        # Prepare payload
        payload = None
        
        if not self.category_select or not isinstance(self.category_select, dict):
            payload = {
                "user_id": str(self.client_id),
                "batch_size": 2,
                "batch": [{"category": "CAT1", "count": 3}, {"category": "CAT2", "count": 3}]
            }
        else:
            payload = {
                "user_id": str(self.client_id),
                "batch": [],
                "batch_size": 0
            }
            for cat, count in self.category_select.items():
                if count > 0:
                    payload["batch"].append({"category": cat, "count": count})
            payload["batch_size"] = len(payload["batch"])

        print("Payload for loading questions:", payload)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{CACHE_SERVICE_URL}/getbatch/", json=payload)
                response.raise_for_status()
                self.questions = response.json()["batch"]
                self.scores = [0 for _ in range(len(self.questions))]
                self.hints_used = [0 for _ in range(len(self.questions))]
                print("Loaded questions:", self.questions)
            except Exception as e:
                print("Error loading questions:", e)
                self.questions = []

    async def get_hints(self, categorySelect):
        # Update stored category selection
        if categorySelect is not None:
            self.category_select = categorySelect
            
        # Implement logic to get the next hints
        await self.load_questions()
        
        # If we've answered all our loaded questions but haven't reached max_questions,
        # we need to load more
        if self.current_question >= len(self.questions) and self.current_question < self.max_questions:
            # Clear questions to force loading more
            self.questions = []
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

    async def check_answer(self, answer, hintsUsed):
        # Implement logic to check the answer
        await self.load_questions()

        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            correct_answer = q["answer"]

            if self._advanced_answer_check(answer, correct_answer):
                self.scores[self.current_question] = 40 - 10*hintsUsed
                self.score += self.scores[self.current_question]
                self.hints_used[self.current_question] = hintsUsed
                result = True
            else:
                result = False

            self.current_question += 1
            
            # If we've used all questions but haven't reached max_questions,
            # clear questions to force loading more in next get_hints call
            if self.current_question >= len(self.questions) and self.current_question < self.max_questions:
                self.questions = []
                
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
            INSERT INTO game_results (game_id,user_id, score,game_length,game_timestamp)
            VALUES (%s ,%s, %s, %s, NOW())
        """, (self.id, self.client_id, self.score, len(self.questions)))
        conn.commit()

        n = len(self.questions)
        for i in range(n):
            category = self.questions[i]["category"]
            score = self.scores[i]

            if score > 0:
                query = """
                    INSERT INTO metrics (user_id, category, correct_count, total_count, avg_hints_used)
                    VALUES (%s, %s, 1, 1, %s)
                    ON CONFLICT (user_id, category) DO UPDATE
                    SET correct_count = metrics.correct_count + 1,
                        total_count = metrics.total_count + 1,
                        avg_hints_used = (metrics.avg_hints_used * metrics.correct_count + %s) / (metrics.correct_count + 1)
                """
                params = (self.client_id, category, self.hints_used[i], self.hints_used[i])
            else:
                query = """
                    INSERT INTO metrics (user_id, category, correct_count, total_count)
                    VALUES (%s, %s, 0, 1)
                    ON CONFLICT (user_id, category) DO UPDATE
                    SET total_count = metrics.total_count + 1
                """
                params = (str(self.client_id), category)
            
            cursor.execute(query, params)
            conn.commit()

        cursor.close()
        conn.close()