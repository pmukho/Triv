import asyncio
import aiohttp
import gamemaster.gmfactory as gmfactory


# Main function to run all API calls asynchronously
async def main():
    async with aiohttp.ClientSession() as session:
        # Example usage of the functions
        gm_instance_id = "12345"
        client_id = "67890"
        question_id = 101
        ans = "A"
        down_vote = True
        hints = ["Hint 1", "Hint 2", "Hint 3"]
        metrics_data = {
            "1": {  # category_i, for example category_1
                "101": {  # question_id
                    "Time_taken": "2025-02-16T10:30:00Z",  # DateTime format
                    "Num_hints": 3,
                    "Submission": "correct"  # enum[correct, wrong, null]
                },
                "102": {
                    "Time_taken": "2025-02-16T10:45:00Z",
                    "Num_hints": 2,
                    "Submission": "wrong"
                }
            },
            "2": {  # category_2
                "103": {
                    "Time_taken": "2025-02-16T10:50:00Z",
                    "Num_hints": 1,
                    "Submission": "null"
                }
            }
        }

        # Request Next Question
        next_question_response = await gmfactory.request_next_question(session, gm_instance_id)
        print(next_question_response)

        # Check Answer
        check_answer_response = await gmfactory.check_answer(session, gm_instance_id, question_id, ans)
        print(check_answer_response)

        # Downvote Question
        downvote_response = await gmfactory.downvote_question(session, gm_instance_id, question_id, down_vote)
        print(downvote_response)

        # Send Hints
        send_hints_response = await gmfactory.send_hints(session, client_id, question_id, hints)
        print(send_hints_response)

        # Send Data
        send_data_response = await gmfactory.send_data(session, client_id, metrics_data)
        print(send_data_response)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())