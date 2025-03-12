from gamemaster import GameMaster

class GmFactory:
    """
    Factory class for managing GameMaster instances and game sessions.
    
    Maintains a registry of active game sessions and handles their lifecycle.
    """
    
    def __init__(self):
        """
        Initializes a new GmFactory instance with empty game masters registry.
        Creates first game master with ID 1 to avoid zero-based indexing issues.
        """
        self.game_masters = {}
        """Dictionary mapping client IDs to GameMaster instances (client_id: GameMaster)."""
        self.game_master_number = 1
        """Auto-incrementing counter for generating unique game instance IDs."""

    def get_or_create_game_master(self, client_id: int, max_questions: int) -> int:
        """
        Retrieves or creates a GameMaster instance for a client.

        Args:
            client_id (int): Unique identifier for the client
            max_questions (int): Maximum number of questions for the game session

        Returns:
            int: Client ID used as the key in the game masters registry

        Note:
            Creates new GameMaster if none exists for the client ID
            Auto-increments game master ID for each new creation
        """
        if client_id not in self.game_masters:
            self.game_masters[client_id] = GameMaster(client_id, self.game_master_number, max_questions)
            print(f"Game Master {self.game_master_number} with client_id: {client_id} created")
            self.game_master_number += 1
        return client_id
    
    async def end_game(self, client_id) -> int:
        """
        Properly terminates a game session and cleans up resources.

        Args:
            client_id: Client ID whose game should be ended

        Returns:
            int: ID of the ended game instance

        Raises:
            KeyError: If no game exists for the specified client ID

        Performs:
            1. Notifies cache service about downvoted questions
            2. Sends final results to database
            3. Removes game instance from registry
            4. Logs game termination
        """
        gm = self.game_masters.get(client_id)
        await gm.notify_downvoted_questions()
        gm_id = gm.id
        print(f"Game Master for game number {gm_id} with client_id: {client_id} called to be ended", flush=True)
        await gm.send_results()
        del self.game_masters[client_id]

        print(f"Game Master for game number {gm_id} with client_id: {client_id} deleted",flush=True)
        return gm_id
