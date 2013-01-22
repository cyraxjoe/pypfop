<root>
  <layout-master-set>
    <simple-page-master  master-name="letter"
       page-width="8.5in" page-height="11in"
			 >
      <region-body margin="0.5in"/>
      <region-after  extent="4.8cm"/>
    </simple-page-master>
  </layout-master-set>

  <declarations>
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	<rdf:Description rdf:about=""  xmlns:dc="http://purl.org/dc/elements/1.1/">
          <!-- Dublin Core properties go here -->
          <dc:title>${title or ''}</dc:title>
          <dc:creator>${author or ''}</dc:creator>
          <dc:description>${subject or ''}</dc:description>
	</rdf:Description>
	<rdf:Description rdf:about=""  xmlns:xmp="http://ns.adobe.com/xap/1.0/">
          <!-- XMP properties go here -->
          <xmp:CreatorTool>${GENERATOR or 'PyPFOP'}</xmp:CreatorTool>
	</rdf:Description>
      </rdf:RDF>
    </x:xmpmeta>
  </declarations>

  <page-sequence master-reference="letter">

    <static-content flow-name="xsl-region-after">
      <%block name="rfooter">
         <block />
      </%block>
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



