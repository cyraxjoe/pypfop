class PypfopError(Exception):
    """General base error class for pypfop, this is just to be
    able to classify the errors that belongs to PyPFOP.
    """


class DocumentGeneratorError(PypfopError):
    """Exception that is intented to be used to be raised when
    an error occur on the document generation logic.
    """


class BuilderError(PypfopError):
    """Exception that is intented to be used on the case of an
    error on the bilder step, this is in the translation from
    the fo template an actual document.
    """


class TemplateError(PypfopError):
    """Exception that is intented to be used on the case of an
    error at the template level, this is for example a mako
    exception will be seen as a TemplateError.
    """
