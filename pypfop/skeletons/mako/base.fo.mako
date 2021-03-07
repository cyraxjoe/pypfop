<%!
MASTER_NAME = 'master-page'
%>
<root xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">
  <layout-master-set>
    <%block name="_page_layout" />
  </layout-master-set>
  <declarations>
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	    <rdf:Description rdf:about=""  xmlns:dc="http://purl.org/dc/elements/1.1/">
          <!-- Dublin Core properties go here -->
          <dc:title>${TITLE or ''}</dc:title>
          <dc:creator>${AUTHOR or ''}</dc:creator>
          <dc:description>${SUBJECT or ''}</dc:description>
	    </rdf:Description>
	    <rdf:Description rdf:about=""  xmlns:xmp="http://ns.adobe.com/xap/1.0/">
          <!-- XMP properties go here -->
          <xmp:CreatorTool>${GENERATOR or 'PyPFOP'}</xmp:CreatorTool>
	    </rdf:Description>
      </rdf:RDF>
    </x:xmpmeta>
  </declarations>
  <page-sequence master-reference="${self.attr.MASTER_NAME}">
    <static-content flow-name="xsl-region-after">
      <%block name="region_after"> <block /> </%block>
    </static-content>
% if FONT_SIZE and FONT_FAMILY:
    <flow flow-name="xsl-region-body" font-size="${FONT_SIZE}" font-family="${FONT_FAMILY}">
% elif FONT_SIZE:
    <flow flow-name="xsl-region-body" font-size="${FONT_SIZE}" font-family="Helvetica" >
% elif FONT_FAMILY:
    <flow flow-name="xsl-region-body" font-family="${FONT_FAMILY}">
% else:
    <flow flow-name="xsl-region-body" font-family="Helvetica">
% endif
        ${next.body()}
    </flow>
  </page-sequence>
</root>
