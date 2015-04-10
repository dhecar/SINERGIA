## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

        .list_main_table {

        text-align:left;

        }
        .list_main_table th {
        text-align:left;
        font-size:11;
        padding-right:3px;
        padding-left:3px;

        }
        .list_main_table td {

        text-align:left;
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


        .ref {
        font-size:9px;
        text-align:center;

        }
        .totals {
        font-size:12px;
        }
    </style>
</head>
<body>

 %for order in objects:
    <% setLang(order.partner_id.lang) %>
    <%
      quotation = order.state in ['draft', 'sent']
    %>

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
	    <td class="ref align_top">
                <div class="nobreak">${line.product_id.name.replace('\n','<br/>') or '' | n}
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



    <p style="page-break-after:default"/>
    %endfor

    </body>
</html>
