.. -*- rst -*-

Python Preprocessor of the Formatting Objects Processor [pypfop]
================================================================

Document preprocessor for `Apache FOP`_.

How does it works?
------------------

It does what the huge title is implying, preprocess a *higher* level template
to generate *dynamically* an specific `XSL-FO`_ document, which then gets
fed to `Apache FOP`_ and generate the expected output. So that means that
this packages *requires Java*  ``>_<'``, but fear not! It is almost transparent
to the python application.

In general the internal workflow is::

    template ->  mako -> apply css ->  xsl-fo ->  fop -> *Document*


Installation
------------

1. Install pypfop::

    pip install pypfop

2. Install `Apache FOP`_:

   #. Download the binary package of fop1.1 either the  zip_ or tar_ package.
   #. Decompress anywhere you like and set the environment variable ``FOP_CMD``
      to the executable file ``fop`` on the decompressed folder. [1]_

Usage
-----

The Markup
^^^^^^^^^^

The markup used to generate the documents is almost the same as the xsl-fo,
the only difference is that is not necessary to set the xml namespace to all
the elements, for example::

   <fo:table>
    <fo:table-header>
       <fo:table-row>
          <fo:table-cell>
            <fo:block>Project</fo:block>
          </fo:table-cell>
       </fo:table-row>
    </fo:table-header>
    <fo:table-body>
       <fo:table-row>
         <fo:table-cell>
            <fo:block>pypfop</fo:block>
        </fo:table-cell>
       </fo:table-row>
    </fo:table-body>
   </fo:table>

can be written like this::

   <table>
    <table-header>
       <table-row>
          <table-cell>
            <block>Project</block>
          </table-cell>
       </table-row>
    </table-header>
    <table-body>
       <table-row>
         <table-cell>
            <block>pypfopp</block>
        </table-cell>
       </table-row>
    </table-body>
   </table>


The higher level template language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At the time the only supported template language is mako_ it should not be very
complicated to extend to your favorite template language based in the
implementation of mako (which is pretty straight forward) and hopefully
contribute back to the project :).

For example, the previous table can be generated with this mako template
assuming the `header` and `rows` variables are passed to the
`DocumentGenerator.generate` method::

    <table>
      <table-header>
        <table-row>
          % for name in header:
          <table-cell>
            <block>${name}</block>
          </table-cell>
          % endfor
        </table-row>
      </table-header>
      <table-body>
        % for row in rows:
           <table-row>
         % for cell in row:
            <table-cell>
              <block>${cell}</block>
            </table-cell>
         % endfor
           </table-row>
        % endfor
      </table-body>
    </table>


Skeletons
^^^^^^^^^

The previous examples are just fragments of a document. To be able to fully
generate a document with metadata, paper size, margins, etc and to avoid the
repetitive work to write this kind of *base document* pypfop have the notion of
*skeleton documents*, the purpose if this documents are to be inherited at each
template, at the time the implemented skeleton are:

 - ``pypfop/skeletons/mako/A4-landscape.fo.mako``
 - ``pypfop/skeletons/mako/A4-portrait.fo.mako``
 - ``pypfop/skeletons/mako/letter-landscape.fo.mako``
 - ``pypfop/skeletons/mako/letter-portrait.fo.mako``


those include place-holders for:

Metadata:

 - title
 - author
 - subject
 - GENERATOR (by default "PyPFOP")

There is also a  mako block called ``rfooter`` and the body of your template will
be the body of the document.

You don't have to define anything else than the body of your own document but you
still have the option to override any of the metadata and your own footer region.

To be a fully functional template for pypfop the previous table need to be like this.


*simple-table.fo.mako*::

    <%inherit file="simple-letter-base.fo.mako" />
    <table id="main-table">
      <table-header>
        <table-row>
          % for name in header:
          <table-cell>
            <block>${name}</block>
          </table-cell>
          % endfor
        </table-row>
      </table-header>
      <table-body>
        % for row in rows:
           <table-row>
         % for cell in row:
            <table-cell>
              <block>${cell}</block>
            </table-cell>
         % endfor
           </table-row>
        % endfor
      </table-body>
    </table>

*The skeletons directory is set in the template directory path by default.*


Format and style with CSS
^^^^^^^^^^^^^^^^^^^^^^^^^

Beside the *higher level language* that define the content and layout of
the document, the style and formatting uses *CSS*, to be more specific it
can parse the rules that cssutils_ support, which are a very good subset
of CSS2 and CSS3, for example it support things like ``:nth-child(X)``
and ``@import url(XX)``.

The properties that can be set are the same as in the specification of xsl-fo,
check out the section of `About XSL-FO syntax`_, with the only exception
that you can use classes as selectors, xsl-fo does not support the
``class`` attribute, the pypfop parser is going to look for the
``class`` attribute then substitute with the specific style and then remove
the ``class`` attribute.

For example I could define the style for the previous table in three files.

*simple_table.css*::

    @import url("general.css");
    @import url("colors.css");

    #main-table > table-header > table-row{
        text-align: center;
        font-weight: bold;
    }

    #main-table > table-header table-cell{
        padding: 2mm 0 0mm;
    }


*general.css*::

    flow[flow-name="xsl-region-body"] {
        font-size: 10pt;
        font-family: Helvetica;
    }

*colors.css*::

    #main-table> table-body > table-row > table-cell:first-child{
        color: red;
    }
    #main-table> table-body > table-row > table-cell:nth-child(2){
        color: blue;
    }
    #main-table> table-body > table-row > table-cell:nth-child(3){
        color: cyan;
    }
    #main-table> table-body > table-row > table-cell:last-child{
        color: green;
    }


Generate the document
^^^^^^^^^^^^^^^^^^^^^

There are a few different ways to implement the ``Document`` class,
but for the sake of simplicity this is a way to generate the document::


  import pypfop
  import pypfop.templates.mako

  tfactory = pypfop.templates.mako.Factory()
  params = {
    'header': ['Project', 'Website', 'Language', 'Notes'],
    'rows': [
      ('pypfop', 'https://github.com/cyraxjoe/pypfop', 'Python', 'Abstraction on top of Apache FOP'),
      ('Apache FOP', 'https://xmlgraphics.apache.org/fop/', 'Java', '')
    ]
  }
  doc = pypfop.DocumentGenerator(tfactory('simple-table.fo.mako'),
                                 'simple_table.css')
  print(doc.generate(params)) # returns the path of the generated file.


Supported Document formats
^^^^^^^^^^^^^^^^^^^^^^^^^^

In the previous example we didn't define the output of the ``Document`` in
that case the default output of ``pdf`` is used, but the supported outputs
are the almost the same as in `Apache FOP output formats`_.

 - pdf
 - rtf
 - tiff
 - png
 - pcl
 - ps
 - txt


The output format can be set in ``DocumentGenerator.__init__`` or
``DocumentGenerator.generate`` ::

    doc = pypfop.DocumentGenerator(tfactory('simple-table.fo.mako'),
                                   'simple_table.css',
                                   oformat='rtf')

or ::

   doc.generate(params, oformat='rtf')


About XSL-FO syntax
^^^^^^^^^^^^^^^^^^^

As you may have already noticed, it is required to know how to format xsl-fo
documents which in most part are very similar to the HTML counterparts
(except that anything needs to be in ``block`` tags), two of the best reference
that I could find online is in the `XML Bible`_ and the `Data 2 Type tutorial`_.

How about a CSS pre-processor and base generic styles?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I'm looking to add support for less_ or something similar and try to generalize
the styling of fonts, colors, tables, etc. Very much in the *boostrap* sense
of the things. If you are interested in something similar we can join forces
and build something nice.

Why!
----

The project used to be part of a larger project of one of my clients,
on which I decide early on that I will *only use python 3*, terrible decision
if you want to generate pdf files easily or at least at the moment when the
`Report Lab PDF Toolkit`_ was not yet available for Python 3 and I was looking
to have some kind of *template* to the very rigid format of the average invoice
and billing order, so pypfop came to relieve that pain.

.. [1] Actually you can set the command at another level, check the ``DocumentGenerator`` class.

.. _`Apache FOP`: https://xmlgraphics.apache.org/fop/
.. _XSL-FO: https://en.wikipedia.org/wiki/XSL_Formatting_Objects
.. _zip: http://apache.webxcreen.org/xmlgraphics/fop/binaries/fop-1.1-bin.zip
.. _tar: http://apache.webxcreen.org/xmlgraphics/fop/binaries/fop-1.1-bin.tar.gz
.. _`XML Bible`:  http://www.ibiblio.org/xml/books/bible3/chapters/ch16.html
.. _mako: http://www.makotemplates.org/
.. _cssutils: http://pypi.python.org/pypi/cssutils
.. _`Apache FOP output formats`: https://xmlgraphics.apache.org/fop/1.1/output.html
.. _`Data 2 Type tutorial`: http://www.data2type.de/en/xml-xslt-xslfo/xsl-fo/
.. _`Report Lab PDF Toolkit`: https://pypi.python.org/pypi/reportlab
.. _less: http://lesscss.org/
