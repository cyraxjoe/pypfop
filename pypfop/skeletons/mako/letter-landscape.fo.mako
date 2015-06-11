<%inherit file="./base.fo.mako" />
<%!
   MASTER_NAME = 'letter-landscape'
%>

<%block name="_page_layout">
    <simple-page-master  master-name="${self.attr.MASTER_NAME}"
                         page-height="8.5in" page-width="11in">
        <region-body margin="${REGION_BODY_MARGIN or '1cm'}"/>
        <region-after extent="${REGION_AFTER_EXTEND or '1cm'}"/>
    </simple-page-master>
</%block>
${next.body()}
