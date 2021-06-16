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
              "instanceid order by count(instanceid) desc limit 1"},
    {"name": "", "description": "",
     "query": "SELECT jsonb_set(jsonb, '{status}', '{\"name\":\"Available\",\"date\": \"2021-05-25T21:07:21.459Z\"}'::jsonb) FROM {tenant_id}_mod_inventory_storage.item WHERE jsonb->'status'->>'name' != 'Available'"}
]
# Template
#

# UPDATE fs00001067_mod_inventory_storage.item SET jsonb = jsonb_set(jsonb, '{status}', '{"name":"Available","date":"2021-05-25T21:07:21.459Z"}'::jsonb) WHERE jsonb->'status'->>'name' = 'Checked out'

# SELECT jsonb->'status'->>'name', count(jsonb->'status'->>'name') FROM fs00001034_mod_inventory_storage.item group by jsonb->'status'->>'name';
