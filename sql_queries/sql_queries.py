sql_queries = [
    {"name": "Count Items divided by Permanent Location",
     "description": "",
     "query": "select l.jsonb->>'code' location_code,l.jsonb->>'name' location_name,c.c from "
              "{tenant_id}_mod_inventory_storage.location as l,(select count(effectivelocationid) c, "
              "effectivelocationid id from {tenant_id}_mod_inventory_storage.item i group by effectivelocationid) as c "
              "where c.id = l.id"},
    {"name": "Maximum # holdings per bib",
     "description": "",
     "query": "select instanceid, count(instanceid) from {tenant_id}_mod_inventory_storage.holdings_record group by "
              "instanceid order by count(instanceid) desc limit 1"}
]
# Template
# {"name":"", "description":"", "query": ""}
