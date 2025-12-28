"""
Etymology Service for Document Manager Pillar.
Handles looking up word origins using:
- Offline: ety-python library
- Online: Free Dictionary API, Sefaria (Hebrew), Wiktionary (Greek/English)
"""
import requests
import logging
import re
from functools import lru_cache
from typing import Dict, Optional

# Try to import BeautifulSoup for enhanced scraping
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Setup logger
logger = logging.getLogger(__name__)


class EtymologyService:
    """
    Service to fetch etymology/origin of words.
    Features:
    - Auto-detects Hebrew, Greek, or Latin/English scripts.
    - Prioritizes Sefaria for Hebrew (BDB lexicon).
    - Deep scrapes Wiktionary Ancient Greek for Greek words.
    - Uses ety-python (offline) or Free Dictionary API for English.
    """

    def __init__(self):
        self._ety_available = False
        try:
            import ety
            self._ety_available = True
            logger.info("ety-python library detected. Offline mode enabled.")
        except ImportError:
            logger.warning("ety-python library not found. Running in online-only mode.")

    def _detect_script(self, text: str) -> str:
        """
        Detects if the word is Hebrew, Greek, or Latin (English/Default).
        """
        for char in text:
            # Hebrew Block: 0590–05FF
            if '\u0590' <= char <= '\u05ff':
                return 'hebrew'
            # Greek Block: 0370–03FF or Greek Extended: 1F00–1FFF
            if ('\u0370' <= char <= '\u03ff') or ('\u1f00' <= char <= '\u1fff'):
                return 'greek'
        return 'latin'

    @lru_cache(maxsize=128)
    def get_word_origin(self, word: str) -> Dict[str, str]:
        """
        Get the origin of a word. Auto-detects script and routes accordingly.
        """
        word = word.strip()
        if not word:
            return {"source": "None", "origin": "Please enter a word.", "details": ""}

        script = self._detect_script(word)

        # --- ROUTING BASED ON SCRIPT ---
        
        # 1. HEBREW PATH (Sefaria -> Wiktionary)
        if script == 'hebrew':
            logger.info(f"Hebrew script detected for: {word}")
            # Try Sefaria first (The "Deep" Theological Data)
            sefaria_result = self._lookup_hebrew_sefaria(word)
            if sefaria_result:
                return sefaria_result
            # Fallback to Wiktionary (Hebrew section)
            return self._scrape_wiktionary(word, target_lang="Hebrew") or self._empty_result()

        # 2. GREEK PATH (Wiktionary Ancient Greek -> English fallback)
        if script == 'greek':
            logger.info(f"Greek script detected for: {word}")
            # Lowercase for Wiktionary (entries are typically lowercase)
            word_lower = word.lower()
            # Try Wiktionary aiming for 'Ancient Greek' specifically
            return self._scrape_wiktionary(word_lower, target_lang="Ancient_Greek") or self._empty_result()

        # 3. ENGLISH/LATIN PATH (ety -> API -> Wiktionary)
        if self._ety_available:
            res = self._try_offline_ety(word.lower())
            if res:
                return res
        
        res = self._try_online_api(word.lower())
        if res:
            return res
        
        return self._scrape_wiktionary(word.lower(), target_lang="English") or self._empty_result()

    def _empty_result(self) -> Dict[str, str]:
        return {"source": "None", "origin": "No etymology found.", "details": ""}

    # --- HEBREW SPECIFIC HANDLER ---
    def _lookup_hebrew_sefaria(self, word: str) -> Optional[Dict[str, str]]:
        """
        Queries Sefaria Lexicon API for deep Hebrew roots/definitions.
        Uses Klein Dictionary and other Hebrew lexicons.
        """
        try:
            url = f"https://www.sefaria.org/api/words/{word}"
            logger.info(f"Querying Sefaria: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    return None
                
                # Sefaria returns a list of lexicon entries
                html_parts = []
                
                for entry in data:
                    headword = entry.get('headword', word)
                    # Correct field name is 'parent_lexicon', not 'lexicon'
                    lexicon = entry.get('parent_lexicon', 'Unknown')
                    
                    block = f"<h4>{headword} <span style='font-size:small; color:gray'>({lexicon})</span></h4>"
                    
                    # Content contains morphology and senses
                    content = entry.get('content', {})
                    
                    # Morphology (part of speech)
                    morphology = content.get('morphology', '')
                    if morphology:
                        block += f"<p><i>{morphology}</i></p>"
                    
                    # Definitions are in content.senses
                    senses = content.get('senses', [])
                    if senses:
                        def_html = ""
                        for sense in senses:
                            if isinstance(sense, dict):
                                definition = sense.get('definition', '')
                                if definition:
                                    def_html += f"<li>{definition}</li>"
                            elif isinstance(sense, str):
                                def_html += f"<li>{sense}</li>"
                        if def_html:
                            block += f"<ul>{def_html}</ul>"
                    
                    # Notes often contain rich etymological info
                    notes = entry.get('notes', '')
                    if notes:
                        # Clean HTML links but keep content
                        notes_clean = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', notes)
                        block += f"<p style='color:#475569; font-size:small;'><b>Notes:</b> {notes_clean}</p>"
                    
                    # Derivatives
                    derivatives = entry.get('derivatives', '')
                    if derivatives:
                        deriv_clean = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', derivatives)
                        block += f"<p style='font-size:small;'>{deriv_clean}</p>"

                    html_parts.append(block)

                if html_parts:
                    return {
                        "source": "Sefaria (Jewish Library)",
                        "origin": "".join(html_parts),
                        "details": "Data provided by Sefaria.org API"
                    }
        except Exception as e:
            logger.error(f"Sefaria lookup failed: {e}")
        return None

    # --- OFFLINE ETY HANDLER ---
    def _try_offline_ety(self, word: str) -> Optional[Dict[str, str]]:
        """Try ety-python library for offline etymology."""
        try:
            import ety
            origins = ety.origins(word)
            
            if origins:
                origin_list = [f"{o.word} ({o.language.name})" for o in origins]
                origin_text = f"Derived from: {', '.join(origin_list)}"
                return {
                    "source": "Offline (ety-python)",
                    "origin": origin_text,
                    "details": "Recursive tree view not captured in text mode."
                }
        except Exception as e:
            logger.error(f"Error in ety lookup: {e}")
        return None

    # --- ONLINE API HANDLER ---
    def _try_online_api(self, word: str) -> Optional[Dict[str, str]]:
        """Try Free Dictionary API for English words."""
        try:
            logger.info(f"Fallback to API for word: {word}")
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    origin = entry.get("origin")
                    
                    if origin:
                        return {
                            "source": "Online (Free Dictionary API)",
                            "origin": origin,
                            "details": "Fetched from dictionaryapi.dev"
                        }
                    
                # If word found but no origin, fall through to scraper
                logger.info("API found word but missing origin. Attempting Wiktionary scrape...")
        except Exception as e:
            logger.error(f"Error in API lookup: {e}")
        return None

    # --- WIKTIONARY SCRAPER ---
    def _scrape_wiktionary(self, word: str, target_lang: str = "English") -> Optional[Dict[str, str]]:
        """
        Enhanced scraper that targets specific languages (Ancient_Greek, Hebrew, English).
        Uses BeautifulSoup if available for cleaner parsing.
        """
        # Try BeautifulSoup method first if available
        if BS4_AVAILABLE:
            result = self._scrape_wiktionary_bs4(word, target_lang)
            if result:
                return result
        
        # Fallback to regex method
        return self._scrape_wiktionary_regex(word, target_lang)

    def _scrape_wiktionary_bs4(self, word: str, target_lang: str) -> Optional[Dict[str, str]]:
        """BeautifulSoup-based Wiktionary scraper for cleaner parsing."""
        try:
            url = f"https://en.wiktionary.org/wiki/{word}"
            headers = {'User-Agent': 'IsopGem/1.0'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Wiktionary now puts IDs directly on h2 elements, not spans
            # Try to find <h2 id="Greek"> or <h2 id="Ancient_Greek">
            lang_h2 = soup.find('h2', id=target_lang)
            
            # Fallback: For Ancient Greek search, also try plain "Greek"
            if not lang_h2 and target_lang == "Ancient_Greek":
                lang_h2 = soup.find('h2', id="Greek")
            
            # Also fallback to looking for span inside h2 (older structure)
            if not lang_h2:
                lang_span = soup.find('span', id=target_lang)
                if lang_span:
                    lang_h2 = lang_span.find_parent('h2')
            
            if not lang_h2:
                logger.warning(f"Language section '{target_lang}' not found on {url}")
                return None
            
            # The h2 might be inside a div.mw-heading, get the parent div
            parent_div = lang_h2.parent
            if parent_div and parent_div.get('class') and 'mw-heading' in parent_div.get('class', []):
                starting_point = parent_div
            else:
                starting_point = lang_h2
                
            content_html = []
            
            # Iterate through siblings after the language heading
            for sibling in starting_point.find_next_siblings():
                # Stop at next h2 (next language section)
                if sibling.name == 'h2':
                    break
                # Also stop at div containing h2
                if sibling.name == 'div' and sibling.find('h2'):
                    break
                
                # Handle div.mw-heading containing h3/h4/h5
                if sibling.name == 'div' and 'mw-heading' in sibling.get('class', []):
                    header_elem = sibling.find(['h3', 'h4', 'h5'])
                    if header_elem:
                        header = header_elem.get_text().strip()
                        # Remove "[edit]" text
                        header = re.sub(r'\[edit\]', '', header).strip()
                        
                        wanted = ["Etymology", "Noun", "Verb", "Adjective", "Root", 
                                  "Inflection", "Declension", "Conjugation", "Numeral", "Definitions"]
                        if any(x in header for x in wanted):
                            content_html.append(f"<h4>{header}</h4>")
                    continue
                
                # Check direct headers (older structure)
                if sibling.name in ['h3', 'h4', 'h5']:
                    header = sibling.get_text().strip()
                    header = re.sub(r'\[edit\]', '', header).strip()
                    
                    wanted = ["Etymology", "Noun", "Verb", "Adjective", "Root", 
                              "Inflection", "Declension", "Conjugation", "Numeral", "Definitions"]
                    if any(x in header for x in wanted):
                        content_html.append(f"<h4>{header}</h4>")
                    continue
                
                # Capture paragraphs and lists
                if sibling.name == 'p':
                    text = sibling.get_text().strip()
                    if text:  # Only non-empty
                        content_html.append(str(sibling))
                elif sibling.name in ['ol', 'ul']:
                    content_html.append(str(sibling))
                elif sibling.name == 'table':
                    # Greek Declension tables
                    classes = sibling.get('class', [])
                    if 'inflection-table' in classes:
                        content_html.append(str(sibling))
            
            if content_html:
                final_html = "".join(content_html)
                # Clean up internal wiki links
                final_html = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', final_html)
                return {
                    "source": f"Wiktionary ({target_lang.replace('_', ' ')})",
                    "origin": final_html,
                    "details": f"Scraped from {url}"
                }

        except Exception as e:
            logger.error(f"BS4 scrape failed: {e}")
        return None

    def _scrape_wiktionary_regex(self, word: str, target_lang: str) -> Optional[Dict[str, str]]:
        """Regex-based Wiktionary scraper (fallback when BS4 not available)."""
        try:
            url = f"https://en.wiktionary.org/wiki/{word}"
            logger.info(f"Scraping Wiktionary: {url}")
            response = requests.get(url, headers={'User-Agent': 'IsopGem/1.0'}, timeout=5)
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # --- 1. Isolate Language Section ---
            target_langs = [target_lang]
            if target_lang == "English":
                target_langs = ["English", "Ancient_Greek", "Hebrew"]
            
            eng_match = None
            lang_found = "Unknown"
            
            for lang in target_langs:
                pattern = fr'(id="{lang}"[^>]*>)(.*?)(?=<h2|<div class="mw-heading mw-heading2")'
                eng_match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                
                if not eng_match:
                    eng_match = re.search(fr'(id="{lang}"[^>]*>)(.*)', html, re.DOTALL | re.IGNORECASE)
                
                if eng_match:
                    lang_found = lang.replace("_", " ")
                    break
                 
            if not eng_match:
                return None
            
            eng_chunk = eng_match.group(2)
            
            # Helper to clean text
            def clean_html_text(text):
                text = re.sub(r'<sup[^>]*>.*?</sup>', '', text, flags=re.DOTALL)
                text = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', text, flags=re.DOTALL)
                text = re.sub(r'<span [^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
                text = re.sub(r' class="[^"]*"', '', text)
                text = re.sub(r' id="[^"]*"', '', text)
                text = re.sub(r' style="[^"]*"', '', text)
                return text

            etymologies = []
            
            # Find Etymology headers
            has_etym = list(re.finditer(r'id="(Etymology(?:_\d+)?)"', eng_chunk))
            
            if has_etym:
                for match in has_etym:
                    etym_id = match.group(1)
                    start_idx = match.end()
                    
                    content_chunk = eng_chunk[start_idx:]
                    next_header = re.search(r'<(h3|h4|div class="mw-heading)', content_chunk)
                    if next_header:
                        block = content_chunk[:next_header.start()]
                    else:
                        block = content_chunk
                        
                    p_matches = re.findall(r'<p>(.*?)</p>', block, re.DOTALL)
                    if p_matches:
                        full_text = "<br><br>".join(p_matches)
                        clean_text = clean_html_text(full_text)
                        
                        title = "Etymology"
                        if "_" in etym_id:
                            parts = etym_id.split('_')
                            if parts[-1].isdigit():
                                title = f"Etymology {parts[-1]}"
                        etymologies.append(f"<h4>{title}</h4>{clean_text}")
            
            # --- Find Definitions ---
            pos_headers = ["Noun", "Verb", "Adjective", "Adverb", "Proper_noun", 
                           "Pronoun", "Preposition", "Conjunction", "Interjection", "Numeral"]
            definitions = []
            
            for pos in pos_headers:
                pos_iter = re.finditer(fr'id="{pos}"', eng_chunk, re.IGNORECASE)
                
                for match in pos_iter:
                    start = match.end()
                    chunk = eng_chunk[start:]
                    
                    ol_match = re.search(r'<ol>(.*?)</ol>', chunk, re.DOTALL)
                    
                    if ol_match:
                        li_content = ol_match.group(1)
                        items = re.findall(r'<li>(.*?)</li>', li_content, re.DOTALL)
                        
                        cleaned_items = []
                        for item in items[:5]:
                            item_no_ex = re.sub(r'<ul[^>]*>.*?</ul>', '', item, flags=re.DOTALL)
                            item_no_dl = re.sub(r'<dl[^>]*>.*?</dl>', '', item_no_ex, flags=re.DOTALL)
                            clean = clean_html_text(item_no_dl)
                            if clean.strip():
                                cleaned_items.append(f"<li>{clean.strip()}</li>")
                        
                        if cleaned_items:
                            pos_label = pos.replace("_", " ")
                            definitions.append(f"<h4>{pos_label}</h4><ul>{''.join(cleaned_items)}</ul>")

            # Combine
            final_parts = []
            if etymologies:
                final_parts.append("<hr>".join(etymologies))
            
            if definitions:
                if final_parts:
                    final_parts.append("<hr>")
                final_parts.append("<h3>Definitions</h3>")
                final_parts.append("".join(definitions))
                
            if final_parts:
                final_html = "".join(final_parts)
                return {
                    "source": f"Wiktionary ({lang_found})",
                    "origin": final_html,
                    "details": f"Deep scrape from {url}"
                }

        except Exception as e:
            logger.error(f"Error scraping Wiktionary: {e}")
            
        return None


# Global instance
_etymology_service = None


def get_etymology_service() -> EtymologyService:
    """Get the global singleton instance of the EtymologyService."""
    global _etymology_service
    if _etymology_service is None:
        _etymology_service = EtymologyService()
    return _etymology_service
