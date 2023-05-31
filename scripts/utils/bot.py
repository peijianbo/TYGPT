import os
from urllib.parse import urljoin

import requests
import json
import gradio as gr

from scripts.utils.constants import *


def process_eventstream_data(data: str) -> str:
    try:
        # 解析数据并获取key-value
        value = data.split(": ", 1)[1].strip()
        content_dict = json.loads(value)
        # 判断是否为开始数据
        if content_dict.get("rid", None) is not None:
            return ""
        # 判断是否为内容或结束数据
        if content_dict.get("finish_reason", None) is None:
            return content_dict.get("chunk")
        else:
            return ""
    except Exception as e:
        return ""


def send_question(conversation_id, question_content, gpt_token):
    url = urljoin(GPT_DOMAIN, GPT_SEND_QUESTION_PATH)
    data = {
        "conversation": conversation_id,
        "content": question_content
    }
    HEADERS = {
        'Authorization': f'Token {gpt_token}',
        'Accept': 'application/json, text/plain, */*'
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print(response)

    if response.status_code == 201:
        return response.json()
    else:
        raise gr.Error(f"Send question Error{response.text}")


def get_bot_answer(question_id, gpt_token):
    url = urljoin(GPT_DOMAIN, GPT_GET_ANSWER_PATH) + str(question_id)
    headers = {
        'Authorization': f'Token {gpt_token}',
        'Accept': 'text/event-stream'
    }
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                yield process_eventstream_data(line.decode('utf-8'))
    else:
        raise gr.Error(f"GET bot answer Error{response.text}")


def list_conversation(gpt_token):
    url = urljoin(GPT_DOMAIN, GPT_CONVERSATION_LIST_PATH)
    headers = {
        'Authorization': f'Token {gpt_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['results']
    else:
        raise gr.Error(f"GET conversation list Error!{response.text}")


def bot(msg, history, gpt_token, conversation):
    if conversation:
        conversation_id = conversation.split('(')[-1][:-1]
    else:
        conversation_id = None
    # POST请求发送问题
    post_response = send_question(conversation_id, msg, gpt_token)
    question_id = post_response["id"]
    # 使用问题ID发送GET请求，获取机器人的回答
    answer = ""
    for character in get_bot_answer(question_id, gpt_token):
        answer += character
    history.append((msg, answer))
    return '', history


if __name__ == '__main__':

    with gr.Blocks() as gpt:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        msg.submit(bot, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)

        gpt.launch()
