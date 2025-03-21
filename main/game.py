import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
from time import sleep
from groq import Groq
from gameLogicHandlers import steal, decide_turn, handle_turn, display_board
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic


class FamilyFeudApp(QWidget):
    def __init__(self):
        super().__init__()
        self.client = Groq()
        self.AI = True
        self.voice = True
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Family Feud Game')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Create widgets for entering family names
        self.family1_name_input = QLineEdit(self)
        self.family1_name_input.setPlaceholderText("Family 1 - Enter your name")
        self.family2_name_input = QLineEdit(self)
        self.family2_name_input.setPlaceholderText("Family 2 - Enter your name")

        name_input_layout = QVBoxLayout()
        name_input_layout.addWidget(self.family1_name_input)
        name_input_layout.addWidget(self.family2_name_input)

        # Button to start the game
        self.start_game_button = QPushButton('Start Game', self)
        self.start_game_button.clicked.connect(self.start_game)

        # Labels for displaying the scores and game info
        self.score_label = QLabel("Current Scores:\nFamily 1: 0\nFamily 2: 0", self)
        self.topic_label = QLabel("Topic: None", self)
        self.turn_label = QLabel("Turn: None", self)
        self.board1 = QLabel("", self)
        self.board2 = QLabel("", self)
        self.board3 = QLabel("", self)
        self.board4 = QLabel("", self)
        self.board5 = QLabel("", self)
        self.board6 = QLabel("", self)
        self.board7 = QLabel("", self)
        self.board8 = QLabel("", self)
        self.board9 = QLabel("", self)
        self.board10 = QLabel("", self)
        self.info_label = QLabel("", self)
        self.voice_commands = QCheckBox("Use voice commands?", self)
        self.voice_commands.setChecked(self.voice)
        self.voice_commands.stateChanged.connect(self.voice_toggle)
        self.AI_use = QCheckBox("Use AI to generate questions?", self)
        self.AI_use.setChecked(self.AI)
        self.AI_use.stateChanged.connect(self.AI_toggle)
        self.num_rounds = QLineEdit(self)
        self.num_rounds.setPlaceholderText("Enter number of rounds: ")

        # Add widgets to the layout
        main_layout.addWidget(self.AI_use)
        main_layout.addWidget(self.num_rounds)
        main_layout.addWidget(self.voice_commands)
        main_layout.addLayout(name_input_layout)
        main_layout.addWidget(self.start_game_button)
        main_layout.addWidget(self.score_label)
        main_layout.addWidget(self.topic_label)
        main_layout.addWidget(self.turn_label)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.board1)
        main_layout.addWidget(self.board2)
        main_layout.addWidget(self.board3)
        main_layout.addWidget(self.board4)
        main_layout.addWidget(self.board5)
        main_layout.addWidget(self.board6)
        main_layout.addWidget(self.board7)
        main_layout.addWidget(self.board8)
        main_layout.addWidget(self.board9)
        main_layout.addWidget(self.board10)
        

        self.setLayout(main_layout)

    def start_game(self):
        # Initialize game logic
        family1_name = self.family1_name_input.text()
        family2_name = self.family2_name_input.text()

        if family1_name == family2_name:
            family1_name += "(1)"
            family2_name += "(2)"
        
        self.score = {family1_name: 0, family2_name: 0}

        num_rounds = self.num_rounds.text()
        if not num_rounds.isnumeric():
            num_rounds = 1
        else:
            num_rounds = int(num_rounds)

        if self.AI:
            rounds = questions_from_topic(num_rounds, self.client, True)
        else:
            rounds = questions_from_file(num_rounds)
        self.rounds = rounds

        self.run_game(family1_name, family2_name)

    def run_game(self, family1_name, family2_name):
        current_round = 0
        full_board = [self.board1,self.board2,self.board3,self.board4,self.board5,self.board6,self.board7,self.board8,self.board9,self.board10]
        for topic in self.rounds:
            self.update_game_info(family1_name, family2_name, topic, current_round)

            board = self.rounds[topic]
            blackout = False
            visited = {i: False for i in board}
            turn_score = 0

            display_board(board, visited, full_board)

            family1_turn, turn_score, visited = decide_turn(family1_name,family2_name,topic,board,visited,self.client, self.topic_label, self.turn_label, self.info_label, full_board) 
            if family1_turn:
                turn_score, blackout = handle_turn(family1_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board)
                if not blackout:
                    steal_score, board = steal(family2_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label)
                    if steal_score > 0:
                        turn_score += steal_score
            else:
                turn_score, blackout = handle_turn(family2_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board)
                if not blackout:
                    steal_score, board = steal(family1_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label)
                    if steal_score > 0:
                        turn_score += steal_score
            
            # Update scores
            self.score[family1_name] += turn_score if family1_turn else 0
            self.score[family2_name] += turn_score if not family1_turn else 0
            display_board(board, visited, full_board, True)
            sleep(2)

            current_round += 1
            sleep(.25)

            # Update the UI with new scores
            self.update_game_info(family1_name, family2_name, topic, current_round)

        self.final_scores(family1_name, family2_name)
        
    
    def update_game_info(self, family1_name, family2_name, topic, round_num):
        self.topic_label.setText(f"Topic: {topic}")
        self.turn_label.setText(f"Round: {round_num + 1}")
        self.score_label.setText(f"Current Scores:\n{family1_name}: {self.score[family1_name]}\n{family2_name}: {self.score[family2_name]}")

    def final_scores(self, family1_name, family2_name):
        self.score_label.setText(f"Final Scores:\n{family1_name}: {self.score[family1_name]}\n{family2_name}: {self.score[family2_name]}")
        self.turn_label.setText("Game Over!")
    
    def AI_toggle(self):
        self.AI = not self.AI

    def voice_toggle(self):
        self.voice = not self.voice

def main():
    app = QApplication(sys.argv)
    ex = FamilyFeudApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()