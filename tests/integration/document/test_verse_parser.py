from pillars.gematria.utils.verse_parser import parse_verses


def test_parse_simple_numbered_verses():
    text = "1. In the beginning.\n2. And then more text.\n3) Final verse."
    verses = parse_verses(text)
    assert len(verses) == 3
    assert verses[0]['number'] == 1
    assert "In the beginning" in verses[0]['text']
    assert verses[1]['number'] == 2
    assert "And then more" in verses[1]['text']


def test_parse_verse_start_positions():
    text = "  1 The first.\nSome intervening text\n2- Next line\n  3) Final line"
    verses = parse_verses(text)
    assert len(verses) == 3
    # Verify that the start/end positions match substrings
    for v in verses:
        s = text[v['start']:v['end']]
        assert s.strip().startswith(str(v['number']) ) is False  # Should not start with the numeric marker
        assert s.strip() != ''


def test_inline_numbers_are_parsed():
    text = "This is text starting 1. Verse one followed by a sentence. 2. Verse two starts here. 3) And the third."
    verses = parse_verses(text)
    assert len(verses) == 3
    assert verses[0]['number'] == 1
    assert "Verse one" in verses[0]['text']
    assert verses[1]['number'] == 2
    assert "Verse two" in verses[1]['text']


def test_inline_numbers_without_punctuation():
    text = "1 First verse 2 Second verse 3 Third verse"
    verses = parse_verses(text)
    assert len(verses) == 3
    assert verses[0]['number'] == 1
    assert "First verse" in verses[0]['text']
    assert verses[2]['number'] == 3


def test_numbers_after_punctuation():
    text = "1) Sentence one.2. Sentence two here. 3) Third line"
    verses = parse_verses(text)
    assert len(verses) == 3
    assert verses[1]['number'] == 2
    assert 'Sentence two' in verses[1]['text']


def test_mid_body_numbers_not_parsed():
    text = "The star gives this number 182 and provides the seven with all they desire 7.\n2. Next verse"
    verses = parse_verses(text, allow_inline=False)
    # Only '2.' should be considered a verse marker here (and possibly 7 if it looks like a marker),
    # but the mid-body 182 should not trigger a split.
    assert any(v['number'] == 2 for v in verses)
    assert all(v['number'] != 182 for v in verses)


def test_inline_parsing_accepts_verse_markers():
    text = "1. One 2. Two 3. Three"
    verses = parse_verses(text, allow_inline=True)
    assert len(verses) == 3
    assert verses[0]['number'] == 1
    assert verses[1]['number'] == 2
    assert verses[2]['number'] == 3


def test_mid_body_numbers_not_parsed_permissive():
    text = "The star gives this number 182 and provides the seven with all they desire 7. This continues 2. Next verse"
    verses = parse_verses(text, allow_inline=True)
    # 182 should still not be recognized as a verse marker because it's mid-sentence and not followed by an uppercase word or sequential pattern
    assert all(v['number'] != 182 for v in verses)


def test_numeric_face_sum_helper():
    from pillars.gematria.utils.numeric_utils import sum_numeric_face_values
    text = "The star gives this number 182 and 7 and 1,234 in totals"
    assert sum_numeric_face_values(text) == 182 + 7 + 1234


def test_parser_reports_marker_spans():
    text = "1. First verse\n2. Second verse"
    verses = parse_verses(text)
    assert all('marker_start' in v and 'marker_end' in v for v in verses)
    assert verses[0]['marker_start'] < verses[0]['start']
    assert verses[0]['marker_end'] <= verses[0]['start']
    assert verses[0]['is_line_start'] is True
