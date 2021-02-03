from dagster import pipeline, ModeDefinition
from solids.nvd.main import (get_latest_cves,
    parse_cve_details, parse_cve_refs, parse_cve_impacted)
from solids.elastic.main import elastic_upsert
from solids.elastic.resource import es_resource

@pipeline(
    mode_defs=[
        ModeDefinition(
            'prod', resource_defs={'es': es_resource}
        )
    ]
)
def sync_new_cves():
    new_cves = get_latest_cves()
    elastic_upsert(parse_cve_details(new_cves))
    elastic_upsert(parse_cve_refs(new_cves))
    elastic_upsert(parse_cve_impacted(new_cves))