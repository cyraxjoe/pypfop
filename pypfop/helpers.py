import functools

import pypfop.templates.mako
from .document_generator import DocumentGenerator


class DocumentDecorator:

    def __init__(self, template_factory, *doc_gen_args, **doc_gen_kwargs):
        self.template_factory = template_factory
        self.default_doc_gen_args = doc_gen_args
        self.default_doc_gen_kwargs = doc_gen_kwargs

    def __call__(self, func):
        self.func = func
        return self.wrapper

    def prepare(self, template, *args, **kwargs):
        template_inst = self.template_factory(template)
        args = self.default_doc_gen_args + args
        # we might need deepcopy here
        merged_kwargs = dict(**self.default_doc_gen_kwargs)
        merged_kwargs.update(kwargs)
        self.generator = DocumentGenerator(
            template_inst, *args, **merged_kwargs
        )
        return self

    def wrapper(self, *args, **kwargs):
        params = self.func(*args, **kwargs)
        return self.generator.generate(params)


@functools.lru_cache
def get_mako_template_factory(lookup_dirs=None, use_skels=True):
    return pypfop.templates.mako.Factory(lookup_dirs, use_skels)


@functools.lru_cache
def get_document_generator(template_path, *args, **kwargs):
    template_factory = get_mako_template_factory(
        kwargs.pop('lookup_dirs', None),
        kwargs.pop('use_skels', True)
    )
    template = template_factory(template_path)
    return DocumentGenerator(template, *args, **kwargs)


@functools.lru_cache
def make_document_decorator(
    lookup_dirs=None,
    use_skels=True,
    *doc_gen_args,
    **doc_gen_kwargs
):
    template_factory = get_mako_template_factory(lookup_dirs, use_skels)
    dd = DocumentDecorator(template_factory, *doc_gen_args, **doc_gen_kwargs)
    return dd.prepare


def generate_document(template_path, template_params, *args, **kwargs):
    doc_gen = get_document_generator(template_path, *args, **kwargs)
    return doc_gen.generate(template_params)
