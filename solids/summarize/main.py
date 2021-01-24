from .utils.transforms import Transform
from .utils.extract import Extract
from .utils.tfidf import TFIDF
from dagster import solid, Field, String, List, Float

# url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

@solid(
    config_schema={
        'patterns_file': Field(
            String,
            is_required=False,
            default_value='solids/summarize/patterns/vulnerabilities.jsonl',
            description='Custom patterns file'
        ),
        'threshold': Field(
            Float,
            is_required=False,
            default_value=0.1,
            description='TFIDF Threshold'
        ),
        'model': Field(
            String,
            is_required=False,
            default_value='en_core_web_md',
            description='Spacy model'
        )
    }
)
def summarize_feeds(context, latest_entries: List, all_entries: List):   
    combined_entries = latest_entries + all_entries
    context.log.info(f'Extraction dataset size {len(combined_entries)}')

    all_docs = [Transform(doc['rss.content']).clean for doc in combined_entries]
    docs_props = Extract.from_docs(all_docs, 
        model=context.solid_config['model'], custom_patterns=context.solid_config['patterns_file']).props()
    get_tags = TFIDF(threshold=context.solid_config['threshold']).keywords([{'title': doc['rss.title'], 
        'content': '__'.join(list(docs_props[index]))} for index, doc in enumerate(combined_entries)])
    to_save = [{**entry, 'tags': get_tags.get(entry['rss.title'], [])} for entry in latest_entries]

    context.log.info(f'Sample: {to_save[:2]}')
    return to_save