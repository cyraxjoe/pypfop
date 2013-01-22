from pypfop import Document
from pypfop.makotemplates import TemplateFactory

tfactory = TemplateFactory()
doc = Document(tfactory('helloworld.fo.mako'))
fpath = doc.generate({"name": "Stranger"})
print("The document has been generated at %s" % fpath)
