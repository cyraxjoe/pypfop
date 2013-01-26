import sys

from pypfop import Document
from pypfop.makotemplates import TemplateFactory


lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Bonum appello quicquid secundurn naturam est, quod contra malum, nec ego solus, sed tu etiam, Chrysippe, in foro, domi; Nam libero tempore, cum soluta nobis est eligendi optio, cumque nihil impedit, quo minus id, quod maxime placeat, facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Qualis est igitur omnis haec, quam dico, conspiratio consensusque virtutum, tale est illud ipsum honestum, quandoquidem honestum aut ipsa virtus est aut res gesta virtute; Ut enim, inquit, gubernator aeque peccat, si palearum navem evertit et si auri, item aeque peccat, qui parentem et qui servum iniuria verberat. Non elogia monimentorum id significant, velut hoc ad portam: Hunc unum plurimae consentiunt gentes populi primarium fuisse virum. Duo Reges: constructio interrete. Cumque ipsa virtus efficiat ita beatam vitam, ut beatior esse non possit, tamen quaedam deesse sapientibus tum, cum sint beatissimi; Nos beatam vitam non depulsione mali, sed adeptione boni iudicemus, nec eam cessando, sive gaudentem, ut Aristippus, sive non dolentem, ut hic, sed agendo aliquid considerandove quaeramus. Unum est sine dolore esse, alterum cum voluptate. Gracchum patrem non beatiorem fuisse quam fillum, cum alter stabilire rem publicam studuerit, alter evertere. Censemus autem facillime te id explanare posse, quod et Staseam Neapolitanum multos annos habueris apud te et complures iam menses Athenis haec ipsa te ex Antiocho videamus exquirere."""


def get_lorem_rows(cols=4, words=3):
    hugelorem = lorem * 10
    def get_cells():
        elem = []
        for i, word in enumerate(hugelorem.split(), 1):
            elem.append(word)
            if not i % words:
                yield ' '.join(elem)
                elem = []
    def get_rows():
        cells = []
        for i, cell in enumerate(get_cells(), 1):
            cells.append(cell)
            if not i % cols:
                yield cells
                cells = []
    return get_rows()


SAMPLE_DATA = {
    'header': ['Garbage one', 'Garbarge two', 'Garbage three', 'Gargabe four'],
    'rows': list(get_lorem_rows()),
    }


def pdf_table(params):
    tfactory = TemplateFactory()
    doc = Document(tfactory('simple-table.fo.mako'), 'simple_table.css',
                   styledir='css')
    return doc.generate(params)



if __name__ == '__main__':
    sys.stderr.write('The document has been generated at ')
    sys.stderr.flush()
    print(pdf_table(SAMPLE_DATA))
    
