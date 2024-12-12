import speech_recognition as sr
from time import sleep
from typing import List, Dict, Tuple
from groq import Groq
from difflib import get_close_matches
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic

def speech_to_text(topic:str) -> str:
    while True:
        recognizer = sr.Recognizer()
        print(f"We asked 100 people: {topic}")
        with sr.Microphone(sample_rate=48000, chunk_size=2048) as source:
                print("Speak something...")
                audio_data = recognizer.listen(source, phrase_time_limit=5)
        try:
            text = recognizer.recognize_google(audio_data).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, could not understand audio. Please speak clearer")
            continue
        except sr.RequestError as e:
            print("Error: Could not request results from Google Speech Recognition service")
            continue

def print_board(board: Dict[str, int], visited: Dict[str, bool], reveal: bool = False) -> None:
    for idx, (answer, points) in enumerate(board.items(), start=1):
        display = f"{answer} {points}" if visited[answer] or reveal else "#" * 10
        print(f"{idx}: {display}")

def steal(stealing_name: str, topic:str, board: Dict[str, int], visited: Dict[str, bool], client) -> Tuple[bool, int]:
    print("The", stealing_name, "family has a chance to steal!")
    sleep(2)
    answer = speech_to_text(topic)
    if answer in board and not visited[answer]:
        print("CORRECT!")
        sleep(.25)
        visited[answer] = True
        return board[answer], board
    else:
        closest = close_enough_AI(answer,visited, client)
        if closest == "null":
            print("WRONG")
            sleep(.5)
            return 0, board
        print("CORRECT!")
        sleep(.25)
        visited[closest] = True
        return board[closest], board
    
def decide_turn(name1: str, name2: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], client) -> Tuple[bool, int, Dict[str, bool]]:
    turn = 1
    chances = 0
    points_gained = False
    family_points = {name1: 0, name2: 0}

    while chances < 2 or not points_gained:
        current_family = name1 if turn == 1 else name2
        print(f"It's the {current_family}'s turn.")
        answer = speech_to_text(topic)
        
        if answer in board and not visited[answer]:
            print("CORRECT!")
            family_points[current_family] += board[answer]
            visited[answer] = True
            points_gained = True
        else:
            closest = close_enough_AI(answer, visited, client)
            if closest == "null":
                print("WRONG")
            else:
                print("CORRECT!")
                family_points[current_family] += board[closest]
                visited[closest] = True
                points_gained = True

        print_board(board, visited)
        sleep(0.75)
        chances += 1
        turn = 3 - turn

    winner = name1 if family_points[name1] >= family_points[name2] else name2
    return winner == name1, sum(family_points.values()), visited

def handle_turn(family_name: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], guesses: int, client) -> Tuple[int, bool]:
    turn_score = 0
    while guesses > 0:
        print(f"It's the {family_name} family's turn. You have {guesses} guesses remaining.")
        answer = speech_to_text(topic)
        if answer in board and not visited[answer]:
            print("CORRECT!")
            turn_score += board[answer]
            visited[answer] = True
        else:
            closest = close_enough_AI(answer, visited, client)
            if closest == "null":
                print("WRONG")
                guesses -= 1
            else:
                print("CORRECT!")
                turn_score += board[closest]
                visited[closest] = True
        print_board(board, visited)
        sleep(0.75)

        if all(visited.values()):
            print("All answers revealed!")
            return turn_score, True
    return turn_score, False



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

file = False
topic_AI = True


def main():
    """while True:
        question_mode = input("SELECT MODE. TYPE FILE (for custom games) OR AI (for randomly generated games) ")
        if question_mode.lower() == "file":
            numrounds = int(input("Number of rounds? "))
            filename = input("Directory to file? ")
            rounds = questions_from_file(numrounds,filename)
            break
        elif question_mode.lower() == "ai":
            numrounds = int(input("Number of rounds? "))
            temperature = float(input("TESTING: Input temperature from 0.0 to 1.0 (.7 being standard) "))
            rounds = questions_from_AI(numrounds, client)
            break
        else:
            print("INCORRECT MODE")"""
    client = Groq()
    rounds = questions_from_topic(5, client)
    family1_name = input("FAMILY 1. ENTER YOUR NAME NOW. MAY IT GO DOWN IN HISTORY. ")
    family2_name = input("FAMILY 2. ENTER YOUR NAME NOW. MAY YOUR JOURNEY THUS FAR BE HONORED. ")
    if family1_name == family2_name:
        family1_name += "(1)"
        family2_name += "(2)"
    score = {family1_name: 0, family2_name: 0}


    for topic in rounds:
        print(f"Current Scores:\n{family1_name}: {score[family1_name]}\n{family2_name}: {score[family2_name]}")
        board = rounds[topic]

        blackout = False
        visited = {i:False for i in board}
        turn_score = 0

        print("We asked 100 people," + topic)
        print_board(board, visited)
        sleep(1)
        if len(board) == 0:
            print("This topic has no questions!")
            sleep(2)
            continue
        family1_turn, turn_score, visited = decide_turn(family1_name,family2_name,topic,board,visited,client)
        if family1_turn:
            turn_score, blackout = handle_turn(family1_name, topic, board, visited, 3, client)
            if not blackout:
                steal_score, board = steal(family2_name, topic, board, visited,client)
                if steal_score > 0:
                    turn_score += steal_score
                    family1_turn = False
        else:
            turn_score, blackout = handle_turn(family2_name, topic, board, visited, 3, client)
            if not blackout:
                steal_score, board = steal(family1_name, topic, board, visited, client)
                if steal_score > 0:
                    turn_score += steal_score
                    family1_turn = True
        
        print_board(board,visited,True)
        sleep(1)

        score[family1_name] += turn_score if family1_turn else 0
        score[family2_name] += turn_score if not family1_turn else 0

    print(f"Final Scores:\n{family1_name}: {score[family1_name]}\n{family2_name}: {score[family2_name]}")

if __name__ == "__main__":
    main()