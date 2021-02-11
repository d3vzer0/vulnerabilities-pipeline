import re
from collections import defaultdict

PATTERNS = [
    {
        'name': 'cve',
        'key': 'id',
        'model': 'vulnerability',
        'regex': re.compile('(?i)(?P<id>CVE-\d{4}-\d{4,5})')
    },
    {
        'name': 'cpe',
        'key': 'cpe',
        'model': 'impacted',
        'regex': re.compile('(?i)(?P<cpe>cpe:(?P<cpe_version>\d\.\d):(?P<part>\w):(?P<vendor>.*?):(?P<product>.*?):(?P<version>.*?):(?P<update>.*?):(?P<edition>.*?):(?P<language>.*?):(?P<sw_edition>.*?):(?P<target_sw>.*?):(?P<target_hw>.*?):(?P<other>.*?))\s')
    },
    {
        'name': 'MSADV',
        'key': 'id',
        'model': 'vulnerability',
        'regex': re.compile('(?i)(?P<id>ADV\d{6})')
    },
    {
        'name':'F5KB',
        'key': 'id',
        'model': 'vulnerability',
        'regex': re.compile('(?i)(?P<id>K\d{8})')
    }
]

class Match:
    def __init__(self, content = None):
        self.content = content
        self.results = { }

    @staticmethod
    def __rename(model, data):
        return {f'{model}.{key}': value for key, value in data.items()}
 
    @property
    def denormalized(self):
        denorm = defaultdict(list)
        for pattern in self.results.values():
            for match in pattern:
                for key, value in match.items():
                    denorm[key].append(value)
                    denorm['tags'].append(value)
        return dict(denorm)

    def from_regex(self, pattern_selection):
        patterns = [pattern for pattern in PATTERNS if pattern['name'] in pattern_selection]
        for pattern in patterns:
            matches = {m.groupdict()[pattern['key']]:
                Match.__rename(pattern['model'], m.groupdict()) for m in pattern['regex'].finditer(self.content)}
            self.results[pattern['name']] = list(matches.values())