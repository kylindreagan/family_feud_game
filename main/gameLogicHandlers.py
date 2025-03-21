from time import sleep
from typing import List, Dict, Tuple
from proximityMeasures import close_enough_AI
from SpeechtoText import speech_to_text
from PyQt5.QtWidgets import QLabel, QApplication
from qwindows import AnswerDialog
from sound_player import play_sound

def print_board(board: Dict[str, int], visited: Dict[str, bool], reveal: bool = False) -> None:
    for idx, (answer, points) in enumerate(board.items(), start=1):
        display = f"{answer} {points}" if visited[answer] or reveal else "#" * 10
        print(f"{idx}: {display}")

def display_board(board: Dict[str, int], visited: Dict[str, bool], labels: List[QLabel], reveal: bool = False):
    idx = 0
    for answer, points in board.items():
        # Select the label for this answer
        label = labels[idx]
        
        # Display answer and points if it's visited or if reveal is True
        display = f"{answer} {points}" if visited.get(answer, False) or reveal else "#" * 10
        
        # Set the label text
        label.setText(str(idx+1)+": "+display)
        idx += 1

def steal(stealing_name: str, topic:str, board: Dict[str, int], visited: Dict[str, bool], client, topic_label=None, turn_label=None, info_label=None, voice = True) -> Tuple[bool, int]:
    if turn_label == None:
        print("The", stealing_name, "family has a chance to steal!")
    else:
        turn_label.setText("The "+ stealing_name+ " family has a chance to steal!")
    sleep(2)
    if voice:
        answer = speech_to_text(topic, topic_label, info_label)
    else:
        dialog = AnswerDialog()
        dialog.exec_()  # This will block until the dialog is closed
        answer = dialog.get_data()
    if info_label == None:
        print("Survey Says!")
    else:
        info_label.setText("Survey Says!")
        QApplication.processEvents()
    sleep(1)
    if answer in board and not visited[answer]:
        if info_label == None:
            print("CORRECT!")
        else:
            info_label.setText("CORRECT!")
            QApplication.processEvents()
        play_sound("sounds/correct.mp3")
        sleep(.25)
        visited[answer] = True
        return board[answer], board
    else:
        closest = close_enough_AI(answer,visited, client)
        if closest == "null":
            if info_label == None:
                print("WRONG!")
            else:
                info_label.setText("WRONG!")
                QApplication.processEvents()
            play_sound("sounds/wrong.wav")
            sleep(.5)
            return 0, board
        if info_label == None:
            print("CORRECT!")
        else:
            info_label.setText("CORRECT!")
            QApplication.processEvents()
        play_sound("sounds/correct.mp3")
        sleep(.25)
        visited[closest] = True
        return board[closest], board
    
def decide_turn(name1: str, name2: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], client, topic_label=None, turn_label=None, info_label=None, board_label=None, voice=False) -> Tuple[bool, int, Dict[str, bool]]:
    turn = 1
    chances = 0
    points_gained = False
    family_points = {name1: 0, name2: 0}

    while chances < 2 or not points_gained:
        current_family = name1 if turn == 1 else name2
        if turn_label == None:
            print(f"It's the {current_family}'s turn.")
        else:
            turn_label.setText(f"It's the {current_family} family's turn.")
            QApplication.processEvents()
        if voice:
            answer = speech_to_text(topic, topic_label, info_label)
        else:
            dialog = AnswerDialog()
            dialog.exec_()  # This will block until the dialog is closed
            answer = dialog.get_data()
        if info_label == None:
            print("Survey Says!")
        else:
            info_label.setText("Survey Says!")
            QApplication.processEvents()
        sleep(1)
        
        if answer in board and not visited[answer]:
            if info_label == None:
                print("CORRECT!")
            else:
                info_label.setText("CORRECT!")
                QApplication.processEvents()
            play_sound("sounds/correct.mp3")
            family_points[current_family] += board[answer]
            visited[answer] = True
            points_gained = True
        else:
            closest = close_enough_AI(answer, visited, client)
            if closest == "null":
                if info_label == None:
                    print("WRONG!")
                else:
                    info_label.setText("WRONG!")
                    QApplication.processEvents()
                play_sound("sounds/wrong.wav")
            else:
                if info_label == None:
                    print("CORRECT!")
                else:
                    info_label.setText("CORRECT!")
                    QApplication.processEvents()
                play_sound("sounds/correct.mp3")
                family_points[current_family] += board[closest]
                visited[closest] = True
                points_gained = True
        if board_label == None:
            print_board(board, visited)
        else:
            display_board(board,visited,board_label)
        sleep(0.75)
        chances += 1
        turn = 3 - turn

    winner = name1 if family_points[name1] >= family_points[name2] else name2
    return winner == name1, sum(family_points.values()), visited

def handle_turn(family_name: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], guesses: int, client, topic_label=None, turn_label=None, info_label=None, board_label=None, voice=True) -> Tuple[int, bool]:
    turn_score = 0
    while guesses > 0:
        if turn_label != None:
            turn_label.setText(f"It's the {family_name} family's turn. You have {guesses} guesses remaining.")
            QApplication.processEvents()
        else:
            print(f"It's the {family_name} family's turn. You have {guesses} guesses remaining.")
        if voice:
            answer = speech_to_text(topic, topic_label, info_label)
        else:
            dialog = AnswerDialog()
            dialog.exec_()  # This will block until the dialog is closed
            answer = dialog.get_data()
        if info_label == None:
            print("Survey Says!")
        else:
            info_label.setText("Survey Says!")
            QApplication.processEvents()
        sleep(1)
        if answer in board and not visited[answer]:
            if info_label == None:
                print("CORRECT!")
            else:
                info_label.setText("CORRECT!")
                QApplication.processEvents()
            play_sound("sounds/correct.mp3")
            turn_score += board[answer]
            visited[answer] = True
        else:
            closest = close_enough_AI(answer, visited, client)
            if closest == "null":
                if info_label == None:
                    print("WRONG!")
                else:
                    info_label.setText("WRONG!")
                    QApplication.processEvents()
                guesses -= 1
                play_sound("sounds/wrong.wav")
            else:
                if info_label == None:
                    print("CORRECT!")
                else:
                    info_label.setText("CORRECT!")
                    QApplication.processEvents()
                play_sound("sounds/correct.mp3")
                turn_score += board[closest]
                visited[closest] = True
        if board_label == None:
            print_board(board, visited)
        else:
            display_board(board,visited,board_label)
        sleep(0.75)

        if all(visited.values()):
            print("All answers revealed!")
            return turn_score, True
    return turn_score, False