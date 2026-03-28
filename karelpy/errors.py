class KarelError(Exception):
    pass


class LexerError(KarelError):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Línea {line}, columna {col}: {message}")
        self.line = line
        self.col = col


class ParseError(KarelError):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Línea {line}, columna {col}: {message}")
        self.line = line
        self.col = col


class KarelRuntimeError(KarelError):
    def __init__(self, message: str, line: int = 0):
        super().__init__(message)
        self.line = line


class MaxStepsError(KarelRuntimeError):
    pass


class KarelShutdown(Exception):
    """Señal de terminación normal cuando Karel ejecuta apagate()."""
    pass


class KarelReturn(Exception):
    """Señal de retorno anticipado cuando Karel ejecuta termina()."""
    pass
