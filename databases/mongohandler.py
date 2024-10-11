import os
from pymongo import MongoClient
from dotenv import load_dotenv
from databases.entities import Users, Messages
from databases.cipher import AESCipher

load_dotenv()

class MongoHandler:
    def __init__(self, database_name="pychat"):
        self.connection_string = os.getenv('MONGODB_URI')
        self.database_name = database_name
        self.client = None
        self.database = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.database = self.client[self.database_name]
            print("Conectado ao Banco de Dados.")
        except Exception as e:
            print(f"Falha na conexão com o Banco de Dados: {e}")
            self.client = None

    def register_user(self, user: Users):
        try:
            users_collection = self.database["users"]
            if users_collection.find_one({"email": user.email}):
                print("Usuário já cadastrado.")
                return

            cipher = AESCipher(user.password)
            encrypted_password = cipher.encrypt(user.password)

            users_collection.insert_one({
                "name": user.name,
                "email": user.email,
                "password": encrypted_password
            })
            print("Usuário cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar o usuário: {e}")

    def authenticate(self, email, password) -> bool:
        try:
            users_collection = self.database["users"]
            user = users_collection.find_one({"email": email})
            if not user:
                return False

            cipher = AESCipher(password)
            decrypted_password = cipher.decrypt(user["password"])

            if decrypted_password == password:
                return True
            return False
        except Exception as e:
            print(f"Erro de autenticação: {e}")
            return False

    def user_exists(self, email: str) -> bool:
        users_collection = self.database["users"]
        return users_collection.find_one({"email": email}) is not None

    def send_message(self, message: Messages, secret_phrase: str):
        try:
            cipher = AESCipher(secret_phrase)
            encrypted_message = cipher.encrypt(message.message)

            messages_collection = self.database["messages"]
            messages_collection.insert_one({
                "sender": message.sender,
                "recipient": message.recipient,
                "message": encrypted_message
            })
            print("Mensagem enviada com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def read_messages(self, recipient: str, sender_email: str, secret_phrase: str):
        try:
            messages_collection = self.database["messages"]

            message_count = messages_collection.count_documents({"recipient": recipient, "sender": sender_email})

            if message_count == 0:
                print("Nenhuma mensagem encontrada. Verifique se o email do remetente está certo.")
                return

            print(f"Você tem {message_count} mensagem(s):")

            messages = messages_collection.find(
                {"recipient": recipient, "sender": sender_email}
            ).sort("_id", -1).limit(5)

            for message in messages:
                try:
                    cipher = AESCipher(secret_phrase)
                    decrypted_message = cipher.decrypt(message['message'])
                    print(f"De: {message['sender']}, Mensagem: {decrypted_message}")
                except ValueError:
                    print("A frase de descriptografia está incorreta para está mensagem.")
        except Exception as e:
            print(f"Erro ao ler mensagens: {e}")

    def get_message_senders(self, recipient: str):
        try:
            messages_collection = self.database["messages"]
            senders = messages_collection.distinct("sender", {"recipient": recipient})
            return senders
        except Exception as e:
            print(f"Erro ao obter remetentes: {e}")
            return []