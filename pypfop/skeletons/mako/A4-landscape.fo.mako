<%inherit file="./base.fo.mako" />
<%block name="_page_layout">
    <simple-page-master  master-name="${self.attr.MASTER_NAME}"
                         page-width="210mm"
                         page-height="297mm" >
        <region-body margin="1cm"/>
        <region-after extent="1cm"/>
    </simple-page-master>
</%block>
${next.body()}
