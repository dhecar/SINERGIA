<html>
    <style type="text/css">

    </style>
    <body>
        <% row_no=1 %>

        <div style="width:100%;display:table;position: relative; overflow: hidden;" >

        <table cellspacing="${datas.get('cell_spacing')}" align="center">
        %for row in get_record(datas.get('rows'), datas.get('columns'), datas.get('ids'), datas.get('model'), datas.get('number_of_copy')):
               <tr height=${datas.get('height')}>
                    %for col in row:
                        <td width=${datas.get('width')} style="padding: ${datas.get('top_margin')}mm ${datas.get('right_margin')}mm ${datas.get('bottom_margin')}mm ${datas.get('left_margin')}mm">
                            <div>
                            %for val in col:
                                %if val.get('newline'):
                                    <br/>
                                %endif
                                <div style="${val.get('style')}" >
                                    %if val.get('type') == 'normal':
                                        ${val.get('string')}${val.get('value')}
                                    %elif val.get('type') == 'image':
                                        ${val.get('string')}${helper.embed_image('png', val.get('value'), datas.get('image_width', 50),datas.get('image_height', 50))|n}
                                    %elif val.get('type') == 'barcode':
                                        ${val.get('string')}${helper.embed_image('png', generate_barcode(val.get('value'),datas.get('barcode_width', 50),datas.get('barcode_height', 50)), datas.get('barcode_width', 50), datas.get('barcode_height', 50))|n}
                                    %endif
                                </div>
                            %endfor
                            </div>
                        </td>
                    %endfor
               </tr>

        </table>

        </div>

        %endfor




    </body>
</html>