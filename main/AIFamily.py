PROMPT_TEMPLATE = (
    "You are a member of a family playing Family Feud."
    "You will be given a topic and will have to return an answer as concisely as possible, only give the answers with no filler."
    "Do not repeat previous answers, you will be shown the current board before every guess."
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

        self.log.append({
        "role": "assistant",
        "content": chat_completion.choices[0].message.content
        })

        return chat_completion.choices[0].message.content
    
    def add_wrong_answer(self, wrong_answer):
        sent_message = f"The other family has said the answer {wrong_answer}, which was not on the board"
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