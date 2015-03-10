<%inherit file="./base.fo.mako" />
<%block name="_page_layout">
    <simple-page-master master-name="${self.attr.MASTER_NAME}"
                        page-width="8.5in" page-height="11in">
        <region-body margin="0.5in"/>
        <region-after  extent="1.5in"/>
    </simple-page-master>
</%block>
${next.body()}
