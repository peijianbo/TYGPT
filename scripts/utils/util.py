import json
import os
from urllib.parse import urljoin

import requests
import gradio as gr
from scripts.utils.constants import *


def get_account_token(username, password):
    url = urljoin(ACCOUNT_DOMAIN, ACCOUNT_LOGIN_PATH)
    data = {
        "username": username,
        "password": password,
        "app_key": GPT_APP_KEY,
        "cate": 1,
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise gr.Error(f"Login Error!{response.text}")
    data = response.json()
    auth_token = data.get("token")
    uid = data.get("id")
    return auth_token, uid


def get_gpt_token(token, account_id):
    url = urljoin(GPT_DOMAIN, GPT_LOGIN_PATH)
    data = {
        'auth_token': token,
        'account_id': account_id
    }
    response = requests.post(url, data)
    if response.status_code != 200:
        raise gr.Error(f"Login TYGPT Error!{response.text}")
    gpt_token = response.json()['token']
    # update_local_gpt_token(account_id, gpt_token)
    return gpt_token


def update_local_gpt_token(account_id, gpt_token):
    data = {account_id: gpt_token}
    try:
        with open(GPT_TOKEN_FILE_PATH, "r") as file:
            token_data = json.load(file)
    except FileNotFoundError:
        with open(GPT_TOKEN_FILE_PATH, "w") as file:
            json.dump(data, file)
    else:
        token_data[account_id] = gpt_token
        with open(GPT_TOKEN_FILE_PATH, "w") as file:
            json.dump(token_data, file)


def get_local_gpt_token():
    try:
        with open(GPT_TOKEN_FILE_PATH, "r") as file:
            token_data = json.load(file)
            return list(token_data.values())[0]
    except FileNotFoundError:
        return ''


def token_is_valid(token):
    url = urljoin(GPT_DOMAIN, GPT_CONVERSATION_LIST_PATH)
    headers = {
        'Authorization': f'Token {token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)

    return True if response.status_code == 200 else False
