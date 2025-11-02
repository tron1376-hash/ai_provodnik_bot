import os
from dotenv import load_dotenv
load_dotenv()
from gigachat import GigaChat
api_key = os.getenv("GIGACHAT_API_KEY")
client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
scope = os.getenv("GIGACHAT_SCOPE","GIGACHAT_API_PERS")
verify = os.getenv("GIGACHAT_VERIFY_SSL","false").lower()=="true"
creds = api_key if api_key else f"{client_id}:{client_secret}"
with GigaChat(credentials=creds, scope=scope, verify_ssl_certs=verify) as giga:
    resp = giga.chat.completions.create(
        model="GigaChat",
        messages=[{"role":"system","content":"Отвечай одним словом: ПРИВЕТ."},{"role":"user","content":"Скажи 'привет'."}],
        temperature=0.1
    )
print("OK:", resp.choices[0].message.content)
