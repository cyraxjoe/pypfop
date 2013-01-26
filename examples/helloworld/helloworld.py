import sys

from pypfop import Document
from pypfop.makotemplates import TemplateFactory

tfactory = TemplateFactory()
doc = Document(tfactory('helloworld.fo.mako'))
fpath = doc.generate({"name": "Stranger"})
sys.stderr.write('The document has been generated at ')
sys.stderr.flush()
print("%s" % fpath)
