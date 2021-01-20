
from dagster import pipeline, solid, Field, Int, Dict, String, List
from datetime import datetime, timedelta
from elastic.elastic_pipeline import elastic_upsert
from .utils.api import NVD
from .utils.transforms import CVE

@solid(
    config_schema={
        'fetch_days': Field(
            Int,
            is_required=False,
            default_value=7,
            description='Default amount of days to sync on first run'
        ),
        'max_results': Field(
            Int,
            is_required=False,
            default_value=2000,
            description='Total amount of records to download'
        )
    }
)
def get_latest_cves(context) -> List[Dict]:
    ''' Get the latest CVEs frtom the NVD API '''
    init_date = datetime.utcnow() - timedelta(days=context.solid_config['fetch_days'])
    init_date_fmt = init_date.strftime('%Y-%m-%dT%H:%M:%S:000 UTC-00:00')
    params = { 'resultsPerPage': context.solid_config['max_results'],
        'modStartDate': init_date_fmt }

    with NVD(params) as nvd:
        all_cves = nvd.cves
        context.log.info(f'Found {len(all_cves)} CVEs')
        return all_cves

@solid
def parse_cve_details(context, cves: List[Dict]) -> List[Dict]:
    ''' Parse CVE details to ECS Schema '''
    context.log.info(f'Parsing details for  {len(cves)} entries')
    cve_details = [CVE(cve=cve).details for cve in cves]
    context.log.info(f'Sample details - {cve_details[0]}')
    return cve_details

@solid
def parse_cve_impacted(context, cves: List[Dict]) -> List[Dict]:
    ''' Parse Impacted products to ECS Schema '''
    context.log.info(f'Parsing impacted for  {len(cves)} entries')
    impacted = [cpe for cve in cves for cpe in CVE(cve=cve).impacted] 
    context.log.info(f'Sample impact - {impacted[0]}')
    return impacted

@solid
def parse_cve_refs(context, cves: List[Dict]) -> List[Dict]:
    ''' Parse CVE Refs to ECS Schema '''
    context.log.info(f'Parsing references for  {len(cves)} entries')
    references = [cpe for cve in cves for cpe in CVE(cve=cve).references] 
    context.log.info(f'Sample reference - {references[0]}')
    return references

@pipeline
def sync_new_cves():
    new_cves = get_latest_cves()
    elastic_upsert(parse_cve_details(new_cves))
    elastic_upsert(parse_cve_refs(new_cves))
    elastic_upsert(parse_cve_impacted(new_cves))