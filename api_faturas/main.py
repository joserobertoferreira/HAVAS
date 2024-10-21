from http import HTTPStatus

from auth.auth import Auth
from config import settings


def api_faturas() -> None:
  # Autentica na API e recupera o token
  http_status, authentication, token = Auth.login(
     settings.SERVER_BASE_ADDRESS, 
     settings.API_USER, 
     settings.API_PASSWORD,
    )

  # Verifica se houve sucesso na autenticação
  if http_status == HTTPStatus.OK:
     # Recupera a lista de mensagens
     ...

  

if __name__ == "__main__":
    api_faturas()