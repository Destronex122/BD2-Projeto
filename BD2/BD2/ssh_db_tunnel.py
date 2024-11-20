# ssh_db_tunnel.py

from sshtunnel import SSHTunnelForwarder

def create_ssh_tunnel():
    return SSHTunnelForwarder(
        ('193.137.7.56', 22),  # Endereço do servidor SSH e porta
        ssh_username='aluno6',  # Nome de usuário SSH
        ssh_password='di!912877',  # Senha do SSH
        remote_bind_address=('127.0.0.1', 5432),  # Endereço e porta do PostgreSQL no servidor remoto
        local_bind_address=('localhost',)  # Deixe o Python escolher uma porta livre
    )
