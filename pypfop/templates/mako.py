import mako.exceptions
import mako.lookup

import pypfop
import pypfop.templates
import pypfop.exceptions


def get_lookup(lookup_dirs, input_enc='utf-8', output_enc='utf-8'):
    if isinstance(lookup_dirs, str):
        lookup_dirs = (lookup_dirs,)
    return mako.lookup.TemplateLookup(directories=lookup_dirs,
                                      input_encoding=input_enc,
                                      output_encoding=output_enc)


class Template(pypfop.templates.Template):

    def __init__(self, template_path, lookup):
        self.template_path = template_path
        self.lookup = lookup

    def render(self, params):
        template = self.lookup.get_template(self.template_path)
        try:
            return template.render(**params)
        except Exception:
            raise pypfop.exceptions.TemplateError(
                mako.exceptions.text_error_template().render()
            )


class Factory(pypfop.templates.Factory):
    name = 'mako'

    def __init__(self, lookup_dirs=None, use_skels=True):
        lookup_dirs = self._get_lookup_dirs(lookup_dirs, use_skels)
        self.lookup = get_lookup(lookup_dirs)

    def __call__(self, template):
        return Template(template, self.lookup)

    def _get_lookup_dirs(self, lookup_dirs, use_skels):
        if lookup_dirs is None:
            lookup_dirs = ['.', ]
        else:
            if isinstance(lookup_dirs, str):
                lookup_dirs = [lookup_dirs, ]
            else:
                lookup_dirs = list(lookup_dirs)
        if use_skels:
            lookup_dirs.append(self.skel_dir)
        return lookup_dirs
