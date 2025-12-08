import spacy
from typing import List, Tuple
import logging

class SmartFilterService:
    """
    Filters Gematria phrases using Spacy NLP to remove linguistic nonsense.
    """
    _instance = None
    _nlp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SmartFilterService, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """Lazy loads the spacy model."""
        if self._nlp is None:
            try:
                # Disable NE, parser (parser needed for deps, but we might just use POS for speed first)
                # Actually we DO want parser for dependency checks if we get advanced.
                # start with efficient loading.
                self._nlp = spacy.load("en_core_web_sm", disable=["ner"])
            except Exception as e:
                logging.error(f"Failed to load Spacy model: {e}")
                raise e

    def filter_phrases(self, matches: List[Tuple[str, int, int, str, int]]) -> List[Tuple[str, int, int, str, int]]:
        """
        Filters a list of matches.
        Match format: (text, start, end, doc_title, tab_index)
        Returns: List of valid matches.
        """
        if not self._nlp:
            self.load_model()
            
        valid_matches = []
        
        # We process texts. Spacy pipe is faster for batches.
        texts = [m[0] for m in matches]
        
        # Batch process
        # Use n_process=1 to avoid multiprocessing issues in UI threads unless large
        docs = list(self._nlp.pipe(texts, batch_size=50))
        
        for i, doc in enumerate(docs):
            if self._is_valid_phrase(doc):
                valid_matches.append(matches[i])
                
        return valid_matches

    def _is_valid_phrase(self, doc) -> bool:
        """
        Heuristics for a valid phrase.
        """
        # 1. Must have at least one CONTENT word (Noun, Verb, Adj, PropN)
        has_content = False
        all_stopwords = True
        
        # POS tags we consider "Content"
        content_pos = {"NOUN", "VERB", "ADJ", "PROPN", "NUM"}
        
        for token in doc:
            if token.pos_ in content_pos:
                has_content = True
            if not token.is_stop and not token.is_punct:
                all_stopwords = False
                
        if not has_content:
            return False
            
        if all_stopwords and len(doc) > 1:
            # "The of" -> False
            # "At which" -> False
            return False
            
        # 2. Check for hanging prepositions/conjunctions at ends implies bad cut?
        # Stricter rules requested by user.
        if len(doc) > 1:
            first = doc[0]
            last = doc[-1]
            
            # Invalid Starters
            # Cannot start with: CCONJ (and), SCONJ (because), PART ('s), PUNCT
            if first.pos_ in {"CCONJ", "SCONJ", "PART", "PUNCT"}:
                return False
                
            # Invalid Enders
            # Cannot end with: CCONJ, SCONJ, PART, PUNCT, DET (the), ADP (of/at/in), PRON (he/him - usually needs verb)
            if last.pos_ in {"CCONJ", "SCONJ", "PART", "PUNCT", "DET", "ADP", "PRON"}:
                return False
                
            # Pattern Check: DET + PREP (e.g., "The of")
            # If 2 words and ends with ADP/DET, caught above.
            
            # Pattern: ADJ + ADP (e.g. "Good of")
            if len(doc) == 2 and first.pos_ == "ADJ" and last.pos_ == "ADP":
                return False
                
        return True
