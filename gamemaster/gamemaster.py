import httpx
import re
import difflib
import psycopg2
import os

CACHE_SERVICE_URL = "http://cache:8000"
"""The URL for the cache service."""
MIN_ANSWER_SIMILARITY = 0.8
"""Minimum similarity ratio for accepting a user's answer."""
MIN_TOKEN_SIMILARITY = 0.5
"""Minimum similarity ratio based on common tokens for accepting a user's answer."""
DEFAULT_MAX_QUESTIONS = 5
"""Default maximum number of questions in a game."""
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": "postgres-db",
    "port": "5432"
}
"""Database configuration settings."""

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


class GameMaster:
    """
    Manages the game flow and logic for a single client.
    """
    def __init__(self, client_id, gm_instance_id, max_questions=DEFAULT_MAX_QUESTIONS):
        """
        Initializes a new GameMaster instance.

        Args:
            client_id (int): The ID of the client playing the game.
            gm_instance_id (str): A unique identifier for this GameMaster instance.
            max_questions (int, optional): The maximum number of questions for the game. Defaults to DEFAULT_MAX_QUESTIONS.
        """
        self.client_id = client_id
        """The ID of the client playing the game."""
        self.current_question = 0
        """The index of the current question."""
        self.score = 0
        """The player's current score."""
        self.id = gm_instance_id
        """A unique identifier for this GameMaster instance."""
        self.questions = []
        """A list to store the questions for the game."""
        self.max_questions = max_questions
        """The maximum number of questions for the game."""
        self.downvoted_questions = []
        """A list to store the IDs of downvoted questions."""

    async def load_questions(self):
        """
        Loads a batch of questions from the cache service.
        """
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
        """
        Retrieves hints for the current question.

        Returns:
            tuple: A tuple containing a list of hints (strings) and a boolean indicating if a question is available.
                   Returns ([], False) if there are no more questions.
        """
        # Implement logic to get the next hints
        await self.load_questions()
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            hints = [q["hint1"], q["hint2"], q["hint3"]]
            return hints, True
        else:
            return [], False
    
    def _normalize_answer(self, answer):
        """
        Normalizes an answer by converting it to lowercase, removing non-alphanumeric characters, and filtering out stop words.

        Args:
            answer (str): The answer to normalize.

        Returns:
            list: A list of normalized tokens.
        """
        STOP_WORDS = set(["the", "a", "an", "of", "in", "on", "at", "and", "or", "but", "from"])
        answer = answer.lower()
        answer = re.sub(r'[^\w\s]', '', answer) # remove non-words and non-whitespace
        tokens = answer.split()
        tokens = [token for token in tokens if token not in STOP_WORDS] # filter out common words
        return tokens
    
    def _advanced_answer_check(self, user_answer, correct_answer, threshold = MIN_ANSWER_SIMILARITY):
        """
        Performs an advanced check to determine if the user's answer is similar to the correct answer.

        Args:
            user_answer (str): The user's answer.
            correct_answer (str): The correct answer.
            threshold (float, optional): The minimum similarity ratio for accepting the answer. Defaults to MIN_ANSWER_SIMILARITY.

        Returns:
            bool: True if the user's answer is considered correct, False otherwise.
        """
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
        """
        Checks if the user's answer is correct.

        Args:
            answer (str): The user's answer.

        Returns:
            tuple: A tuple containing:
                - bool: True if the answer is correct, False otherwise.
                - int: The player's current score.
                - str: The correct answer.
                - list: A list of hints for the current question.
        """
        # Implement logic to check the answer
        await self.load_questions()

        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            correct_answer = q["answer"]

            if self._advanced_answer_check(answer, correct_answer):
                self.score += 10
                result = True
            else:
                result = False

            self.current_question += 1
            return result, self.score, correct_answer, [q["hint1"], q["hint2"], q["hint3"]]
        else:
            return False, self.score, "", []
        

    def downvote_question(self):
        """
        Downvotes the current question.

        Returns:
            str: The ID of the downvoted question.
        """
        index = self.current_question - 1
        if 0 <= index < len(self.questions):
            question = self.questions[index]
            self.downvoted_questions.append(question["id"])
            
        return question["id"]
    
    async def notify_downvoted_questions(self):
        """
        Notifies the cache service about the downvoted questions.
        """
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
        """
        Sends the game results to the database.
        """
        # Writing Results to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO game_results (game_id,user_id, score,game_length,game_timestamp)
            VALUES (%s ,%s, %s, %s, NOW())
        """, (self.id, self.client_id, self.score, len(self.questions)))
        for question_number,question in enumerate(self.questions):
            cursor.execute("""
                INSERT INTO questions_in_game (game_id, question_number,question_id)
                VALUES (%s,%s, %s)
            """, (self.id,question_number+1,question["id"]))
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
