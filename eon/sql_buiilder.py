# sql_builder.py
def build_sql_query(filters):
    """
    Build a SQL query using the provided filters.
    The base query is fixed; the date range (and, optionally, order_status and order_action)
    are appended as WHERE conditions.
    """
    sql_query = f"""
select DISTINCT 
    si.order_no,
    si.item_no,
    ii.action as 'Order Action',
    oo.order_type as 'Order Type',
    sca.account_no as 'BAN',
    sca.account_name as 'CustName',
    itc.description,
    psp.sub_profile_desc,
    si.circuit_id as 'FroId',
    scp.cpi_status_code as 'Circuit Status',
    case when sva.cust_site_id != 'null' then aa.address + '  ' + aa.city + ' ' + aa.state + ' ' + aa.country else '' end as 'Customer Prem Address A',
    case when sva.cust_site_id != 'null' then ca.country_name else '' end as 'A customer prem country',
    case when svz.cust_site_id != 'null' then az.address + '  ' + az.city + ' ' + az.state + ' ' + az.country else '' end as 'Customer Prem Address Z',
    case when svz.cust_site_id != 'null' then cz.country_name else '' end as 'Z customer prem country',
    ii.create_date as 'Created Date'
from orders oo 
    join sonet_item si on oo.id = si.order_no  
    join improv_item ii on ii.id = si.id  
    join sonet_vendor_interface sva on sva.side = 'A' and sva.item_id = si.id  
    left outer join site sa on sva.cust_site_id = sa.site_id  
    left outer join address aa on sa.address_id = aa.address_id  
    join sonet_vendor_interface svz on svz.side = 'Z' and svz.item_id = si.id  
    left outer join site sz on svz.cust_site_id = sz.site_id  
    left outer join address az on sz.address_id = az.address_id  
    left outer join country ca on ca.country_alpha3_code = aa.country  
    left outer join country cz on cz.country_alpha3_code = az.country,
    profile_sub_profile psp,
    improv_item_catalog itc,
    sonet_customer_account sca,
    sonet_cpi scp
where 
    si.sub_profile_code = psp.id 
    and sca.account_no = oo.account_no 
    and si.circuit_id = scp.circuit_id 
    and itc.item_type = psp.item_type
"""
    # Append the date range condition using the converted dates
    sql_query += f"\nand ii.create_date between '{filters['start_date']}' and '{filters['end_date']}'"

    # Append additional filters if they are not "ALL"
    if filters.get("order_status", "ALL").upper() != "ALL":
        sql_query += f"\nand oo.order_status = '{filters['order_status']}'"
    if filters.get("order_action", "ALL").upper() != "ALL":
        sql_query += f"\nand ii.action = '{filters['order_action']}'"

    return sql_query
