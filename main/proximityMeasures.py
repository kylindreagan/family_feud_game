from difflib import get_close_matches
from typing import List, Dict, Tuple
from qwindows import HostDialog

def check_similarity(AI:bool, answer:str, visited:Dict[str, bool], client) -> str:
    unvisited = [x.lower() for x in visited if not visited[x]]
    inverse_visited = [not visited[x] for x in visited]
    first_chance = string_sim(answer, unvisited)
    if first_chance == "null":
        if AI:
            return close_enough_AI(answer, unvisited, client)
        else:
            return close_enough(answer, inverse_visited, unvisited)
    else: return first_chance

def close_enough(answer:str, is_visited:List[bool], unvisited:List[str]) -> str:
    while True:
        dialog = HostDialog(answer)
        dialog.exec_()  # This will block until the dialog is closed
        choice = dialog.get_data()
        #checks if choice in bounds and either null or a number that isn't on the board
        if (not choice.isnumeric() and choice != "null") or (choice.isnumeric() and (int(choice) < 0 or int(choice) > len(is_visited) or is_visited[int(choice)-1] != True)):
            print("INVALID")
        else:
            return unvisited[int(choice)-1] if choice.isnumeric() else choice

def close_enough_AI(answer:str, unvisited: List[str], client) -> str:
    possible = " ".join(unvisited)
    sent_message = f"ANSWER: {answer} POSSIBLE: {possible}"
    chat_completion = client.chat.completions.create(
        messages=[
            {
            "role": "system", 
            "content": "You are a backstage producer of Family Feud. Your job is to decide if a contestant's answer matches any unvisited answers on the board. Be strict and logical: 1. Exact matches are always acceptable. 2. Accept partial matches only if they are highly similar (e.g., share key words or concepts). Avoid overly broad interpretations. 3. If no acceptable matches are found, respond only with 'null'. Respond with the exact match from the board if there is one or 'null' otherwise. Never add explanations, comments, or other text.",
             },
            {
                "role": "user",
                "content": sent_message,
            }
        ],
        model="llama3-8b-8192",
        stream=False,
    )
    response = chat_completion.choices[0].message.content.lower()
    if response in unvisited or response == "null":
        return response
    
    else: return "null"

def string_sim(answer:str, unvisited: List[str]) -> str:
    closest_match = get_close_matches(answer.lower(), unvisited, n=1, cutoff=0.8)
    return closest_match[0] if closest_match else "null"