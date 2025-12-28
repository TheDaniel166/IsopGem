"""Maat Symbols service - Egyptian degree symbols for astrology."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import re


@dataclass(slots=True)
class MaatSymbol:
    """A Maat symbol for a specific degree."""
    degree: int  # 0-359 (absolute degree)
    sign: str    # Zodiac sign name
    sign_degree: int  # 0-29 within sign
    heaven: int  # 1-7
    heaven_name: str
    text: str    # The symbolic description


# Heaven definitions with degree ranges
HEAVENS = [
    (1, "Workshop of Ptah", 0, 51),      # 0° Ari - 21° Tau
    (2, "Garden of Hathor", 52, 102),    # 22° Tau - 12° Can
    (3, "Library of Thoth", 103, 154),   # 13° Can - 4° Vir
    (4, "Arena of Horus & Set", 155, 205), # 5° Vir - 25° Lib
    (5, "Hall of Ma'at", 206, 256),      # 26° Lib - 16° Sag
    (6, "Kingdom of Osiris", 257, 308),  # 17° Sag - 8° Aqu
    (7, "Solar Barque of Ra", 309, 359), # 9° Aqu - 29° Pis
]

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ZODIAC_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def _get_heaven(abs_degree: int) -> tuple[int, str]:
    """Get heaven number and name for an absolute degree."""
    for num, name, start, end in HEAVENS:
        if start <= abs_degree <= end:
            return num, name
    return 1, "Workshop of Ptah"  # Fallback


class MaatSymbolsService:
    """Service for looking up Maat symbols by degree."""
    
    def __init__(self):
        """
          init   logic.
        
        """
        self._symbols: Dict[int, MaatSymbol] = {}
        self._load_symbols()
    
    def _load_symbols(self) -> None:
        """Load symbols from the embedded data."""
        # Parse and store all 360 symbols
        for abs_deg in range(360):
            sign_idx = abs_deg // 30
            sign_deg = abs_deg % 30
            sign = ZODIAC_SIGNS[sign_idx]
            heaven_num, heaven_name = _get_heaven(abs_deg)
            
            # Get symbol text from embedded data
            text = MAAT_SYMBOLS_DATA.get(abs_deg, "Symbol not found.")
            
            self._symbols[abs_deg] = MaatSymbol(
                degree=abs_deg,
                sign=sign,
                sign_degree=sign_deg,
                heaven=heaven_num,
                heaven_name=heaven_name,
                text=text,
            )
    
    def get_symbol(self, longitude: float) -> MaatSymbol:
        """Get the Maat symbol for a given ecliptic longitude."""
        abs_deg = int(longitude) % 360
        return self._symbols.get(abs_deg, self._symbols[0])
    
    def get_symbols_for_positions(self, positions: Dict[str, float]) -> List[tuple[str, MaatSymbol]]:
        """Get Maat symbols for a dict of planet positions."""
        result = []
        for planet, lon in positions.items():
            symbol = self.get_symbol(lon)
            result.append((planet, symbol))
        return result


# ========================================================================
# EMBEDDED MAAT SYMBOLS DATA (360 symbols)
# ========================================================================
MAAT_SYMBOLS_DATA = {
    # ARIES (0-29)
    0: "The creator god Ptah, standing in the primordial darkness, traces the first boundary of the world with a finger of pure light.",
    1: "A craftsman carves a throne from a block of meteoric iron, knowing it is destined for a king who has not yet been born.",
    2: "A stonemason strikes a flawed stone, shattering the exterior to reveal a perfect, star-like crystal at its heart.",
    3: "In a dark temple, a beam of light strikes a golden capstone, projecting the luminous blueprint of the finished structure onto the ground.",
    4: "An artist paints the eyes onto the statue of a goddess, and for a moment, the entire workshop is filled with a sense of profound beauty.",
    5: "A scribe dips his reed brush in ink, preparing to write the first hieroglyph, a symbol that will bring a new concept into existence.",
    6: "Workers on the banks of the Nile gather clay, their hands shaping the first bricks that will build a home and a nation.",
    7: "The four cornerstones of a temple are laid in a solemn ceremony, fixing the sacred structure to its place in the world forever.",
    8: "A priest blesses a newly opened quarry, anointing the rock and asking it to yield its strength for the glory of the gods.",
    9: "A worker uses a bronze saw to cut a massive cedar log, the difficult and forceful action preparing the wood for its sacred purpose as a pillar.",
    10: "A priest strikes a crystal bowl, its pure tone causing salt in a nearby dish of water to crystallize into a perfect, intricate pattern.",
    11: "The master architect holds up a golden plumb line, its simple, unwavering verticality establishing the fundamental law of the temple.",
    12: "The blacksmith quenches a red-hot sword in sacred water, the violent hiss of steam marking the containment of a great and fiery power.",
    13: "A single, polished sunstone is placed at the center of a maze, its light providing the key to navigating the winding path.",
    14: "A sheet of papyrus is unrolled, its fibers still holding the warmth of the sun, ready to receive the words of a divine decree.",
    15: "The gears of a water clock are set, their steady, rhythmic clicks marking the first measured moments of time.",
    16: "A magician cups his hands, gathering the faint light of the stars and compressing it into a solid, glowing diamond.",
    17: "The final keystone is set in an archway, and the wooden scaffolding is removed, leaving the stones to support each other in perfect unity.",
    18: "A high priest enters a newly built, silent temple and whispers a single, resonant word that awakens the spirit of the place.",
    19: "A bolt of lightning strikes the desert sand, instantly fusing it into a jagged spear of pure glass.",
    20: "On a perfectly balanced scale, a golden effigy of the sun is weighed against a silver effigy of the moon, defining the nature of duality.",
    21: "A geometer draws a complex diagram in the sand, using simple tools to map the relationship between the earth and the heavens.",
    22: "A potter takes the shards of a broken ceremonial jar and pieces them back together with seams of gold, making it more precious than before.",
    23: "A pillar of salt stands in the desert, a testament to a promise kept and a form made permanent and incorruptible.",
    24: "An explorer stands on a high cliff, drawing a circle with his outstretched arm to define the horizon of a new land to be settled.",
    25: "A priest holds a polished obsidian mirror up to the noon sun, using its reflection to project a circle of pure darkness onto a white temple wall.",
    26: "A sculptor whispers an incantation to a block of marble, which seems to soften and yield willingly to his chisel.",
    27: "A perfect, newly-forged object—a crown, a sword, a scepter—is held aloft and struck by a beam of light from the Galactic Center, transforming it from a masterwork of craft into a living artifact of cosmic destiny.",
    28: "The sacred resonance from the anointed artifact echoes through the workshop, causing all the other tools to hum with a newfound, higher purpose.",
    29: "The architect places seven different metals into a crucible, melting them together to forge a single, perfect alloy that contains the virtues of all the planets.",
    
    # TAURUS (30-59)
    30: "In a newly plowed field, a priestess plants the first seed, burying a promise of life and abundance in the fertile, consecrated earth.",
    31: "A river is diverted into a series of precisely dug channels, its life-giving water guided to create a great and flourishing city.",
    32: "A sacred bull, decorated with flowers, is led around the perimeter of a plot of land, its path consecrating the ground for a future temple.",
    33: "A massive, perfectly square foundation stone is lowered into the earth, its immense weight and stability anchoring the entire landscape.",
    34: "A botanist discovers a desert flower with five perfect petals, its form an undeniable expression of divine geometry in the natural world.",
    35: "A historian carves the final symbol of a king's legacy onto a stone tablet, completing the story and setting it for all time.",
    36: "A brewer fills a ceremonial vessel with beer, its foam settling to reveal a perfectly still surface that reflects the night sky.",
    37: "A great wall is built around a city, its purpose not to imprison, but to create a safe and sacred space for the community within.",
    38: "A tomb is sealed, its treasures and secrets protected within the living rock, waiting for a distant and future age.",
    39: "A powerful talisman is buried at the heart of a field, its magic slowly radiating outwards to ensure a bountiful harvest.",
    40: "The four canopic jars, containing the preserved organs of a pharaoh, are placed in a chest, ensuring his completeness in the afterlife.",
    41: "The architect of a great pyramid stands back to admire his work, his deep sense of satisfaction a tangible force that blesses the structure.",
    42: "A queen gazes into a polished silver mirror, not to see her own reflection, but to scry the eternal and unchanging patterns of the future.",
    43: "The doors of a great granary are sealed, its contents a guarantee of survival and a promise of life through the coming winter.",
    44: "The steady, rhythmic chant of workers pulling a great stone becomes the foundational heartbeat of the nation they are building.",
    45: "A soldier places his hand on a stone altar and swears an oath of loyalty, his words becoming as solid and binding as the rock itself.",
    46: "A sculptor carves the final detail on the face of a sphinx, capturing a timeless expression of divine mystery in stone.",
    47: "A locksmith forges a heavy bronze key, its complex design the sole means of locking a gate that separates the world of the living from the world of the gods.",
    48: "A merchant weighs a bag of gold against a single, perfect feather, establishing the principle of fair and just exchange.",
    49: "In the silent darkness of an oyster, a pearl achieves its perfect luster, a treasure created through long and patient endurance.",
    50: "A farmer places a carved stone marker at the edge of his land, its presence a clear and undisputed declaration of his stewardship.",
    51: "The final capstone is placed on a great obelisk, its gilded tip catching the first ray of the morning sun and announcing the completion of a great work.",
    52: "The first vine begins to grow on the wall of a newly built temple, its green leaves a soft counterpoint to the hard stone.",
    53: "A priestess anoints a statue of a god with fragrant lotus oil, the scent filling the air and awakening a sense of devotion.",
    54: "A procession of musicians enters the city gates, their drums and sistrums announcing the beginning of a joyous festival.",
    55: "A woman weaves a tapestry depicting the bounty of the land, her hands translating the beauty of nature into art.",
    56: "Two lovers meet in a hidden garden at twilight, their shared silence a bond more powerful than words.",
    57: "A scribe, having finished a serious text, now draws a playful cat in the margins of the papyrus.",
    58: "A child laughs as she chases a flock of ibis along the banks of the Nile, her joy a simple, perfect prayer.",
    59: "A feast is laid out on woven mats, the abundance of dates, figs, and bread a testament to the generosity of the land.",
    
    # GEMINI (60-89)
    60: "Two children sit by the river, teaching each other a new song, their voices blending in simple harmony.",
    61: "A messenger delivers a love letter, its words a bridge connecting two hearts separated by distance.",
    62: "A troupe of acrobats and dancers performs in the village square, their movements telling a story of the gods without a single word.",
    63: "A woman looks at her own reflection in a polished copper mirror, adorning herself with turquoise jewelry not for vanity, but for the joy of beauty.",
    64: "Two merchants, after a long day of haggling, share a cup of beer and a story, their rivalry forgotten in a moment of camaraderie.",
    65: "A priest of Thoth and a priestess of Hathor debate the nature of creation, one with logic and one with poetry, finding they are speaking of the same truth.",
    66: "A flock of sacred geese flies overhead, their honking calls a familiar and comforting sound to the people below.",
    67: "A young couple exchanges faience rings, their simple, handmade vows the foundation of a new family.",
    68: "A storyteller captivates an audience with a tale of magic and adventure, their shared imagination creating a world within the world.",
    69: "A traveler learns a simple greeting in a foreign tongue, allowing him to connect with the people of a strange new city.",
    70: "A beekeeper gently gathers honey from a hive, his calm and respectful presence a pact with the wild creatures.",
    71: "A group of women gathers by the river to wash laundry, their chatter and laughter a vital part of the community's social fabric.",
    72: "A gardener grafts a branch from a sweet fig tree onto a wild one, creating a new and more perfect fruit.",
    73: "A musician discovers that two different notes played on his lyre create a beautiful and pleasing harmony.",
    74: "A priestess of Isis finds a lost child in the marketplace and gently returns him to his mother's arms.",
    75: "A diplomat from a foreign land is welcomed with a feast, the sharing of food a universal language of peace.",
    76: "A cat curls up to sleep in the sun at the foot of a great statue, a small, living comfort in the presence of the divine.",
    77: "A farmer and a boatman make a trade, exchanging grain for fish in a simple act of mutual reliance.",
    78: "A woman plants a garden of fragrant flowers, her intention not just to create beauty, but to attract the blessings of the gods.",
    79: "A young scribe is taught to write his own name for the first time, a moment of profound self-realization.",
    80: "Two friends sit in comfortable silence, their long-standing affection needing no words.",
    81: "A dancer ties a series of small bells to her ankle, their sound adding a new layer of magic to her movements.",
    82: "A parrot in a cage perfectly mimics the voice of its owner, a strange and wonderful connection between two different kinds of beings.",
    83: "A perfumer blends myrrh and frankincense, creating a scent that will be used to consecrate a sacred space.",
    84: "A game of senet is played between two rivals, the roll of the dice a reminder that even in strategy, there is always an element of chance.",
    85: "A rumor of a miracle passes through a crowd, transforming the mood of the city from despair to hope.",
    86: "A mirror is positioned in a tomb to reflect the light of the rising sun on one day of the year, a message of rebirth sent across time.",
    87: "A priest deciphers a confusing passage in a sacred text by realizing it is not a narrative, but a poem.",
    88: "Two separate irrigation canals are linked, allowing two different communities to share the life-giving water of the Nile.",
    89: "A garland of blue lotus flowers is woven, its beauty destined to be offered at a temple and then fade, a lesson in impermanence.",
    
    # CANCER (90-119)
    90: "A mother swaddles her newborn child, creating a safe and sacred space for a new soul in the world.",
    91: "A family gathers on the roof of their home to watch the stars, their shared sense of wonder a quiet, binding ritual.",
    92: "A priest carefully tends the sacred flame in the heart of a temple, ensuring it is never extinguished.",
    93: "A farmer builds a mud-brick wall around his family's first home, defining the boundary between the world and their private sanctuary.",
    94: "A woman hums a lullaby that her grandmother sang to her, passing a legacy of comfort down through the generations.",
    95: "A fisherman offers the first catch of the day back to the river, a gesture of gratitude that ensures future abundance.",
    96: "A chest is carved from cedar wood, its purpose to hold and protect the precious, everyday objects of a family's life.",
    97: "A high priestess performs a scrying ritual with a bowl of water, seeking to understand the hidden currents of the future.",
    98: "A family shares a meal in silence, their deep, unspoken connection filling the room.",
    99: "An amulet of the goddess Taweret, the protector of mothers, is placed above the door of a home.",
    100: "A memory of a loved one who has passed brings a sad, sweet smile to a woman's face.",
    101: "The annual flooding of the Nile arrives, its waters a familiar and welcome promise of renewal for the entire land.",
    102: "A child buries a seed in the dark, wet earth, having faith that it will grow into something beautiful.",
    103: "A priestess of Isis carefully preserves a collection of old, treasured family stories by writing them down for the first time.",
    104: "A royal architect unrolls a papyrus showing the blueprints for a new temple, its design a perfect expression of sacred geometry.",
    105: "A judge consults a scroll containing the foundational laws of the kingdom to ensure his ruling is fair and just.",
    106: "A young apprentice, after years of study, finally learns to read the most ancient and sacred hieroglyphs.",
    107: "A star-gazer in a temple observatory makes a new mark on a celestial map, recording the slow, eternal dance of the heavens.",
    108: "A healer consults a medical text, finding the precise recipe for a remedy that will save a life.",
    109: "A mother teaches her child the names of the gods and goddesses, a lesson that is the foundation of all other knowledge.",
    110: "A secret message is passed between two priests, its meaning hidden from the uninitiated by a clever cipher.",
    111: "A historian discovers a hidden chamber containing a lost king's records, bringing a forgotten chapter of history back to light.",
    112: "A poet composes a hymn of praise to Thoth, his words carefully chosen to reflect the perfection of the divine order.",
    113: "A teacher uses a simple story about the river to explain a complex and profound cosmic truth to his students.",
    114: "A treaty of peace between two warring nations is written and sealed, its words a magical barrier against future conflict.",
    115: "A librarian carefully tends to his scrolls, treating them not as objects, but as living vessels of knowledge.",
    116: "A magician draws a protective circle in the sand, speaking the secret names of the guardians of the four directions.",
    117: "A genealogist uncovers a link between a commoner and an ancient royal line, revealing a hidden nobility.",
    118: "A prophecy is spoken, its cryptic words setting in motion a chain of events that will unfold over generations.",
    119: "A debate takes place between two scribes, their respectful disagreement sharpening the understanding of a difficult sacred text.",
    
    # LEO (120-149)
    120: "A king, speaking with the authority of the gods, issues a decree that will bring order and prosperity to his entire kingdom.",
    121: "A master craftsman signs his name to a finished statue, a proud and public declaration of his creative power.",
    122: "A royal storyteller performs the grand epic of the sun god's journey, his charismatic performance making the ancient myth feel alive and present.",
    123: "The heart of a pharaoh is placed on a scale, its virtues and deeds the only testament he can offer in the hall of judgment.",
    124: "A champion, confident in his strength and purpose, issues a bold challenge to his rivals.",
    125: "A high priest stands before the temple doors at dawn, his arms raised to welcome the first, life-giving rays of the sun.",
    126: "A royal decree, written in gold ink, is read aloud in the city square, its authority absolute and unquestioned.",
    127: "A child, playing, pretends to be a great pharaoh, instinctively acting out a role of power and nobility.",
    128: "An actor on a festival stage wears a golden mask of the sun god, for a time becoming a vessel for the divine presence.",
    129: "A king pardons a penitent enemy, his act of magnanimous mercy demonstrating the true nature of his power.",
    130: "The coronation of a new pharaoh takes place, a ceremony that transforms a mortal man into a living god.",
    131: "A great lion, resting in the shade, watches over the desert, its calm and powerful presence a symbol of natural royalty.",
    132: "A master goldsmith crafts a radiant pectoral for the pharaoh, its design a celebration of the sun's eternal glory.",
    133: "A charismatic leader gives a speech that fills his followers with courage and a powerful sense of shared purpose.",
    134: "A king refuses to listen to the advice of his vizier, certain in the absolute correctness of his own judgment.",
    135: "The grand procession of a pharaoh passes through the city, the sheer spectacle of his wealth and power inspiring awe in all who watch.",
    136: "A single, perfect sunflower in a field turns its face to follow the journey of the sun across the sky.",
    137: "A royal herald announces the birth of a prince, his voice carrying the promise of the kingdom's continuity.",
    138: "A game is won not by a clever trick, but by a bold and decisive move that takes all opponents by surprise.",
    139: "A king orders a great monument to be built, not for the gods, but to ensure that his own name and legacy will live forever.",
    140: "An offering of pure gold is made at a temple, a gift worthy of the gods' splendor.",
    141: "A performer on a stage holds the entire audience captive with a dramatic and heartfelt monologue.",
    142: "A king, surveying his lands from a high balcony, feels a deep and abiding pride in the kingdom he rules.",
    143: "A hero, having completed his quest, returns not in secret, but in a grand triumphal parade.",
    144: "A seal bearing the personal sigil of the pharaoh is pressed into hot wax, marking a document with his undeniable authority.",
    145: "A ray of sunlight penetrates a dark tomb, illuminating a hieroglyph that reveals the secret name of the king buried within.",
    146: "A court historian writes the official history of a great battle, his narrative focusing on the glorious and noble deeds of the king.",
    147: "In the great library of Thoth, a triumphant king, reading the history of his own glorious victories, is suddenly struck by a beam of light from the Galactic Center.",
    148: "A scribe, inspired by the king's revelation, begins to write a new book, not of history, but of prophecy.",
    149: "The laws of the kingdom are re-written, their foundation shifting from the king's authority to a higher, divine principle.",
    
    # VIRGO (150-179)
    150: "A priestess meticulously cleans and organizes a temple shrine, her small, humble actions a prayer of devotion.",
    151: "A physician grinds herbs with a pestle and mortar, his precise and patient work transforming simple plants into a powerful medicine.",
    152: "An apprentice scribe practices his hieroglyphs for hours, striving for the perfect form in every single character.",
    153: "A farmer carefully sorts his seeds, separating the best ones to ensure the purity and strength of the next harvest.",
    154: "A weaver inspects her cloth for a single flawed thread, knowing that the strength of the whole depends on the integrity of each part.",
    155: "A military strategist analyzes a map, his careful and precise placements of troop markers a vital preparation for the coming battle.",
    156: "A royal physician works tirelessly to identify the source of a strange plague, his methodical search a battle against an unseen enemy.",
    157: "An armorer meticulously inspects a chariot, ensuring every pin and leather strap is perfect before it is sent to the field of war.",
    158: "A priest of Horus confronts a priest of Set in a theological debate, using logic and sacred texts as his weapons.",
    159: "A farmer builds a series of dikes and canals to protect his fields from the unpredictable and destructive power of the river's flood.",
    160: "A scout returns from a dangerous mission with a detailed report of the enemy's position, his accurate information a critical advantage.",
    161: "A judge sifts through contradictory testimony, his patient analysis a struggle to separate truth from falsehood.",
    162: "A trainer works with a young, wild falcon, his patient and disciplined approach slowly turning its chaotic energy into focused purpose.",
    163: "A list of grievances is carefully written before being presented to the pharaoh, transforming a chaotic mob into a legitimate political body.",
    164: "A military scribe records the events of a battle, his account focused not on glory, but on the practical successes and failures of strategy.",
    165: "A weapon is sharpened on a whetstone, the slow, abrasive process preparing the blade for a moment of swift, decisive action.",
    166: "A fortress is built on a contested border, its very existence a clear and defiant statement of sovereignty.",
    167: "A spy deciphers a coded message, his mental acuity foiling the enemy's secret plans.",
    168: "A general, after a great victory, insists on a full accounting of the army's remaining supplies, knowing that discipline is the key to future success.",
    169: "A wild desert storm erodes a poorly built wall, revealing the weakness of its construction.",
    170: "A duel is fought not with swords, but with a game of senet, the outcome determining the fate of a great inheritance.",
    171: "A moment of doubt in a commander's heart is overcome by a renewed focus on the justice of his cause.",
    172: "A rebellion is quelled not by force, but by a royal decree that addresses the legitimate complaints of the people.",
    173: "A wild desert oasis, a place of chaos and life, is claimed and cultivated, becoming an orderly and productive garden.",
    174: "A flaw is discovered in a battle plan, forcing the generals to adapt and create a new, more resilient strategy.",
    175: "A single soldier holds a narrow pass against a superior force, his courage turning a tactical disadvantage into a legendary victory.",
    176: "A truce is called on the battlefield, allowing both sides to tend to their wounded.",
    177: "A diplomat, seeking to end a war, proposes a treaty that offers a fair and honorable compromise to both sides.",
    178: "A monument is erected on a former battlefield, its purpose to commemorate not the victory, but the peace that followed.",
    179: "Two rival gods, after a long and bitter struggle, agree to rule their respective domains in a state of balanced opposition.",
    
    # LIBRA (180-209)
    180: "The goddess Ma'at holds her scales, the perfect, unwavering balance of the empty pans a symbol of absolute justice.",
    181: "A marriage is arranged between the children of two rival chieftains, their union a living treaty of peace.",
    182: "A judge places a single white feather on one side of a scale, the ultimate standard against which all hearts will be weighed.",
    183: "A beautiful and harmonious chord is played on a lyre, its notes a perfect resolution to a piece of tense and dramatic music.",
    184: "A border dispute is settled by a diplomat who carefully redraws the map in a way that satisfies the honor of both kingdoms.",
    185: "A craftsman designs a pectoral ornament with perfect symmetry, its beauty derived from its exquisite balance.",
    186: "A law is written that applies equally to the noble and the commoner, establishing the principle of justice for all.",
    187: "Two architects collaborate on a design, their different ideas blending to create a building more beautiful than either could have imagined alone.",
    188: "A poem is written in which every line has a corresponding and balancing counterpart.",
    189: "A king, faced with a difficult decision, consults his wife, their partnership the source of his wisest counsel.",
    190: "A peace offering of great beauty is sent from one kingdom to another, a gesture intended to heal a past grievance.",
    191: "A social gathering is held, its success dependent on the host's skill in introducing the right people to one another.",
    192: "A dancer and her shadow move in perfect synchrony, creating a performance of haunting beauty.",
    193: "A difficult negotiation is resolved when one side makes a graceful concession, allowing the other to save face.",
    194: "A mirror is placed opposite a window in a dark room, its reflection filling the space with balanced, indirect light.",
    195: "A verdict of acquittal is given, the accused being declared in perfect balance with the law of Ma'at.",
    196: "A gardener prunes a rose bush, his careful cuts creating a more beautiful and well-balanced plant.",
    197: "An alliance is formed, the strengths of one partner perfectly compensating for the weaknesses of the other.",
    198: "A piece of music resolves its final, lingering dissonance into a chord of pure, satisfying harmony.",
    199: "A choice is made to forgive an old enemy, not for their sake, but to restore one's own inner peace.",
    200: "A trade agreement is signed, its terms ensuring mutual prosperity for both nations.",
    201: "A beautiful and intricate knot is tied, its stability dependent on the equal tension of all its parts.",
    202: "A judge in a dispute declares that both parties are partially right and partially wrong, and orders them to find a middle way.",
    203: "A moment of perfect, serene stillness is found in a beautifully proportioned temple garden.",
    204: "A social rule of etiquette is observed, its purpose to ensure that all interactions are graceful and respectful.",
    205: "The two pillars of a great temple gate stand as equals, their shared strength creating a passage to the sacred space within.",
    206: "A soul, entering the Hall of Judgment, takes a deep breath and makes a declaration of innocence, its words echoing in the vast, silent space.",
    207: "The forty-two divine assessors, who witness the weighing of the heart, are present not as accusers, but as silent embodiments of the universal law.",
    208: "A feather of Ma'at is plucked from her headdress, its weight so infinitesimal it seems to float, yet it is the measure of a soul's entire existence.",
    209: "An offering of clear, pure water is placed on an altar, its transparency a symbol of a life lived with nothing to hide.",
    
    # SCORPIO (210-239)
    210: "The heart of the deceased is removed and placed on the great golden scale, a moment of profound and terrifying truth.",
    211: "Ammit, the devourer of souls, waits patiently by the scales, her presence a stark reminder of the consequences of a life lived out of balance.",
    212: "Thoth, the divine scribe, stands ready with his palette and reed brush, prepared to record the final, unalterable verdict.",
    213: "The scale tips, ever so slightly, revealing a hidden burden of guilt that the soul had long since forgotten.",
    214: "A soul, seeing its own heart weighed, is overcome with a flood of memories, understanding for the first time the true import of its every past action.",
    215: "A secret shame is brought to light in the Hall of Ma'at, not for punishment, but so that its power can finally be dissolved by the truth.",
    216: "The scale holds in perfect balance, the heart as light as the feather, a moment of supreme and silent vindication.",
    217: "A soul is judged not on its worldly successes, but on the hidden kindnesses it showed when no one was watching.",
    218: "An act of profound betrayal, long hidden, causes the great scale to shudder and groan.",
    219: "Thoth records the verdict, his inscription not merely a record, but the very act that makes the soul's fate a reality.",
    220: "A soul, having been judged worthy, is led by Horus towards the blessed fields of Aaru, leaving the Hall of Judgment behind forever.",
    221: "An old, inherited curse is broken by a single act of selfless courage, its power nullified in the presence of Ma'at.",
    222: "The great scale is meticulously cleaned and recalibrated after each judgment, ensuring its perfect impartiality for the next soul.",
    223: "A soul confesses a hidden crime, and this act of honest self-assessment lightens the heart upon the scale.",
    224: "The gods do not speak; the verdict is revealed only by the silent, inexorable movement of the scale.",
    225: "A life of quiet, humble integrity is shown to weigh more than a life of celebrated but selfish glory.",
    226: "A soul, having been devoured by Ammit, is utterly unmade, its existence erased from the cosmic record.",
    227: "A single, perfect tear of remorse falls from the eye of a soul, its weight mysteriously lightening the heart on the scale.",
    228: "The laws of Ma'at are not carved in stone for all to see; they are woven into the very fabric of the silent, star-filled ceiling of the Hall.",
    229: "A life of great suffering, endured with grace, is revealed to have purified the heart, making it lighter than the feather.",
    230: "The concept of 'fairness' is revealed not as a human invention, but as a fundamental, structural law of the cosmos.",
    231: "A soul understands that it is not being judged by the gods, but by the truth of its own life.",
    232: "An oath, sworn in life and faithfully kept, adds a golden sheen to the heart as it sits upon the scale.",
    233: "The silence in the Hall of Ma'at is absolute, a presence so powerful it dissolves all lies and illusions.",
    234: "A soul is shown a vision of the ripples of consequence that flowed from its every choice, spreading through generations.",
    235: "The shadow-self is acknowledged and integrated, its hidden truths no longer a burden on the heart.",
    236: "A final, binding judgment is passed, its cosmic resonance setting the course for the soul's next incarnation.",
    237: "A truth is revealed that is so profound it re-contextualizes a soul's entire life, turning seeming sins into necessary lessons.",
    238: "The gates of the underworld swing open, their movement governed not by force, but by the verdict of the scale.",
    239: "A soul, finally free from the burdens of its past, experiences a moment of pure, unadulterated peace.",
    
    # SAGITTARIUS (240-269)
    240: "A soul, declared 'true of voice,' is given a glimpse of the cosmic map, showing the path its journey will now take across the heavens.",
    241: "An arrow, loosed from a divine bow, flies straight and true towards a distant, unseen target.",
    242: "A philosopher, gazing at the stars, suddenly understands a universal law that connects all living things.",
    243: "A horse, wild and free, gallops across the open desert, a living embodiment of untamed spirit and forward momentum.",
    244: "A teacher points to a constellation, telling his students the ancient story of its meaning and purpose.",
    245: "A great library of Alexandria is envisioned, a place where all the knowledge of the world can be gathered for the betterment of humanity.",
    246: "A difficult truth is spoken in a king's court, not as a challenge, but as a necessary piece of guidance.",
    247: "A traveler on a long pilgrimage feels a surge of renewed faith as he sees the distant shape of his sacred destination.",
    248: "A law is passed that grants new freedoms to the people, expanding the boundaries of their world.",
    249: "A prophecy is not about a fixed doom, but reveals the path one must take to achieve a higher destiny.",
    250: "A ship is built, its tall mast pointing to the stars, its purpose to explore the unknown waters beyond the horizon.",
    251: "A university is founded, its central principle the free and open pursuit of knowledge.",
    252: "A moment of sudden, intuitive understanding solves a problem that logic alone could not crack.",
    253: "A wild, foreign custom is observed and understood, broadening the observer's perspective of the world.",
    254: "The constitution of a nation is written, its abstract principles the guiding light for all future laws.",
    255: "A great beacon is lit on a high hill, its light a signal of hope and guidance for those lost in the wilderness.",
    256: "A leap of faith is taken, an action based not on what is known, but on a powerful belief in a positive outcome.",
    257: "A soul, guided by Anubis, stands before the great stone gates of the underworld, taking its first step from the world of light into the realm of shadow.",
    258: "A map of the Duat is studied, its winding paths and guarded gates a spiritual geography that must be navigated with wisdom and courage.",
    259: "A ferryman poles his silent boat across a subterranean river, its dark waters separating the land of the living from the land of the dead.",
    260: "A series of magical spells from the Book of the Dead are recited, their words a passport and a protection for the soul on its perilous journey.",
    261: "A torch is lit, its flame pushing back the oppressive darkness of a tomb and revealing a path that leads ever deeper.",
    262: "The soul is challenged by a gatekeeper with a riddle, and only a true and wise answer will allow passage.",
    263: "A vision of one's own funeral is witnessed, a necessary detachment from the life that has been left behind.",
    264: "A guide explains that in the underworld, the stars are not above, but below, their light shining up from the depths.",
    265: "The soul recognizes a familiar face among the blessed dead, a comforting reminder that it is not alone on its journey.",
    266: "A moment of profound understanding dawns: the journey through the underworld is not a punishment, but a necessary purification.",
    267: "Standing in the deepest part of the Duat, the soul looks up and sees not a ceiling of rock, but a direct, shimmering portal to the Galactic Center.",
    268: "Having glimpsed the cosmic truth, the soul is now guided by an inner star, no longer needing the map to find its way.",
    269: "A great serpent is encountered, its act of shedding its skin a living lesson in rebirth and transformation.",
    
    # CAPRICORN (270-299)
    270: "The soul stands before Osiris, enthroned in the Hall of Two Truths, his silent, mummified form a symbol of the laws that govern death and rebirth.",
    271: "The soul is tested by being asked to plow a field in the underworld, its ability to create life in the land of the dead a measure of its power.",
    272: "A great, heavy stone door, which can only be opened from the inside, seals a chamber of transformation.",
    273: "The soul is shown the immutable architecture of the underworld, its structure as real and enduring as any mountain.",
    274: "A ritual of dismemberment is undergone, the soul's old form taken apart so it can be reassembled in a new and more perfect way.",
    275: "The soul is judged on its ability to remember its own secret name, the core of its eternal identity.",
    276: "A field of reeds in the afterlife, the Field of Aaru, is cultivated with the same care and discipline as a field on Earth.",
    277: "The soul is given a new body of light, a Sahu, its form no longer subject to decay.",
    278: "The heart, once weighed, is returned to the soul, its preserved memories now a source of wisdom rather than a burden.",
    279: "A great and ancient fear of the dark is confronted and overcome.",
    280: "The soul is shown the great cosmic cycles of death and rebirth, understanding its own journey as a single, necessary note in an eternal song.",
    281: "A pact is made with the ancestors, their collective wisdom now a source of guidance and strength.",
    282: "The soul is given a position of responsibility in the kingdom of Osiris, its earthly skills put to use in the afterlife.",
    283: "A moment of profound stillness and silence is experienced, a state of being that is the ultimate source of all power.",
    284: "The soul understands that the rigid laws of the underworld are not a prison, but a framework that makes resurrection possible.",
    285: "A demon is faced and subdued not by force, but by a calm and unwavering refusal to give in to fear.",
    286: "The soul is shown the mummified seed of a grain of wheat, a potent symbol of life preserved through death.",
    287: "A great library in the underworld is discovered, containing the life stories of every soul that has ever lived.",
    288: "The soul is granted the ability to travel between the world of the living and the world of the dead, becoming a bridge between realms.",
    289: "A drink is taken from the Pool of Memory, and the soul recalls all of its past incarnations.",
    290: "The soul joins the eternal crew of the solar barque, its new duty to help the sun god fight the forces of darkness each night.",
    291: "A new, divine purpose is accepted, one that will be carried into the next life.",
    292: "The soul realizes that the underworld is not a place of sorrow, but a place of profound and structured peace.",
    293: "A community of blessed souls works together to maintain the order and beauty of the afterlife.",
    294: "The soul is shown a vision of the future, understanding its role in the great, unfolding cosmic plan.",
    295: "A new star appears in the sky of the Duat, marking the successful transformation of a soul.",
    296: "The soul understands that its individual consciousness is a part of a much larger, collective whole.",
    297: "The boundaries between self and other begin to dissolve in the face of a universal, divine truth.",
    298: "A final gift of wisdom is received from Osiris before the soul prepares to depart his kingdom.",
    299: "The soul is led to the final gate of the underworld, which opens not into darkness, but into a flood of pure, cool light.",
    
    # AQUARIUS (300-329)
    300: "The soul is bathed in the life-giving waters of the celestial Nile, its old wounds and sorrows washed away in a baptism of cosmic renewal.",
    301: "A breath of fresh, celestial air is taken, the first breath of a new and liberated existence.",
    302: "The soul is given a new name, one that reflects its transformed, divine nature.",
    303: "A vision is granted of the interconnected web of all life, seeing the universe not as a collection of separate things, but as a single, living being.",
    304: "The soul joins a chorus of celestial beings, its individual voice blending into a universal, harmonious song.",
    305: "A familiar human emotion is felt, but from a new, detached perspective, understanding its purpose in the cosmic design.",
    306: "The soul is shown how a single, selfless act in its past life created waves of positive change that continue to spread through the world.",
    307: "The concept of 'self' expands to include the entire community of humanity, past, present, and future.",
    308: "The soul stands on the threshold between the eternal realm and the world of form, ready and willing to be reborn.",
    309: "The reborn soul takes its place as a rower on the solar barque of Ra, its new duty to help power the journey of the sun across the sky.",
    310: "A new star is charted by celestial navigators, its light a beacon for all the souls traveling in the fleet of the sun god.",
    311: "The crew of the solar barque works in perfect, silent unison, their shared purpose a bond stronger than any oath.",
    312: "A being of pure light explains a complex cosmic law to the soul, the knowledge received not through words but through direct, intuitive understanding.",
    313: "The solar barque passes a constellation shaped like a key, a reminder that the secrets of the universe are unlocked through shared wisdom.",
    314: "The soul sees the Earth from a great distance, its old life now appearing as a beautiful, intricate pattern in a vast cosmic design.",
    315: "A gift of pure energy is given freely from one soul to another to help it overcome a moment of cosmic weariness.",
    316: "The soul helps to defend the solar barque against Apep, the serpent of chaos, not with force, but with a song of pure, unwavering light.",
    317: "A council of enlightened beings is held, their thoughts blending to solve a problem that affects the entire galaxy.",
    318: "The soul understands that its true home is not a place, but the community of conscious beings traveling together through eternity.",
    319: "A new, more advanced form of consciousness is born from the collective mind of the barque's crew.",
    320: "The light of the sun god Ra illuminates a dark and forgotten corner of the cosmos, bringing it back into the fold of creation.",
    321: "The soul is shown how to build a chariot of pure thought, capable of traveling to any reality it can imagine.",
    322: "A wave of divine grace, emanating from the heart of Ra, washes over the crew, renewing their strength and purpose.",
    323: "The soul looks ahead and sees an infinite number of other solar barques, each on its own journey, all part of one great celestial fleet.",
    324: "A universal truth is understood: that to serve the whole is the highest and most joyful form of freedom.",
    325: "The boundaries between individual souls on the barque begin to soften, their thoughts and energies flowing together in a luminous stream.",
    326: "A future incarnation is chosen not for personal gain, but for the role that will best serve the evolution of the cosmos.",
    327: "The soul pours its own light into the great lantern at the prow of the ship, contributing its essence to the navigation of the whole.",
    328: "A perfect, silent understanding passes between the soul and the sun god Ra, a communion beyond all form and language.",
    329: "The very concept of a separate, individual journey is replaced by the joy of being part of a universal, divine current.",
    
    # PISCES (330-359)
    330: "The solar barque reaches the edge of the known cosmos and sails into the primordial, starless ocean of Nun, the source of all things.",
    331: "The solid form of the celestial boat begins to dissolve, its substance returning to the cosmic waters.",
    332: "Individual memories of past lives are offered to the great ocean, becoming part of the universal dream.",
    333: "A song is sung, not by any single voice, but by the gentle, rhythmic lapping of the cosmic waters themselves.",
    334: "A feeling of profound empathy is experienced for all beings who have ever suffered, their sorrows washed clean in the waters of Nun.",
    335: "The last star of the old universe fades, its light reabsorbed into the infinite potential of the void.",
    336: "A sacrifice is made, not of a thing, but of the very idea of self, a willing surrender to the great cosmic whole.",
    337: "A dream is dreamt by the sleeping cosmos, a dream that contains the seed of the next universe.",
    338: "A single, perfect tear of compassion, containing the memory of all creation, falls into the primordial sea.",
    339: "The distinction between the inner world and the outer world vanishes completely.",
    340: "A soul, now formless, becomes a guardian of a sacred spring in the heart of the cosmic ocean.",
    341: "A prayer is answered before it is even spoken, a testament to the perfect unity of all things.",
    342: "A lost story, a forgotten god, a faded memory—all are found, safe and whole, in the gentle depths of Nun.",
    343: "The soul experiences a state of pure, unconditional love for all that has been, all that is, and all that will ever be.",
    344: "A great, cosmic tide pulls all things toward a silent, invisible center.",
    345: "A promise is made to return to the world of form when the time is right, not out of duty, but out of love.",
    346: "The last illusion, the fear of being forgotten, dissolves into a state of perfect peace.",
    347: "A piece of divine music is heard, its melody the source code for the next creation.",
    348: "The soul becomes a drop of water in the infinite ocean, retaining its essence while being part of the whole.",
    349: "A final act of forgiveness is offered to all beings, including oneself, erasing the last karmic trace.",
    350: "A state of pure, dreamlike sanctuary is entered, a cosmic womb where all things are nurtured before their birth.",
    351: "The very laws of reality become fluid and poetic, their logic replaced by a deeper, more mysterious truth.",
    352: "A message of hope is encoded into the cosmic waters, a message that will be found by the first souls of the next universe.",
    353: "The last boundary, the one between life and death, is seen to be a beautiful, shimmering illusion.",
    354: "A deep and profound cosmic weariness is finally allowed to rest.",
    355: "A story ends, its moral absorbed into the consciousness of the universe, ready to be told again in a new form.",
    356: "The final, silent mantra is uttered: 'All is one.'",
    357: "A state of pure potential is reached, a fertile void containing all possibilities.",
    358: "The last ripple on the surface of the cosmic ocean becomes perfectly still.",
    359: "The absolute end, which is also the absolute beginning. Silence.",
}