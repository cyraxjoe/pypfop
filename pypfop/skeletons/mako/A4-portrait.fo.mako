<%inherit file="./base.fo.mako" />
<%block name="_page_layout">
    <simple-page-master  master-name="${self.attr.MASTER_NAME}"
                         page-heigh="210mm"
                         page-width="297mm">
        <region-body margin="1cm"/>
        <region-after extent="1cm"/>
    </simple-page-master>
</%block>
${next.body()}
