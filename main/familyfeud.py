from time import sleep
from groq import Groq
from gameLogicHandlers import steal, decide_turn, handle_turn, print_board
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic

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