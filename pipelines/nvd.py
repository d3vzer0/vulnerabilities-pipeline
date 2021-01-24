from dagster import pipeline
from solids.nvd.main import (get_latest_cves,
    parse_cve_details, parse_cve_refs, parse_cve_impacted)
from solids.elastic.main import elastic_upsert

@pipeline
def sync_new_cves():
    new_cves = get_latest_cves()
    elastic_upsert(parse_cve_details(new_cves))
    elastic_upsert(parse_cve_refs(new_cves))
    elastic_upsert(parse_cve_impacted(new_cves))