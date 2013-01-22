import pypfop
from pypfop import makotemplates
import pypfop.makotemplates

tfactory = makotemplates.TemplateFactory(('.', '../pypfop/skeletons/mako/'))
doc = pypfop.Document(tfactory('helloworld.fo.mako'),
                      fop_cmd='/usr/bin/fop', debug=True)
doc.generate({})
