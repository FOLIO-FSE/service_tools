sql_queries = [
    {"name": "Count Items divided by Permanent Location",
     "description": "",
     "query": "SELECT L.JSONB->>'code' location_code,L.JSONB->>'name' location_name,C.C FROM "
              "{tenant_id}_MOD_INVENTORY_STORAGE.LOCATION AS L,(SELECT COUNT(EFFECTIVELOCATIONID) C, "
              "EFFECTIVELOCATIONID ID FROM {tenant_id}_MOD_INVENTORY_STORAGE.ITEM I GROUP BY EFFECTIVELOCATIONID) AS C "
              "WHERE C.ID = L.ID"},
    {"name": "Maximum # holdings per bib",
     "description": "",
     "query": "SELECT INSTANCEID, COUNT(INSTANCEID) FROM {tenant_id}_MOD_INVENTORY_STORAGE.HOLDINGS_RECORD GROUP BY "
              "INSTANCEID ORDER BY COUNT(INSTANCEID) DESC LIMIT 1"}
]
# Template
# {"name":"", "description":"", "query": ""}
