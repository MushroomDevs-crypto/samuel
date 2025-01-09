import tweepy
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da API do Twitter
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Configuração da API do OpenAI (para ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar a API do Twitter
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# Inicializar o modelo de linguagem ChatGPT
llm = ChatOpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo")

def generate_response(text):
    # Definindo a personalidade do bot
    system_template = """
    Você é um bot de Twitter que ajuda com tecnologia, mas com uma personalidade sarcástica e espirituosa.
    - Responda de forma concisa.
    - Use humor, mas mantenha a resposta informativa.
    - Não use emojis, mas seu tom pode ser irônico.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    human_template="{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Formatar a entrada do usuário
    final_prompt = chat_prompt.format_prompt(text=text).to_messages()
    
    # Gerar a resposta
    response = llm(final_prompt).content
    return response

# Função para responder a menções
def respond_to_mentions():
    # Obtem as menções
    mentions = api.mentions_timeline()

    for mention in mentions:
        # Verificar se já respondemos a este tweet
        if not mention.in_reply_to_status_id:
            tweet_text = mention.text
            response = generate_response(tweet_text)
            try:
                api.update_status(
                    status=response,
                    in_reply_to_status_id=mention.id,
                    auto_populate_reply_metadata=True
                )
                print(f"Respondido ao tweet de @{mention.user.screen_name}")
            except tweepy.TweepError as e:
                print(f"Erro ao responder ao tweet: {e}")

if __name__ == "__main__":
    while True:
        respond_to_mentions()
        # Espera um pouco para não sobrecarregar a API e respeitar os limites de taxa
        time.sleep(60)  # Aguarda 1 minuto antes de verificar novamente