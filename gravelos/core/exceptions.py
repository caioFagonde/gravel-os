class GravelOSException(Exception):
    """Base architectural fault."""
    pass

class TerminalAcousticFailureError(GravelOSException):
    """Fired when clock speeds exceed dolomite material thresholds."""
    pass

class StackOverflowError(GravelOSException):
    """Fired when rocks tumble over their own runtime footprint."""
    def __init__(self, sp: int, pc: int):
        super().__init__(f"STACK OVERFLOW AT SP=0x{sp:02X} — AVALANCHE IMMINENT")

class StackUnderflowError(GravelOSException):
    def __init__(self, sp: int, pc: int):
        super().__init__(f"STACK UNDERFLOW AT SP=0x{sp:02X} — THE CEILING FELL")

class LithicAssemblerError(GravelOSException):
    def __init__(self, line: int, instruction: str, reason: str):
        super().__init__(f"ASSEMBLY ERROR L{line}: '{instruction}' -> {reason}")

class ParseException(GravelOSException):
    def __init__(self, message: str, line: int):
        super().__init__(f"RUNE SYNTAX ERROR L{line}: {message}")

class RegisterExhaustionError(GravelOSException):
    def __init__(self, message="OUT OF ROCKS! AST exceeds hardware limits."):
        super().__init__(message)