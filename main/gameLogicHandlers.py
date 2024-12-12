from time import sleep
from typing import List, Dict, Tuple
from proximityMeasures import close_enough_AI
from SpeechtoText import speech_to_text

def print_board(board: Dict[str, int], visited: Dict[str, bool], reveal: bool = False) -> None:
    for idx, (answer, points) in enumerate(board.items(), start=1):
        display = f"{answer} {points}" if visited[answer] or reveal else "#" * 10
        print(f"{idx}: {display}")

def steal(stealing_name: str, topic:str, board: Dict[str, int], visited: Dict[str, bool], client) -> Tuple[bool, int]:
    print("The", stealing_name, "family has a chance to steal!")
    sleep(2)
    answer = speech_to_text(topic)
    print("Survey Says!")
    sleep(2)
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
        print("Survey Says!")
        sleep(2)
        
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
        print("Survey Says!")
        sleep(2)
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