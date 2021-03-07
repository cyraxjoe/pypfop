import pypfop
import pypfop.templates.mako


def explicit_generation():
    tfactory = pypfop.templates.mako.Factory()
    doc = pypfop.DocumentGenerator(template=tfactory('helloworld.fo.mako'))
    fpath = doc.generate({"name": "Stranger"})
    return fpath


def decorator_style():
    document = pypfop.make_document_decorator()

    @document(template="helloworld.fo.mako")
    def example():
        return {"name": "Stranger"}

    return example()


def single_func_call():
    return pypfop.generate_document(
        "helloworld.fo.mako", {"name": "Stranger"}
    )


if __name__ == '__main__':

    methods = {
        "explicit": explicit_generation,
        "decorator_style": decorator_style,
        "single_func_call": single_func_call
    }
    for method_name, func in methods.items():
        print("Generating document with method: {}".format(method_name))
        print("The document has been generated at: {}".format(func()))
    print("All the three documents should have the same content")
