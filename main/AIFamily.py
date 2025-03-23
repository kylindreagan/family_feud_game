from groq import Groq

PROMPT_TEMPLATE = (
    "You are a member of a family playing Family Feud."
    "You will be given a topic and will have to return an answer as concisely as possible"
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
        ],
    
    def get_answer(self, board, topic):
        str_board = '\n'.join([' '.join(sublist) for sublist in board])
        sent_message = f"TOPIC:{topic} CURRENT BOARD:{str_board}"
        self.log.append({
                "role": "user",
                "content": sent_message,
            })
        
