## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

.list_main_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
    margin-top: 15px;
}
.list_main_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_main_table td {
    border-bottom : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_main_table thead {
    display:table-header-group;
}

div.formatted_note {
    text-align:left;
    padding-left:10px;
    font-size:11;
}


.list_bank_table {
    text-align:center;
    border-collapse: collapse;
    page-break-inside: avoid;
    display:table;
}

.act_as_row {
   display:table-row;
}
.list_bank_table .act_as_thead {
    background-color: #EEEEEE;
    text-align:left;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
    white-space:nowrap;
    background-clip:border-box;
    display:table-cell;
}
.list_bank_table .act_as_cell {
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
    white-space:nowrap;
    display:table-cell;
}


.list_tax_table {
}
.list_tax_table td {
    text-align:left;
    font-size:12;
}
.list_tax_table th {
}
.list_tax_table thead {
    display:table-header-group;
}


.list_total_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_total_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px
    padding-left:3px
}
.list_total_table thead {
    display:table-header-group;
}


.no_bloc {
    border-top: thin solid  #ffffff ;
}

.right_table {
    right: 4cm;
    width:"100%";
}

.std_text {
    font-size:12;
}

tfoot.totals tr:first-child td{
    padding-top: 15px;
}

tfoot.totals td {
    border: thin solid  #ffffff;
}

th.date {
    width: 90px;
}

td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}
.header_table {
    text-align: center;
    border: 1px solid lightGrey;
    border-collapse: collapse;
}
.header_table th {
    font-size: 12px;
    border: 1px solid lightGrey;
}
.header_table td {
    font-size: 12px;
    border: 1px solid lightGrey;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}
.address .recipient {
    font-size: 12px;
    border: 1px solid blue;
}

.nobreak {
     page-break-inside: avoid;
 }

.align_top {
     vertical-align:text-top;
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

    <div style="border:1px solid;margin:12px;width:300px;float:left">

        <table class="recipient">
	 
	 <tr><td><b>${order.partner_id.ref}</b></td></tr>
	 <tr><td>${order.partner_id.name}</td></tr>
	 <tr><td>${order.partner_id.street}</td></tr>
	 <tr><td>${order.partner_id.zip} ${order.partner_id.city}(${order.partner_id.state_id.name})</td></tr>
	 <tr><td>${order.partner_id.country_id.name}</td></tr>
        </table>

    </div>
    

    <h1 style="clear:both;">${quotation and _(u'Quotation N°') or _(u'Order N°') } ${order.name}</h1>


    <div>   
    <table class="basic_table" width="100%">
        <tr>
            <th class="date">${quotation and _("Date Ordered") or _("Quotation Date")}</td>
            <th>${_("Your Reference")}</td>
            <th>${_("Vendedor")}</td>
            <th>${_('Payment Term')}</td>
        </tr>
        <tr>
            <td class="date">${formatLang(order.date_order, date=True)}</td>
            <td>${order.client_order_ref or ''}</td>
            <td>${order.user_id and order.user_id.name or ''}</td>
            <td>${order.payment_term and order.payment_term.note or ''}</td>
        </tr>
    </table>

    %if order.note1:
        <p class="std_text"> ${order.note1 | n} </p>
    %endif
    </div>    

    <table class="list_main_table" width="100%">
      <thead>
          <tr>
            <th class="amount main_col2">${_("Quantity")}</th>
	    <th class="main_col1">${_("Description")}</th>
            <th class="amount main_col4">${_("Pr.Unid. €")}</th>
            <th class="main_col5">${_("I.V.A.")}</th>
            <th class="amount main_col6">${_("Disc.(%)")}</th>
   
	    <th class="amount main_col7">${_("Price")}</th>
          </tr>
      </thead>
      <tbody>
        %for line in order.order_line:
	   <tr>
	    <td class="amount main_col2 align_top">${ formatLang(line.product_uos and line.product_uos_qty or line.product_uom_qty) }</td>
            <td class="align_top"><div class="nobreak">${line.name.replace('\n','<br/>') or '' | n}
                 %if line.formatted_note:
                 <br />
                 <div class="formatted_note">${line.formatted_note| n}</div>
                 %endif
                 </div>
            </td>

	   <td class="amount main_col4 align_top">${formatLang(line.price_unit)}</td>
            <td class="main_col5 align_top">${ ', '.join([tax.description or tax.name for tax in line.tax_id]) }</td>
              <td class="amount main_col6 align_top">${line.discount and formatLang(line.discount, digits=get_digits(dp='Sale Price')) or '    '    } ${line.discount and '%' or ''}</td>
            <td class="amount main_col7 align_top">${formatLang(line.price_subtotal, digits=get_digits(dp='Sale Price'))}&nbsp;${order.pricelist_id.currency_id.symbol}</td>
          </tr>
        %endfor
      </tbody>
      <tfoot class="totals">
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td style="font-weight:bold">
            ${_("Net Total:")}
          </td>
          <td class="amount total_sum_cell">
            ${formatLang(order.amount_untaxed, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td style="font-weight:bold">
            ${_("Taxes:")}
          </td>
          <td class="amount total_sum_cell">
            ${formatLang(order.amount_tax, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="total_empty_cell"/>
          <td style="font-weight:bold">
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
    <p style="page-break-after:always"/>
    %endfor
</body>
</html>
