from gamemaster import GameMaster


class GmFactory:
    """
    A factory class to manage the creation and lifecycle of GameMaster instances.
    
    Attributes
    ----------
    game_masters : dict
        A dictionary to store active GameMaster instances with client_id as key.
    game_master_number : int
        A counter to assign unique identifiers to GameMaster instances.
        
    Methods
    -------
    get_or_create_game_master(client_id: int, max_questions: int) -> int
        Retrieves an existing GameMaster instance or creates a new one if it doesn't exist.
    end_game(client_id: int) -> int
        Ends the game for a given client_id, notifies downvoted questions, and sends results.
        Deletes the GameMaster instance from the dictionary.
        Returns the unique identifier of the ended GameMaster instance.
    """
    def __init__(self):
        self.game_masters = {}
        # Initialize the game_master_number to 0, could cause issues with too many game masters
        self.game_master_number = 1
        
    def get_or_create_game_master(self, client_id: int, max_questions: int) -> int:
        if client_id not in self.game_masters:
            self.game_masters[client_id] = GameMaster(client_id, self.game_master_number, max_questions)
            print(f"Game Master {self.game_master_number} with client_id: {client_id} created")
            self.game_master_number += 1
        return client_id
    
    async def end_game(self, client_id):
        gm = self.game_masters.get(client_id)
        await gm.notify_downvoted_questions()
        gm_id = gm.id
        print(f"Game Master for game number {gm_id} with client_id: {client_id} called to be ended", flush=True)
        await gm.send_results()
        del self.game_masters[client_id]

        print(f"Game Master for game number {gm_id} with client_id: {client_id} deleted",flush=True)
        return gm_id
