import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from time import sleep
from groq import Groq
from gameLogicHandlers import steal, decide_turn, handle_turn, display_board
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic
from qwindows import FileDialog


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

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap_image = QPixmap("images/logofued.png")
        self.image_label.setPixmap(pixmap_image)
        self.image_label.setGeometry(100, 100, 200, 150)
        main_layout.addWidget(self.image_label)

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
        self.info_label = QLabel("", self)
        self.voice_commands = QCheckBox("Use voice commands?", self)
        self.voice_commands.setChecked(self.voice)
        self.voice_commands.stateChanged.connect(self.voice_toggle)
        self.AI_use = QCheckBox("Use AI to generate questions?", self)
        self.AI_use.setChecked(self.AI)
        self.AI_use.stateChanged.connect(self.AI_toggle)
        self.num_rounds = QLineEdit(self)
        self.num_rounds.setPlaceholderText("Enter number of rounds: ")
        self.menu_button = QPushButton('Back to Menu', self)
        self.start_game_button.clicked.connect(self.reinit_widgets)

        self.score_label.setVisible(False)
        self.turn_label.setVisible(False)
        self.topic_label.setVisible(False)
        self.info_label.setVisible(False)
        self.menu_button.setEnabled(False)
        self.menu_button.setVisible(False)
        

        # Add widgets to the layout
        main_layout.addWidget(self.AI_use)
        main_layout.addWidget(self.num_rounds)
        main_layout.addWidget(self.voice_commands)
        main_layout.addLayout(name_input_layout)
        main_layout.addWidget(self.start_game_button)
        
        self.setLayout(main_layout)

    def start_game(self):
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
            dialog = FileDialog()
            dialog.exec_()  # This will block until the dialog is closed
            file_name = dialog.get_data()
            try:
                rounds = questions_from_file(num_rounds, "games/"+file_name+".txt")
            except Exception:
                rounds = questions_from_file(num_rounds)
        self.rounds = rounds

        self.run_game(family1_name, family2_name)

    def run_game(self, family1_name, family2_name):
        self.remove_initial_widgets()
        current_round = 0
        full_board = [self.board1,self.board2,self.board3,self.board4,self.board5,self.board6,self.board7,self.board8]
        for topic in self.rounds:
            self.update_game_info(family1_name, family2_name, topic, current_round)

            board = self.rounds[topic]
            blackout = False
            visited = {i: False for i in board}
            turn_score = 0

            display_board(board, visited, full_board)

            family1_turn, turn_score, visited = decide_turn(family1_name,family2_name,topic,board,visited,self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice) 
            if family1_turn:
                turn_score, blackout = handle_turn(family1_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice)
                if not blackout:
                    steal_score, board = steal(family2_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label, self.voice)
                    if steal_score > 0:
                        turn_score += steal_score
            else:
                turn_score, blackout = handle_turn(family2_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice)
                if not blackout:
                    steal_score, board = steal(family1_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label, self.voice)
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
        self.menu_button.setEnabled(True)
        self.menu_button.setVisible(True)
        
    def remove_initial_widgets(self):
        # Remove widgets related to game setup
        self.layout().removeWidget(self.image_label)
        self.layout().removeWidget(self.family1_name_input)
        self.layout().removeWidget(self.family2_name_input)
        self.layout().removeWidget(self.start_game_button)
        self.layout().removeWidget(self.AI_use)
        self.layout().removeWidget(self.voice_commands)
        self.layout().removeWidget(self.num_rounds)

        # Delete the widgets
        self.family1_name_input.setVisible(False)
        self.family2_name_input.setVisible(False)
        self.start_game_button.setVisible(False)
        self.AI_use.setVisible(False)
        self.voice_commands.setVisible(False)
        self.num_rounds.setVisible(False)
        self.image_label.setVisible(False)

        self.layout().addWidget(self.score_label)
        self.layout().addWidget(self.topic_label)
        self.layout().addWidget(self.turn_label)
        self.layout().addWidget(self.info_label)
        self.layout().addWidget(self.board1)
        self.layout().addWidget(self.board2)
        self.layout().addWidget(self.board3)
        self.layout().addWidget(self.board4)
        self.layout().addWidget(self.board5)
        self.layout().addWidget(self.board6)
        self.layout().addWidget(self.board7)
        self.layout().addWidget(self.board8)

        self.score_label.setVisible(True)
        self.turn_label.setVisible(True)
        self.topic_label.setVisible(True)
        self.info_label.setVisible(True)
    
    def reinit_widgets(self):
        self.menu_button.setEnabled(False)
        self.menu_button.setVisible(False)
        # Remove widgets related to game setup
        self.layout().addWidget(self.image_label)
        self.layout().addWidget(self.AI_use)
        self.layout().addWidget(self.num_rounds)
        self.layout().addWidget(self.voice_commands)
        self.layout().addWidget(self.family1_name_input)
        self.layout().addWidget(self.family2_name_input)
        self.layout().addWidget(self.start_game_button)

        # Delete the widgets
        self.family1_name_input.setVisible(True)
        self.family2_name_input.setVisible(True)
        self.start_game_button.setVisible(True)
        self.AI_use.setVisible(True)
        self.voice_commands.setVisible(True)
        self.num_rounds.setVisible(True)
        self.image_label.setVisible(True)

        self.layout().removeWidget(self.score_label)
        self.layout().removeWidget(self.topic_label)
        self.layout().removeWidget(self.turn_label)
        self.layout().removeWidget(self.info_label)
        self.layout().removeWidget(self.board1)
        self.layout().removeWidget(self.board2)
        self.layout().removeWidget(self.board3)
        self.layout().removeWidget(self.board4)
        self.layout().removeWidget(self.board5)
        self.layout().removeWidget(self.board6)
        self.layout().removeWidget(self.board7)
        self.layout().removeWidget(self.board8)

        self.score_label.setVisible(False)
        self.turn_label.setVisible(False)
        self.topic_label.setVisible(False)
        self.info_label.setVisible(False)

        self.board1.clear()
        self.board2.clear()
        self.board3.clear()
        self.board4.clear()
        self.board5.clear()
        self.board6.clear()
        self.board7.clear()
        self.board8.clear()

    def update_game_info(self, family1_name, family2_name, topic, round_num):
        self.topic_label.setText(f"We asked 100 people, {topic}")
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