import sys

import pypfop
import pypfop.templates.mako

tfactory = pypfop.templates.mako.Factory()
doc = pypfop.DocumentGenerator(tfactory('helloworld.fo.mako'))
fpath = doc.generate({"name": "Stranger"})
sys.stderr.write('The document has been generated at ')
sys.stderr.flush()
print(fpath)
