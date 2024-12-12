from typing import List, Dict, Tuple
from groq import Groq

def questions_from_file(num_topics:int=1, filepath:str="answers.txt"):
    total_topics = {}
    with open("answers.txt", "r") as file:
        for i in range(num_topics):
            initial_line = file.readline().strip("\n")
            topic = initial_line[:-1]
            num_questions = int(initial_line[-1])
            total_ans = {}
            for line in range(int(num_questions)):
                temp = file.readline().strip("\n").split()
                points = temp.pop()
                answer = "".join(temp)
                total_ans[answer.lower()] = int(points)
            sorted_ans = dict(sorted(total_ans.items(), key=lambda item: item[1]))
            total_topics[topic] = sorted_ans
    return total_topics

def questions_from_AI(num_topics:int, client):
    total_topics = {}
    log=[
            {
                "role": "system",
                "content": "You are an AI who's job is to generate a real family feud question. Must be between 4 and 8 answers with points adding up to a number between 90 and 100. Style like this: topic as 1st line (it has to be a question, it cannot be a statement), each subsequent line is answer space amount of points. Add a newline after each answer. Say NOTHING but these things. This means do not say anything before the topic or inbetween or after anything at all. Do not repeat the same question. Example: Name a fruit\nApple 20\nBanana 20\nStrawberry 20\nOrange 20\nPineapple 20",
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
                "content": "groq generate a real family feud question. Must be between 4 and 8 answers with points adding up to a number between 90 and 100. Style like this: topic as 1st line (it has to be a question, it cannot be a statement), each subsequent line is answer space amount of points. Add a newline after each answer. Say NOTHING but these things. This means do not say anything before the topic or inbetween or after anything at all. Do not repeat the same question. Example: Name a fruit\nApple 20\nBanana 20\nStrawberry 20\nOrange 20\nPineapple 20",
            }
            )
    return total_topics

def questions_from_topic(num_topics:int, client):
    total_topics = {}
    log=[
            {
                "role": "user",
                "content": "groq generate a real sounding family feud question on a given topic. Must be between 4 and 8 answers with points adding up to a number between 90 and 100. Style like this: topic as 1st line (it has to be a question, it cannot be a statement), each subsequent line is answer space amount of points. Add a newline after each answer. Say NOTHING but these things. This means do not say anything before the topic or inbetween or after anything at all. Do not repeat the same question. Example: Name a fruit\nApple 20\nBanana 20\nStrawberry 20\nOrange 20\nPineapple 20",
            }

        ]
    for i in range(num_topics):
        topic = input("Enter a topic for question "+str(i+1)+": ")
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
        print(response)
        question = " ".join(response[0])
        total_ans = {}
        on_topic = True
        for j in response:
            if on_topic:
                on_topic = False
                continue
            points = j.pop()
            total_ans[" ".join(j).lower().strip()] = int(points)
        sorted_ans = dict(sorted(total_ans.items(), key=lambda item: item[1], reverse=True))
        total_topics[question.lower()] = sorted_ans
    return total_topics