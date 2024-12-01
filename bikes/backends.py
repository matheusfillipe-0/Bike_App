from django.contrib.auth.backends import BaseBackend
from .models import Usuario
import logging

logger = logging.getLogger(__name__)

class UsuarioBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            logger.warning(f"Usuário não encontrado: {username}")
            return None

        logger.info(f"Verificando usuário: {username}")

        if usuario.check_password(password):
            logger.info("Senha correta!")

             
            if usuario.is_active:
                return usuario
            else:
                logger.warning(f"Usuário {username} está inativo.")
                return None
        else:
            logger.warning("Senha incorreta!")
        
        return None
