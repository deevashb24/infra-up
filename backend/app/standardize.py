# backend/app/standardize.py

HINDI_MAP = {
    'सड़क': 'ROAD',
    'मार्ग': 'ROAD',
    'राजमार्ग': 'ROAD',
    'सड़क निर्माण': 'ROAD',
    'जल': 'UTILITY',
    'पाइपलाइन': 'UTILITY',
    'जल कार्य': 'UTILITY',
    'सीवर': 'UTILITY',
    'बिजली': 'UTILITY',
    'विद्युत': 'UTILITY',
    'निर्माण': 'CONSTRUCTION',
    'भवन': 'CONSTRUCTION',
    'आवास': 'CONSTRUCTION',
    'कॉम्प्लेक्स': 'CONSTRUCTION'
}

def transliterate_and_classify(title: str, raw_type: str = "") -> str:
    """
    Standardize Hindi or English raw project titles into English internal 
    Enum classifications: ROAD, UTILITY, CONSTRUCTION.
    Handles UP specific civic portals inherently returning regional scripts.
    """
    combined = f"{title} {raw_type}".lower()
    
    # 1. Check strict Hindi map mappings
    for hindi_keyword, eng_classification in HINDI_MAP.items():
        if hindi_keyword in combined:
            return eng_classification
            
    # 2. English strict fallbacks
    if any(k in combined for k in ['road', 'highway', 'street', 'expressway', 'path', 'flyover']):
        return 'ROAD'
    if any(k in combined for k in ['water', 'pipe', 'sewer', 'electric', 'power', 'cable', 'drain']):
        return 'UTILITY'
    if any(k in combined for k in ['building', 'housing', 'complex', 'plaza', 'park', 'airport']):
        return 'CONSTRUCTION'
        
    return 'CONSTRUCTION' # Default fallback

def standardize_authority(raw_authority: str) -> str:
    """
    Maps wildly scraped authority names strictly into our Database Native Enum constraints.
    """
    raw = raw_authority.upper()
    if 'SMART' in raw: return 'Smart City Lucknow'
    if 'NHAI' in raw or 'HIGHWAY' in raw: return 'NHAI'
    if 'PWD' in raw or 'PUBLIC WORKS' in raw: return 'PWD_UP'
    if 'LMC' in raw or 'MUNICIPAL' in raw or 'NAGAR NIGAM' in raw: return 'LMC'
    if 'LDA' in raw or 'LUCKNOW DEV' in raw: return 'LDA'
    if 'JAL' in raw or 'WATER' in raw or 'UPJN' in raw: return 'Jal Nigam'
    if 'UPSIDA' in raw or 'INDUSTRIAL' in raw: return 'UPSIDA'
    return 'PWD_UP' # default safely to Public Works
