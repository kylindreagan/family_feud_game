from typing import List, Dict, Tuple
from groq import Groq
from qwindows import QuestionDialog

PROMPT_TEMPLATE = (
    "You are an AI tasked with generating family feud-style questions. "
    "Each question must have 4 to 8 answers, with points summing between 90 and 100. "
    "Output should strictly follow this format: "
    "Topic as the first line (a question), followed by answers with points. "
    "Example:\n"
    "Name a fruit\nApple 20\nBanana 20\nStrawberry 20\nOrange 20\n"
)

def questions_from_file(num_topics:int=1, filepath:str="games/testanswers.txt"):
    total_topics = {}
    with open(filepath, "r") as file:
        for i in range(num_topics):
            topic_line = file.readline().strip("\n")
            if not topic_line or len(topic_line) < 2 or not topic_line[-1].isdigit():
                raise ValueError("Malformed topic line.")
            topic = topic_line[:-1]
            num_questions = int(topic_line[-1])
            total_ans = {}
            for line in range(int(num_questions)):
                temp = file.readline().strip("\n").rsplit(" ", 1)
                if len(temp) != 2 or not temp[1].isdigit():
                    raise ValueError("Malformed answer line.")
                answer, points = temp
                total_ans[answer.lower()] = int(points)
            sorted_ans = dict(sorted(total_ans.items(), key=lambda item: item[1]))
            total_topics[topic] = sorted_ans
    return total_topics

def questions_from_AI(num_topics:int, client):
    total_topics = {}
    log=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE,
            }

        ]
    for i in range(num_topics):
        chat_completion = client.chat.completions.create(
        messages=log,
        model="llama3-8b-8192",
        stream=False,
        )
        log.append({
        "role": "assistant",
        "content": chat_completion.choices[0].message.content
        })
        response = [x.split() for x in chat_completion.choices[0].message.content.split("\n") if x != '']
        topic = " ".join(response[0])
        total_ans = {}
        on_topic = True
        for j in response:
            if on_topic:
                on_topic = False
                continue
            points = j.pop()
            total_ans[" ".join(j).lower().strip()] = int(points)
        sorted_ans = dict(sorted(total_ans.items(), key=lambda item: item[1], reverse=True))
        print(sorted_ans)
        total_topics[topic.lower()] = sorted_ans
        log.append(
            {
                "role": "user",
                "content": PROMPT_TEMPLATE
            }
            )
    return total_topics

def questions_from_topic(num_topics:int, client, game=False):
    total_topics = {}
    log=[
            {
                "role": "system",
                "content": "You are an AI who's job is to generate a real family feud question on a given topic" + PROMPT_TEMPLATE,
            }
        ]
    for i in range(num_topics):
        if not game:
            topic = input("Enter a topic for question "+str(i+1)+": ")
        else:
            dialog = QuestionDialog()
            dialog.exec_()  # This will block until the dialog is closed
            topic = dialog.get_data()
        
        log.append({
                "role": "user",
                "content": "Generate a question on topic "+topic,
            })
        
        chat_completion = client.chat.completions.create(
        messages=log,
        model="llama3-8b-8192",
        stream=False,
        )
        log.append({
        "role": "assistant",
        "content": chat_completion.choices[0].message.content
        })
        response = [x.split() for x in chat_completion.choices[0].message.content.split("\n") if x != '']
        question = " ".join(response[0])
        total_ans = {}
        on_topic = True
        try:
            for j in response:
                if on_topic:
                    on_topic = False
                    continue
                points = j.pop()
                total_ans[" ".join(j).lower().strip()] = int(points)
            sorted_ans = dict(sorted(total_ans.items(), key=lambda item: item[1], reverse=True))
            total_topics[question.lower()] = sorted_ans
        except ValueError:
            question = "Error in question generation."
            total_topics[question.lower()] = {}
    return total_topics