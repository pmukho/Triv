

# @app.post("/{client_id}/question")
#     async def request_next_question(client_id: str):
#         gm = get_or_create_game_master(client_id)
#         question = await gm.get_next_question()
#         return {"question": question}

#     @app.post("/{client_id}/answer")
#     async def check_answer(client_id: str, answer: Answer):
#         gm = get_or_create_game_master(client_id)
#         is_correct = await gm.check_answer(answer.ans)
#         return {"correct": is_correct}

#     @app.post("/{client_id}/downvote")
#     async def downvote_question(client_id: str, downvote: DownVote):
#         gm = get_or_create_game_master(client_id)
#         await gm.downvote_question()
#         return {"status": "Downvote recorded"}

#     @app.post("/{client_id}/hints")
#     async def send_hints(client_id: str, hint: Hint):
#         gm = get_or_create_game_master(client_id)
#         await gm.send_hints(hint.hints)
#         return {"status": "Hints sent successfully"}

#     @app.post("/{client_id}/data")
#     async def send_data(client_id: str, data: Data):
#         # Implement data handling logic
#         return {"status": "Data sent successfully"}