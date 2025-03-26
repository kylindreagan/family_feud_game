from time import sleep
from typing import List, Dict, Tuple
from proximityMeasures import check_similarity
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

def display_fm_board(round: Dict[str, int], labels: List[QLabel]):
    idx = 0
    for answer, points in round.items():
        # Select the label for this answer
        label = labels[idx]
        
        # Display answer and points if it's visited or if reveal is True
        play_sound("sounds/fmding.mp3")
        display = f"{answer} ###"
        label.setText(str(idx+1)+": "+display)
        QApplication.processEvents()
        sleep(3)
        # Set the label text
        play_sound("sounds/surveysays.mp3")
        display = f"{answer} {points}"
        label.setText(str(idx+1)+": "+display)
        QApplication.processEvents()
        sleep(2)
        
        sleep(1)
        idx += 1


def steal(stealing_name: str, topic:str, board: Dict[str, int], visited: Dict[str, bool], client, topic_label=None, turn_label=None, info_label=None, voice = True, host= True, family_guise=None) -> Tuple[bool, int]:
    if turn_label == None:
        print("The", stealing_name, "family has a chance to steal!")
    else:
        turn_label.setText("The "+ stealing_name+ " family has a chance to steal!")
    sleep(2)
    
    if family_guise == None:
        if voice:
            answer = speech_to_text(topic, topic_label, info_label)
        else:
            dialog = AnswerDialog()
            dialog.exec_()  # This will block until the dialog is closed
            answer = dialog.get_data()
    else:
        answer = family_guise.get_answer(board, topic)
    
    if info_label == None:
        print(f"Show me {answer}!")
    else:
        info_label.setText(f"Show me {answer}!")
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
        closest = check_similarity(host, answer, visited, client)
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
    
def decide_turn(name1: str, name2: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], client, topic_label=None, turn_label=None, info_label=None, board_label=None, voice=False, host=True, family1_guise=None, family2_guise=None) -> Tuple[bool, int, Dict[str, bool]]:
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
        
        if current_family == name1 and family1_guise != None:
            answer = family1_guise.get_answer(board, topic)
        elif current_family == name2 and family2_guise != None:
            answer = family2_guise.get_answer(board, topic)
        else:
            if voice:
                answer = speech_to_text(topic, topic_label, info_label)
            else:
                dialog = AnswerDialog()
                dialog.exec_()  # This will block until the dialog is closed
                answer = dialog.get_data()
        
        if info_label == None:
            print(f"Show me {answer}!")
        else:
            info_label.setText(f"Show me {answer}!")
            QApplication.processEvents()
        sleep(1)
        
        if answer in board and not visited[answer]:
            if info_label == None:
                print("CORRECT!")
            else:
                info_label.setText("CORRECT!")
                QApplication.processEvents()
            if current_family != name1 and family1_guise != None:
                    family1_guise.add_opponent_answer(answer, True)
            elif current_family != name2 and family2_guise != None:
                family2_guise.add_opponent_answer(answer, True)
            if current_family == name1 and family1_guise != None:
                family1_guise.receive_feedback(answer, True)
            elif current_family == name2 and family2_guise != None:
                family2_guise.receive_feedback(answer, True)
            play_sound("sounds/correct.mp3")
            family_points[current_family] += board[answer]
            visited[answer] = True
            points_gained = True
        else:
            closest = check_similarity(host, answer, visited, client)
            if closest == "null":
                if info_label == None:
                    print("WRONG!")
                else:
                    info_label.setText("WRONG!")
                    QApplication.processEvents()
                if current_family != name1 and family1_guise != None:
                    family1_guise.add_opponent_answer(answer, False)
                elif current_family != name2 and family2_guise != None:
                    family2_guise.add_opponent_answer(answer, False)
                if current_family == name1 and family1_guise != None:
                    family1_guise.receive_feedback(answer, False)
                elif current_family == name2 and family2_guise != None:
                    family2_guise.receive_feedback(answer, False)
                play_sound("sounds/wrong.wav")
            else:
                if info_label == None:
                    print("CORRECT!")
                else:
                    info_label.setText("CORRECT!")
                    QApplication.processEvents()
                play_sound("sounds/correct.mp3")
                if current_family != name1 and family1_guise != None:
                    family1_guise.add_opponent_answer(answer, True)
                elif current_family != name2 and family2_guise != None:
                    family2_guise.add_opponent_answer(answer, True)
                if current_family == name1 and family1_guise != None:
                    family1_guise.receive_feedback(answer, True)
                elif current_family == name2 and family2_guise != None:
                    family2_guise.receive_feedback(answer, True)
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

def handle_turn(family_name: str, topic: str, board: Dict[str, int], visited: Dict[str, bool], guesses: int, client, topic_label=None, turn_label=None, info_label=None, board_label=None, voice=True, host=True, family_guise=None, opposite_guise=None) -> Tuple[int, bool]:
    turn_score = 0
    while guesses > 0:
        if turn_label != None:
            turn_label.setText(f"It's the {family_name} family's turn. You have {guesses} guesses remaining.")
            QApplication.processEvents()
        else:
            print(f"It's the {family_name} family's turn. You have {guesses} guesses remaining.")
        
        if family_guise != None:
            answer = family_guise.get_answer(board, topic)
        else:
            if voice:
                answer = speech_to_text(topic, topic_label, info_label)
            else:
                dialog = AnswerDialog()
                dialog.exec_()  # This will block until the dialog is closed
                answer = dialog.get_data()
        
        if info_label == None:
            print(f"Show me {answer}!")
        else:
            info_label.setText(f"Show me {answer}!")
            QApplication.processEvents()
        sleep(1)
        
        if answer in board and not visited[answer]:
            if info_label == None:
                print("CORRECT!")
            else:
                info_label.setText("CORRECT!")
                QApplication.processEvents()
            play_sound("sounds/correct.mp3")
            if opposite_guise != None:
                    opposite_guise.add_opponent_answer(answer, True)
            if family_guise != None:
                family_guise.receive_feedback(answer, True)
            turn_score += board[answer]
            visited[answer] = True
        else:
            closest = check_similarity(host, answer, visited, client)
            if closest == "null":
                if info_label == None:
                    print("WRONG!")
                else:
                    info_label.setText("WRONG!")
                    QApplication.processEvents()
                if opposite_guise != None:
                    opposite_guise.add_opponent_answer(answer, False)
                if family_guise != None:
                    family_guise.receive_feedback(answer, False)
                guesses -= 1
                play_sound("sounds/wrong.wav")
            else:
                if info_label == None:
                    print("CORRECT!")
                else:
                    info_label.setText("CORRECT!")
                    QApplication.processEvents()
                play_sound("sounds/correct.mp3")
                if opposite_guise != None:
                    opposite_guise.add_opponent_answer(answer, True)
                if family_guise != None:
                    family_guise.receive_feedback(answer, True)
                turn_score += board[closest]
                visited[closest] = True
        if board_label == None:
            print_board(board, visited)
        else:
            display_board(board,visited,board_label)
        sleep(0.75)

        if all(visited.values()):
            if info_label == None:
                print("All answers revealed!")
            else:
                info_label.setText("All answers revealed!")
                QApplication.processEvents()
            return turn_score, True
    return turn_score, False

def fast_money(rounds: Dict[str, List[str]], voice:bool, host:bool, client, topic_label, info_label, family_guise):
    first_round = {}
    second_round = {}
    for i in range(2):
        question = 1
        for topic in rounds:
            if topic_label != None:
                topic_label.setText(topic)
                QApplication.processEvents()
            else:
                print(topic)
            sleep(.5)
            board = rounds[topic]
            while True:
                if family_guise != None:
                    answer = family_guise.get_answer(board, topic)
                else:
                    if voice:
                        answer = speech_to_text(topic, topic_label, info_label)
                    else:
                        dialog = AnswerDialog()
                        dialog.exec_()  # This will block until the dialog is closed
                        answer = dialog.get_data()
                if info_label != None:
                    info_label.setText(f"You answered {answer}")
                else:
                    print(f"You answered {answer}")
                if i == 0:
                    break
                else:
                    if list(first_round.keys())[question] != answer.lower():
                        break
                    else:
                        if info_label == None:
                            print("Try Again")
                        else:
                            info_label.setText("Try Again")
                            QApplication.processEvents()
            
            if answer in board:
                score = board[answer]
            else:
                closest = check_similarity(host, answer, {x:False for x in board}, client)
                if closest == "null":
                    score = 0
                else:
                    score = board[closest]
            
            if i == 0:
                first_round[answer.lower()] = score
            else:
                second_round[answer.lower()] = score
        if family_guise != None:
            family_guise.clear_memory()
    
    return first_round, second_round