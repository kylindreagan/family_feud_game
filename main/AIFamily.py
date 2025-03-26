PROMPT_TEMPLATE = (
    "You are a member of a family playing Family Feud."
    "You will be given a topic and will have to return an answer as concisely as possible, only give the answers with no filler."
    "You will be shown the current board with every guess, do not guess anything already on the board."
    "You will be shown your own answers and your opponents answers as they happen, do not repeat these either."
)

class Family_Guise:
    def __init__(self, client):
        self.client = client
        self.log=[
            {
            "role": "system", 
            "content": PROMPT_TEMPLATE,
             },
        ]
    
    def get_answer(self, board, topic):
        str_board = '\n'.join([' '.join(sublist) for sublist in board])
        sent_message = f"TOPIC:{topic} CURRENT BOARD:{str_board}"
        
        self.log.append({
                "role": "user",
                "content": sent_message,
            })
        
        chat_completion = self.client.chat.completions.create(
        messages=self.log,
        model="llama3-8b-8192",
        stream=False,
        )

        return chat_completion.choices[0].message.content
    
    def add_opponent_answer(self, answer, correct):
        if not correct:
            sent_message = f"The other family has said the answer {answer}, which was not on the board"
            self.log.append({
                    "role": "user",
                    "content": sent_message,
                })
        else:
            sent_message = f"The other family has said the answer {answer}, which was on the board"
            self.log.append({
                    "role": "user",
                    "content": sent_message,
                })
    
    def receive_feedback(self, answer, correct):
        if not correct:
            sent_message = f"Your answer of {answer} was incorrect and not on the board."
            self.log.append({
                    "role": "user",
                    "content": sent_message,
                })
        else:
            sent_message = f"Your answer of {answer} was correct and on the board."
            self.log.append({
                    "role": "user",
                    "content": sent_message,
                })

    def clear_memory(self):
        self.log=[
            {
            "role": "system", 
            "content": PROMPT_TEMPLATE,
             },
        ]