<%inherit file="./base.fo.mako" />
<%!
   MASTER_NAME = 'letter-portrait'
%>

<%block name="_page_layout">
    <simple-page-master master-name="${self.attr.MASTER_NAME}"
                        fox:scale="1" fox:crop-offset="5mm"
                        fox:crop-box="media-box" fox:bleed="5mm"
                        page-width="8.5in" page-height="11in">

        ## main region
        <region-body margin="${REGION_BODY_MARGIN or '5mm 3.5mm'}"/>

        ## top region
        <region-before extent="${REGION_BEFORE_EXTEND or '0mm'}"/>

        ## bottom region
        <region-after extent="${REGION_AFTER_EXTEND or '0mm'}"/>

        ## left region
        <region-start extent="${REGION_START_EXTEND or '0mm'}"/>

        ## right region
        <region-end extent="${REGION_END_EXTEND or '0mm'}"/>

    </simple-page-master>
</%block>
${next.body()}
