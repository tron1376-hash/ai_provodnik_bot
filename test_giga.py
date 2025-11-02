import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GIGACHAT_API_KEY")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

print("API_KEY:", (api_key or "")[:20], "...")
print("SCOPE:", scope)

if not api_key or len(api_key) < 20:
    print("❌ GIGACHAT_API_KEY не задан или слишком короткий")
    exit(1)

try:
    from gigachat import GigaChat
    from gigachat.models import Chat, Messages, MessagesRole
    
    print("Подключаемся к GigaChat...")
    
    with GigaChat(credentials=api_key, scope=scope, verify_ssl_certs=False) as giga:
        # Синтаксис для старой версии библиотеки
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.USER, content="Привет")
            ],
            temperature=0.7
        )
        response = giga.chat(payload)
        
        print("✅ GigaChat работает!")
        print("Ответ:", response.choices[0].message.content)
        
except Exception as e:
    print("❌ Ошибка:", type(e).__name__)
    print("Детали:", str(e))
    import traceback
    traceback.print_exc()
