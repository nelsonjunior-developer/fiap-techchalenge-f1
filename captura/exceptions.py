# captura/exceptions.py

class InvalidDataError(Exception):
    """
    Exceção lançada quando algum dado capturado não puder
    ser convertido ou for considerado inválido.
    """
    pass


class ScrapeError(Exception):
    """Erro genérico para falhas durante a raspagem dos dados."""
    pass