import modules.scripts as scripts
import gradio as gr
import os
from modules.processing import process_images, Processed
import modules.scripts as scripts
from modules import script_callbacks

from scripts.utils.bot import bot, list_conversation
from scripts.utils.util import get_account_token, get_gpt_token, get_local_gpt_token, token_is_valid


class GPTScript(scripts.Script):
    def title(self):
        return 'TYGPT'

    def show(self, is_img2img):
        return not is_img2img

    def ui(self, is_img2img):
        with gr.Blocks() as demo:
            local_gpt_token = get_local_gpt_token()
            account_token = gr.Textbox(type="text", label='token', visible=False)
            account_id = gr.Textbox(type="text", label='id', visible=False)
            gpt_token = gr.Textbox(type="text", value=local_gpt_token, label='GPT token', visible=False)

            if not token_is_valid(local_gpt_token):
                with gr.Row(visible=True) as login_row:
                    with gr.Column() as login_col:
                        username = gr.Textbox(type="text", label='用户名')
                        password = gr.Textbox(type="password", label='密码')
                        login_btn = gr.Button("确认")

                with gr.Column(visible=False) as chatbot_row:
                    # with gr.Column(scale=1) as conversation_col:
                    conversation = gr.Dropdown(choices=[], label="Conversation")
                    # with gr.Column(scale=4) as chatbot_col:
                    chatbot = gr.Chatbot(visible=True)
                    question = gr.Textbox(visible=True, lines=2, placeholder='Shift+↵发送，↵换行', label='')
                    dialog = gr.Button("Clear", visible=True)
                    question.submit(bot, [question, chatbot, gpt_token, conversation], [question, chatbot])
                    dialog.click(lambda: None, None, chatbot, queue=False)

                def show_gpt(username, password):
                    auth_token, uid = get_account_token(username, password)
                    gpt_token_value = get_gpt_token(auth_token, uid)

                    conversations = list_conversation(gpt_token_value)
                    choices = [f"{c['topic']}({c['id']})" for c in conversations]
                    default_value = choices[0] if choices else None
                    return gr.Row.update(visible=False), \
                           gr.Row.update(visible=True), \
                           gr.Textbox.update(value=gpt_token_value), \
                           gr.Dropdown.update(choices=choices, value=default_value)

                login_btn.click(show_gpt, inputs=[username, password],
                                outputs=[login_row, chatbot_row, gpt_token, conversation])
                # login_btn \
                #     .click(get_account_token, [username, password], [account_token, account_id]) \
                #     .success(get_gpt_token, [account_token, account_id], gpt_token) \
                #     .success(fn=show_gpt, outputs=[login_row, chatbot_row, conversation])
            else:
                conversations = list_conversation(local_gpt_token)
                choices = [f"{c['topic']}({c['id']})" for c in conversations]
                default_value = choices[0] if choices else None
                with gr.Column(visible=True) as chatbot_row:
                    # with gr.Column(scale=1) as conversation_col:
                    conversation = gr.Dropdown(choices=choices, value=default_value, label="Conversation")
                    # with gr.Column(scale=4) as chatbot_col:
                    chatbot = gr.Chatbot(visible=True)
                    question = gr.Textbox(visible=True, lines=2, placeholder='Shift+↵发送，↵换行', label='')
                    clear = gr.Button("Clear", visible=True)
                    question.submit(bot, [question, chatbot, gpt_token, conversation],
                                    [question, chatbot, conversation])
                    clear.click(lambda: None, None, chatbot, queue=False)
    def run(self, p):
        proc = process_images(p)
        return proc
