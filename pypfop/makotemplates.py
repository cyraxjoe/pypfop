import mako.exceptions
from mako.lookup import TemplateLookup

import pypfop


def get_lookup(lookup_dirs, input_enc='utf-8', output_enc='utf-8'):
    if isinstance(lookup_dirs, str):
        lookup_dirs = (lookup_dirs,)
    return TemplateLookup(directories=lookup_dirs,
                          input_encoding=input_enc,
                          output_encoding=output_enc)

class Template(object):

    def __init__(self, template_path, lookup):
        self.template_path = template_path
        self.lookup = lookup


    def render(self,  params):
        template = self.lookup.get_template(self.template_path)
        try:
            return template.render(**params)
        except Exception:
            raise Exception(mako.exceptions.text_error_template().render())


class TemplateFactory(object):

    def __init__(self, lookup_dirs=pypfop.skeldir_for('mako')):
        self.lookup = get_lookup(lookup_dirs)

    def __call__(self, template):
        return Template(template, self.lookup)
