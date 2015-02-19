class PypfopError(Exception):
    """
    General base error class for pypfrop.
    """
class DocumentGeneratorError(PypfopError):
    pass

class BuilderError(PypfopError):
    pass

class TemplateError(PypfopError):
    pass
