<%inherit file="./base.fo.mako" />
<%block name="_page_layout">
    <simple-page-master master-name="${self.attr.MASTER_NAME}"
                        page-width="8.5in" page-height="11in">
        <region-body margin="${REGION_BODY_MARGIN or '1cm'}"/>
        <region-after extent="${REGION_AFTER_EXTEND or '1cm'}"/>
    </simple-page-master>
</%block>
${next.body()}
