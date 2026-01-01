"""
Theosophical Glossary Scraper Service.

Scrapes the Encyclopedic Theosophical Glossary from theosociety.org
and provides lookup functionality for enrichment.
"""
import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TheosophicalEntry:
    """A glossary entry from the Theosophical Glossary."""
    term: str
    definition: str
    language: Optional[str] = None
    source_page: Optional[str] = None


class TheosophicalGlossaryService:
    """
    Service for querying the Encyclopedic Theosophical Glossary.
    
    Data is scraped once and cached locally as JSON.
    Subsequent lookups use the local cache.
    """
    
    BASE_URL = "https://www.theosociety.org/pasadena/etgloss/"
    
    # All section pages (alphabetical ranges)
    SECTION_PAGES = [
        "a-adh.htm", "adi-ag.htm", "ah-al.htm", "am-ani.htm", "anj-arc.htm",
        "ard-asr.htm", "ass-atm.htm", "ato-az.htm", "ba-be.htm", "bh-bo.htm",
        "br-bz.htm", "ca-ce.htm", "cha-chy.htm", "ci-cz.htm", "daa-der.htm",
        "des-dir.htm", "dis-dz.htm", "ea-el.htm", "em-ez.htm", "fa-fz.htm",
        "ga-gl.htm", "gn-gz.htm", "ha-hh.htm", "hi-hz.htm", "ia-iz.htm",
        "ja-jz.htm", "ka.htm", "ke-kz.htm", "la-li.htm", "lo-lz.htm",
        "ma-mam.htm", "man-mar.htm", "mas-me.htm", "mi-mo.htm", "mp-mz.htm",
        "na-ne.htm", "nf-nz.htm", "oa-oz.htm", "pa-peq.htm", "per-pi.htm",
        "pl-pral.htm", "pram-prj.htm", "pro-pz.htm", "q-rec.htm", "red-roos.htm",
        "root-rz.htm", "saa-sal.htm", "sam-saq.htm", "sar-sec.htm", "sed-sez.htm",
        "sh-sir.htm", "sis-som.htm", "son-sq.htm", "sr-sum.htm", "sun-sz.htm",
        "ta-tel.htm", "tem-thn.htm", "tho-tre.htm", "tri-tz.htm", "ua-uz.htm",
        "va-vih.htm", "vij-vz.htm", "wa-x.htm", "ya-yz.htm", "za-zz.htm",
    ]
    
    def __init__(self, cache_path: Optional[Path] = None):
        if cache_path is None:
            cache_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "openoccult" / "theosophical.json"
        
        self.cache_path = cache_path
        self._index: Dict[str, List[TheosophicalEntry]] = {}
        self._loaded = False
        
    def _ensure_loaded(self):
        """Load from cache if available."""
        if self._loaded:
            return
            
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    entry = TheosophicalEntry(**item)
                    key = entry.term.lower()
                    if key not in self._index:
                        self._index[key] = []
                    self._index[key].append(entry)
                    
                logger.debug(f"Loaded {len(self._index)} Theosophical terms from cache")
            except Exception as e:
                logger.error(f"Failed to load Theosophical cache: {e}")
                
        self._loaded = True
        
    def lookup(self, term: str) -> List[TheosophicalEntry]:
        """Look up a term in the glossary."""
        self._ensure_loaded()
        key = term.lower().strip()
        return self._index.get(key, [])
    
    def scrape_all(self, progress_callback=None) -> int:
        """
        Scrape all glossary pages and save to cache.
        
        Args:
            progress_callback: Optional callback(current, total, message)
            
        Returns:
            Number of entries scraped
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available for scraping")
            return 0
            
        all_entries = []
        total_pages = len(self.SECTION_PAGES)
        
        for i, page in enumerate(self.SECTION_PAGES):
            if progress_callback:
                progress_callback(i + 1, total_pages, f"Scraping {page}...")
                
            url = self.BASE_URL + page
            entries = self._scrape_page(url, page)
            all_entries.extend(entries)
            
            # Rate limit
            time.sleep(0.5)
            
        # Save to cache
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(e) for e in all_entries], f, indent=2, ensure_ascii=False)
            
        logger.info(f"Scraped {len(all_entries)} Theosophical entries")
        
        # Reload cache
        self._loaded = False
        self._index.clear()
        self._ensure_loaded()
        
        return len(all_entries)
    
    def _scrape_page(self, url: str, page_name: str) -> List[TheosophicalEntry]:
        """Scrape a single glossary page."""
        entries = []
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'IsopGem/1.0 (Esoteric Research Tool)'
            })
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: {response.status_code}")
                return entries
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all <p> tags that contain definitions
            # Pattern: Term in bold, followed by definition
            for p in soup.find_all('p'):
                text = p.get_text(separator=' ', strip=True)
                
                # Look for bold term at start
                bold = p.find('b') or p.find('strong')
                if bold:
                    term = bold.get_text(strip=True)
                    
                    # Extract language if present (in parentheses after term)
                    language = None
                    lang_match = re.search(r'\(([A-Za-z]+)\)', text[:100])
                    if lang_match:
                        lang_candidate = lang_match.group(1)
                        if lang_candidate in ('Sanskrit', 'Hebrew', 'Greek', 'Latin', 
                                             'Egyptian', 'Arabic', 'Persian', 'Pali',
                                             'Tibetan', 'Aramaic', 'Gnostic', 'Chaldean'):
                            language = lang_candidate
                    
                    # Definition is everything after the term
                    definition = text
                    
                    # Skip if too short (likely navigation)
                    if len(definition) > 50 and len(term) > 1:
                        entries.append(TheosophicalEntry(
                            term=term,
                            definition=definition[:2000],  # Truncate very long entries
                            language=language,
                            source_page=page_name
                        ))
                        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            
        return entries
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded data."""
        self._ensure_loaded()
        return {
            'total_terms': len(self._index),
            'cache_exists': self.cache_path.exists(),
        }
