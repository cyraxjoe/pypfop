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
