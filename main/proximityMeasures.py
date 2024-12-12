from difflib import get_close_matches
from typing import List, Dict, Tuple

def close_enough_AI(answer:str, visited: Dict[str, bool], model_client) -> str:
    unvisited = [x for x in visited if visited[x] != True]
    possible = " ".join(unvisited)
    sent_message = f"ANSWER: {answer} POSSIBLE: {possible}"
    chat_completion = model_client.chat.completions.create(
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

    # Fallback to string similarity if model response is invalid
    return close_enough(answer, unvisited)

def close_enough(answer:str, unvisited: List) -> str:
    closest_match = get_close_matches(answer, unvisited, n=1, cutoff=0.8)
    return closest_match[0] if closest_match else "null"