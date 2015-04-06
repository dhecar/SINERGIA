## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

        .list_main_table {

        text-align:center;
        margin-top: 15px;
        }
        .list_main_table th {
        text-align:center;
        font-size:11;
        padding-right:3px;
        padding-left:3px;

        }
        .list_main_table td {

        text-align:center;
        font-size:11;
        padding-right:3px;
        padding-left:3px;
        padding-top:3px;
        padding-bottom:3px;
        }
        .list_main_table thead {
        border-bottom:1px solid;

        }

        div.formatted_note {
        text-align:left;
        padding-left:10px;
        font-size:11;
        }

        .totals {
        font-size:12px;
        }


        .cabecera {
        z-index:-1;
        margin-bottom:10px;
        text-align:right;


        }

        .datos_empresa {
        font-size:12px;
        text-align:right;
        float:right;
        margin-top:85px;

        }

        .datos_cliente {
        font-size:12px;
        float:left;
        top:10px;
        z-index:2;
        width:300px;
        text-align:left;
                }

        .datos_pedido{
        float:left;
        margin-top:30px;
        margin-bottom:30px;
        width:400px;
        text-align:left;
        }

        .datos_pedido td {
        font-size:11px;
        color:#424242;
        }

        .datos_pedido td b {
        text-transform: uppercase;
        font-size:12px;
        }

        .ref {
        font-size:9px;
        text-align:center;
        }
    </style>
</head>


<body>

    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>

    <%def name="address(partner)">
        <%doc>
            XXX add a helper for address in report_webkit module as this won't be suported in v8.0
        </%doc>
        %if partner.parent_id:
            <tr><td class="name">${partner.parent_id.name or ''}</td></tr>
            <tr><td>${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
	    <tr><td>${partner.parent_id.website}</td></tr>
            <% address_lines = partner.contact_address.split("\n")[1:] %>
        %else:
            <tr><td>${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
            <% address_lines = partner.contact_address.split("\n") %>
	    ${partner.state_id.name}
        %endif
        %for part in address_lines:
            % if part:
                <tr><td>${part}</td></tr>
            % endif
        %endfor
    </%def>

     %for order in objects:
    <% setLang(order.partner_id.lang) %>
    <%
      quotation = order.state in ['draft', 'sent']
    %>

<div class="orden">
    <table class="list_main_table" width="100%">
      <thead>
          <tr>
            <th >${_("Ref. Art")}</th>
	        <th class="main_col1">${_("Description")}</th>
	        <th class="amount main_col2">${_("Quantity")}</th>
            <th class="amount main_col4">${_("Precio")}</th>
            <th class="amount main_col6">${_("Dto%")}</th>
	        <th class="amount main_col7">${_("Importe")}</th>
          </tr>
      </thead>
      <tbody>
        %for line in order.order_line:
	   <tr>
	    <td class="ref">${line.product_id.default_code}</td>
	    <td class="ref align_top"><div class="nobreak">${line.product_id.name.replace('\n','<br/>') or '' | n}
                 %if line.formatted_note:
                 <br />
                 <div class="formatted_note">${line.formatted_note| n}</div>
                 %endif
                 </div>
            </td>
	    <td class="ref">${ formatLang(line.product_uos and line.product_uos_qty or line.product_uom_qty) }</td>


	   <td class="ref">${formatLang(line.price_unit)}</td>
       <td class="ref">${line.discount and formatLang(line.discount, digits=get_digits(dp='Sale Price')) or '    '    } ${line.discount and '%' or ''}</td>
       <td class="ref">${formatLang(line.price_subtotal, digits=get_digits(dp='Sale Price'))}&nbsp;${order.pricelist_id.currency_id.symbol}</td>
          </tr>
        %endfor
      </tbody>
      <tfoot>
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td>
            ${_("Net Total:")}
          </td>
          <td class="amount total_sum_cell">
            ${formatLang(order.amount_untaxed, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td >
            ${_("Taxes:")}
          </td>
          <td class="amount total_sum_cell">
            ${formatLang(order.amount_tax, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td >
            ${_("Total:")}
          </td>
          <td class="amount total_sum_cell">
            <b>${formatLang(order.amount_total, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}</b>
          </td>
        </tr>
      </tfoot>
    </table>

    %if order.note :
        <p class="std_text">${order.note | carriage_returns}</p>
    %endif
    %if order.note2:
        <p class="std_text">${order.note2 | n}</p>
    %endif

 %endfor
    </div>
</body>
</html>

