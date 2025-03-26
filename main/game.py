import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from time import sleep
from groq import Groq
from gameLogicHandlers import steal, decide_turn, handle_turn, display_board, display_fm_board, fast_money
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic, fast_money_from_file, fast_money_from_topics
from qwindows import FileDialog, EmailDialog, ContinueDialog, ErrorDialog
from sound_player import play_sound, stop_sound
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from AIFamily import Family_Guise

#Fill these in with your own email, potential way around this in the works.
SENDER_EMAIL =  None
SENDER_PASSWORD = None

class FamilyFeudApp(QWidget):
    def __init__(self):
        super().__init__()
        self.client = Groq()
        self.AI = True
        self.voice = True
        self.host = True
        self.email = None
        self.family1 = False
        self.family2 = False
        self.multiplier = 1
        self.play_fast_money = True
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Family Feud Game')
        self.setGeometry(100, 100, 800, 600)

        self.main_layout = QVBoxLayout()

        self.family1_name_input = QLineEdit(self)
        self.family1_name_input.setPlaceholderText("Family 1 - Enter your name")
        self.family2_name_input = QLineEdit(self)
        self.family2_name_input.setPlaceholderText("Family 2 - Enter your name")
        self.AI_family1 = QCheckBox("Have family 1 be AI?")
        self.AI_family1.setChecked(self.family1)
        self.AI_family1.stateChanged.connect(self.family1_toggle)
        self.AI_family2 = QCheckBox("Have family 2 be AI?")
        self.AI_family2.setChecked(self.family2)
        self.AI_family2.stateChanged.connect(self.family2_toggle)

        name_input_layout = QVBoxLayout()
        name_input_layout.addWidget(self.family1_name_input)
        name_input_layout.addWidget(self.AI_family1)
        name_input_layout.addWidget(self.family2_name_input)
        name_input_layout.addWidget(self.AI_family2)

        self.start_game_button = QPushButton('Start Game', self)
        self.start_game_button.clicked.connect(self.start_game)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap_image = QPixmap("images/logofued.png")
        self.image_label.setPixmap(pixmap_image)
        self.image_label.setGeometry(100, 100, 200, 150)
        self.main_layout.addWidget(self.image_label)

        self.score_label = QLabel("Current Scores:\nFamily 1: 0\nFamily 2: 0", self)
        self.topic_label = QLabel("Topic: None", self)
        self.turn_label = QLabel("Turn: None", self)
        self.mult_label = QLabel("", self)
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
        self.AI_host = QCheckBox("Use AI host instead of human host?", self)
        self.AI_host.setChecked(self.host)
        self.AI_host.stateChanged.connect(self.host_toggle)
        self.fm_check = QCheckBox("Have a fast money round?", self)
        self.fm_check.setChecked(self.play_fast_money)
        self.fm_check.stateChanged.connect(self.fm_toggle)

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
        
        self.main_layout.addWidget(self.AI_use)
        self.main_layout.addWidget(self.num_rounds)
        self.main_layout.addWidget(self.voice_commands)
        self.main_layout.addLayout(name_input_layout)
        self.main_layout.addWidget(self.AI_host)
        self.main_layout.addWidget(self.fm_check)
        self.main_layout.addWidget(self.start_game_button)
        
        self.setLayout(self.main_layout)
        self.fmboardA = [QLabel("", self) for _ in range(5)]
        self.fmboardB = [QLabel("", self) for _ in range(5)]


        self.theme = play_sound("sounds/themesong.mp3")

    def start_game(self):
        if not self.host:
            dialog = EmailDialog()
            dialog.exec_()  # This will block until the dialog is closed
            email = dialog.get_data()
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)  != None:
                self.email = email
        family1_name = self.family1_name_input.text()
        family2_name = self.family2_name_input.text()

        if family1_name == family2_name:
            family1_name += "(1)"
            family2_name += "(2)"
        
        self.score = {family1_name: 0, family2_name: 0}

        n = self.num_rounds.text()
        if not n.isnumeric():
            n = 1
        else:
            n = int(n)
            if n < 1:
                n = 1

        if self.AI:
            rounds = questions_from_topic(n, self.client, True)
        else:
            dialog = FileDialog()
            dialog.exec_()  # This will block until the dialog is closed
            file_name = dialog.get_data()
            try:
                rounds = questions_from_file(n, "games/"+file_name+".txt")
            except Exception:
                rounds = questions_from_file(n)
        self.rounds = rounds

        family1_guise = Family_Guise(self.client) if self.family1 else None
        family2_guise = Family_Guise(self.client) if self.family2 else None

        self.run_game(n, family1_name, family2_name, family1_guise, family2_guise)

    def run_game(self, n, family1_name, family2_name, family1_guise, family2_guise):
        stop_sound(self.theme)
        self.remove_initial_widgets()
        current_round = 0
        full_board = [self.board1,self.board2,self.board3,self.board4,self.board5,self.board6,self.board7,self.board8]
        
        for topic in self.rounds:
            if self.multiplier == 2:
                self.mult_label.setText("DOUBLE")
            elif self.multiplier == 3:
                self.mult_label.setText("TRIPLE")
            elif self.multiplier != 1:
                self.mult_label.setText(f"{self.multiplier}x ROUND")

            self.clear_board()
                       
            self.update_game_info(family1_name, family2_name, topic, current_round)

            board = self.rounds[topic]

            if len(board) == 0:
                dialog = ErrorDialog()
                dialog.exec_()  # This will block until the dialog is closed
                continue

            if self.email != None:
                body = "" 
                for idx, (answer, points) in enumerate(board.items(), start=1):
                    display = f"{idx}:{answer} {points} \n"
                    body.join(display)
                self.send_email(self.email, f"Family Feud Round {current_round+1}", body, "smtp.gmail.com", 465, SENDER_EMAIL, SENDER_PASSWORD)

            blackout = False
            visited = {i: False for i in board}
            turn_score = 0
            is_steal = False

            display_board(board, visited, full_board)

            family1_turn, turn_score, visited = decide_turn(family1_name,family2_name,topic,board,visited,self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice, self.host, family1_guise, family2_guise) 
            if family1_turn:
                turn_score, blackout = handle_turn(family1_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice, self.host, family1_guise, family2_guise)
                if not blackout:
                    steal_score, board = steal(family2_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label, self.voice, self.host, family2_guise)
                    if steal_score > 0:
                        turn_score += steal_score
                        is_steal = True
            else:
                turn_score, blackout = handle_turn(family2_name, topic, board, visited, 3, self.client, self.topic_label, self.turn_label, self.info_label, full_board, self.voice, self.host, family2_guise, family1_guise)
                if not blackout:
                    steal_score, board = steal(family1_name, topic, board, visited, self.client, self.topic_label, self.turn_label, self.info_label, self.voice, self.host, family1_guise)
                    if steal_score > 0:
                        turn_score += steal_score
                        is_steal = True
            
            turn_score *= self.multiplier
            # Update scores
            if not is_steal:
                self.score[family1_name] += turn_score if family1_turn else 0
                self.score[family2_name] += turn_score if not family1_turn else 0
            else:
                self.score[family2_name] += turn_score if family1_turn else 0
                self.score[family1_name] += turn_score if not family1_turn else 0
            display_board(board, visited, full_board, True)
            sleep(2)

            current_round += 1
            if current_round >= n-2:
                self.multiplier += 1
            sleep(.25)

            # Update the UI with new scores
            self.update_game_info(family1_name, family2_name, topic, current_round)
            play_sound("sounds/roundend.mp3")
            dialog = ContinueDialog()
            dialog.exec_()  # This will block until the dialog is closed

            if self.family1:
                family1_guise.clear_memory()
            
            if self.family2:
                family2_guise.clear_memory()


        self.final_scores(family1_name, family2_name)

        if self.play_fast_money:
            self.start_fm()
            if self.AI:
                fm_rounds = fast_money_from_topics(self.client, True)
            else:
                dialog = FileDialog()
                dialog.exec_()  # This will block until the dialog is closed
                file_name = dialog.get_data()
                try:
                    fm_rounds = fast_money_from_file(5, "games/"+file_name+".txt")
                except Exception:
                    fm_rounds = fast_money_from_file(5)
            
            if self.score[family1_name] >= self.score[family2_name]:
                self.score_label.setText(f"{family1_name}:0")
                first_round, second_round = fast_money(fm_rounds, self.voice, self.AI_host, self.client, self.topic_label, self.info_label, family1_guise)
            
            else:
                self.score_label.setText(f"{family1_name}:0")
                first_round, second_round = fast_money(fm_rounds, self.voice, self.AI_host, self.client, self.topic_label, self.info_label, family2_guise)
            
            x = sum(first_round.values())
            display_fm_board(first_round, self.fmboardA)
            self.score_label.setText(f"{family1_name}:{x}")
            dialog = ContinueDialog()
            dialog.exec_()  # This will block until the dialog is closed

            y = sum(second_round.values())
            display_fm_board(second_round, self.fmboardB)
            self.score_label.setText(f"{family1_name}:{x+y}")
            
            if x+y >= 200:
                play_sound("sounds/win.mp3")
            
            dialog = ContinueDialog()
            dialog.exec_()  # This will block until the dialog is closed

            self.end_fm()
        
    def remove_initial_widgets(self):
        # Remove widgets related to game setup
        self.layout().removeWidget(self.image_label)
        self.layout().removeWidget(self.family1_name_input)
        self.layout().removeWidget(self.family2_name_input)
        self.layout().removeWidget(self.start_game_button)
        self.layout().removeWidget(self.AI_use)
        self.layout().removeWidget(self.voice_commands)
        self.layout().removeWidget(self.num_rounds)
        self.layout().removeWidget(self.AI_host)
        self.layout().removeWidget(self.AI_family1)
        self.layout().removeWidget(self.AI_family2)
        self.layout().removeWidget(self.fm_check)

        # Delete the widgets
        self.family1_name_input.setVisible(False)
        self.family2_name_input.setVisible(False)
        self.start_game_button.setVisible(False)
        self.AI_use.setVisible(False)
        self.voice_commands.setVisible(False)
        self.num_rounds.setVisible(False)
        self.image_label.setVisible(False)
        self.AI_host.setVisible(False)
        self.AI_family1.setVisible(False)
        self.AI_family2.setVisible(False)
        self.fm_check.setVisible(False)

        self.layout().addWidget(self.mult_label)
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
    
    def start_fm(self):
        self.clear_layout(self.main_layout)
        self.main_layout.deleteLater()

        self.clear_board()
        self.mult_label.clear()
        self.turn_label.clear()
        self.score_label.clear()

        self.fm_layout = QHBoxLayout()

        fmboardA_layout = QVBoxLayout()
        fmboardB_layout = QVBoxLayout()
        for i in range(5):
            A = self.fmboardA[i]
            B = self.fmboardB[i]
            A.setText("###### ###")
            B.setText("###### ###")
            fmboardA_layout.addWidget(A)
            fmboardB_layout.addWidget(B)

        self.fm_layout.addWidget(self.topic_label)
        self.fm_layout.addWidget(self.info_label)
        
        self.fm_layout.addLayout(fmboardA_layout)
        self.fm_layout.addLayout(fmboardB_layout)
        self.layout().addLayout(self.fm_layout)
    
    def end_fm(self):
        for i in range(5):
            A = self.fmboardA[i]
            B = self.fmboardB[i]
            A.setText("")
            B.setText("")
        
        self.clear_layout(self.fm_layout)
        self.fm_layout.deleteLater()
        self.layout().invalidate()
    
    def reinit_widgets(self):
        self.menu_button.setEnabled(False)
        self.menu_button.setVisible(False)
        # Remove widgets related to game setup
        self.layout().addWidget(self.image_label)
        self.layout().addWidget(self.AI_use)
        self.layout().addWidget(self.num_rounds)
        self.layout().addWidget(self.voice_commands)
        self.layout().addWidget(self.family1_name_input)
        self.layout().addWidget(self.AI_family1)
        self.layout().addWidget(self.family2_name_input)
        self.layout().addWidget(self.AI_family2)
        self.layout().addWidget(self.AI_host)
        self.layout().addWidget(self.start_game_button)
        self.layout().addWidget(self.fm_check)

        # Delete the widgets
        self.family1_name_input.setVisible(True)
        self.family2_name_input.setVisible(True)
        self.start_game_button.setVisible(True)
        self.AI_use.setVisible(True)
        self.voice_commands.setVisible(True)
        self.num_rounds.setVisible(True)
        self.image_label.setVisible(True)
        self.AI_host.setVisible(True)
        self.AI_family1.setVisible(True)
        self.AI_family2.setVisible(True)
        self.fm_check.setVisible(True)

        self.layout().removeWidget(self.score_label)
        self.layout().removeWidget(self.topic_label)
        self.layout().removeWidget(self.info_label)
        
        self.layout().removeWidget(self.turn_label)
        self.layout().removeWidget(self.board1)
        self.layout().removeWidget(self.board2)
        self.layout().removeWidget(self.board3)
        self.layout().removeWidget(self.board4)
        self.layout().removeWidget(self.board5)
        self.layout().removeWidget(self.board6)
        self.layout().removeWidget(self.board7)
        self.layout().removeWidget(self.board8)
        self.layout().removeWidget(self.mult_label)

        self.score_label.setVisible(False)
        self.turn_label.setVisible(False)
        self.topic_label.setVisible(False)
        self.info_label.setVisible(False)

        self.clear_board()
        self.mult_label.clear()
    
    def clear_board(self):
        self.board1.clear()
        self.board2.clear()
        self.board3.clear()
        self.board4.clear()
        self.board5.clear()
        self.board6.clear()
        self.board7.clear()
        self.board8.clear()
    
    def clear_layout(self, layout):
        while layout.count():
            item = layout.itemAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater() # or widget.setParent(None)
            layout.removeItem(item)



    def update_game_info(self, family1_name, family2_name, topic, round_num):
        self.topic_label.setText(f"We asked 100 people, {topic}")
        self.turn_label.setText(f"Round: {round_num + 1}")
        self.score_label.setText(f"Current Scores:\n{family1_name}: {self.score[family1_name]}\n{family2_name}: {self.score[family2_name]}")

    def final_scores(self, family1_name, family2_name):
        self.score_label.setText(f"Final Scores:\n{family1_name}: {self.score[family1_name]}\n{family2_name}: {self.score[family2_name]}")
        self.turn_label.setText("Game Over!")
        dialog = ContinueDialog()
        dialog.exec_()  # This will block until the dialog is closed
    
    def AI_toggle(self):
        self.AI = not self.AI

    def host_toggle(self):
        self.host = not self.host

    def voice_toggle(self):
        self.voice = not self.voice
    
    def family1_toggle(self):
        self.family1 = not self.family1
    
    def family2_toggle(self):
        self.family2 = not self.family2
    
    def fm_toggle(self):
        self.play_fast_money = not self.play_fast_money
    
    def send_email(self, to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password):
        server = smtplib.SMTP(smtp_server, smtp_port)
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Use TLS to secure the connection
            server.login(sender_email, sender_password)

            # Prepare the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.sendmail(sender_email, to_email, msg.as_string())

            print("Email sent successfully!")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            server.quit()


def main():
    app = QApplication(sys.argv)
    ex = FamilyFeudApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()