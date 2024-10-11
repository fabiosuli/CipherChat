from databases.mongohandler import MongoHandler
from databases.entities import Users, Messages


def main():
    mongo_handler = MongoHandler()
    mongo_handler.connect()

    while True:
        print("\n================ Bem-vindo(a) ao CipherChat ================")
        print("Menu:")
        print("1. Cadastrar")
        print("2. Fazer Login")
        print("3. Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            name = input("Digite seu nome: ")
            email = input("Digite seu email: ")
            password = input("Digite sua senha: ")

            if not name or not email or not password:
                print("Erro: Todos os campos (nome, email e senha) devem ser preenchidos.")
                continue

            if '@' not in email:
                print("Erro: O email deve conter '@'.")
                continue

            user = Users(name, email, password)
            mongo_handler.register_user(user)

        elif choice == '2':
            login_email = input("Digite seu email para login: ")
            login_password = input("Digite sua senha para login: ")

            if mongo_handler.authenticate(login_email, login_password):
                user_data = mongo_handler.database["users"].find_one({"email": login_email})
                user = Users(user_data["name"], user_data["email"], user_data["password"])

                print(f"\nLogin bem-sucedido, bem-vindo(a) {user.name} ao CipherChat!")
                while True:
                    print("\nMenu de Mensagens:")
                    print("1. Enviar Mensagem")
                    print("2. Ler Mensagens")
                    print("3. Sair")

                    message_choice = input("Escolha uma opção: ")

                    if message_choice == '1':
                        recipient = input("Digite o email do destinatário: ")

                        if not mongo_handler.user_exists(recipient):
                            print("Erro: O destinatário não está cadastrado.")
                            continue

                        message_text = input("Digite sua mensagem: ")
                        secret_phrase = input("Digite a frase de criptografia: ")

                        message = Messages(sender=login_email, recipient=recipient, message=message_text)
                        mongo_handler.send_message(message, secret_phrase)

                    elif message_choice == '2':
                        print("Listando usuários que enviaram mensagens para você:")
                        senders = mongo_handler.get_message_senders(login_email)

                        if not senders:
                            print("Nenhum remetente encontrado.")
                            continue

                        for sender in senders:
                            print(sender)

                        sender_email = input("Digite o email do remetente: ")
                        secret_phrase = input("Digite a frase de criptografia: ")

                        mongo_handler.read_messages(login_email, sender_email, secret_phrase)

                    elif message_choice == '3':
                        print("Saindo do menu de mensagens...")
                        break

                    else:
                        print("Opção inválida. Tente novamente.")

            else:
                print("Email ou senha incorretos.")

        elif choice == '3':
            print("\nSaindo...")
            print("Obrigado por usar o CipherChat! Até logo!")
            print("\n")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()