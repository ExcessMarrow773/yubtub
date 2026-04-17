import re
import json
from django import template
from django.conf import settings

register = template.Library()

def load_word_list(min_intensity=1, categories=None):
    """
    Load words from better-profane-words words.json.
    
    min_intensity: 1=mild, 2=moderate, 3=strong, 4=very strong, 5=extreme
    categories: list of categories to include, or None for all
                e.g. ['sexual', 'slur_racial', 'slur_gender', 'hateful_ideology']
    """
    path = settings.BASE_DIR / 'data' / 'words.json'
    with open(path) as f:
        data = json.load(f)

    words = []
    for entry in data:
        if entry['intensity'] < min_intensity:
            continue
        if categories and not any(c in entry['categories'] for c in categories):
            continue
        words.append(entry['word'])
    return words

def build_patterns(words):
    patterns = []
    for word in words:
        escaped = re.escape(word)
        pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
        patterns.append(pattern)
    return patterns

def make_replacement(match):
    original = match.group()
    if len(original) <= 2:
        return original[0] + '#'
    return original[0] + '#' * (len(original) - 2) + original[-1]

# Load and compile once at module level
WORDS = load_word_list(min_intensity=2)  # skip very mild words like 'crap'
COMPILED_PATTERNS = build_patterns(WORDS)

def apply_filter(text):
    for pattern in COMPILED_PATTERNS:
        text = pattern.sub(make_replacement, text)
    return text

@register.filter(name='censor')
def censor(text, user):
    if not user.is_authenticated:
        return apply_filter(text)
    if not user.use_naughty_words:
        return apply_filter(text)
    return text