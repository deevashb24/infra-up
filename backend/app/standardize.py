# backend/app/standardize.py
from .models import AuthorityEnum, ProjectTypeEnum

HINDI_MAP = {
    'सड़क': ProjectTypeEnum.ROAD,
    'मार्ग': ProjectTypeEnum.ROAD,
    'राजमार्ग': ProjectTypeEnum.ROAD,
    'सड़क निर्माण': ProjectTypeEnum.ROAD,
    'जल': ProjectTypeEnum.UTILITY,
    'पाइपलाइन': ProjectTypeEnum.UTILITY,
    'जल कार्य': ProjectTypeEnum.UTILITY,
    'सीवर': ProjectTypeEnum.UTILITY,
    'बिजली': ProjectTypeEnum.UTILITY,
    'विद्युत': ProjectTypeEnum.UTILITY,
    'निर्माण': ProjectTypeEnum.CONSTRUCTION,
    'भवन': ProjectTypeEnum.CONSTRUCTION,
    'आवास': ProjectTypeEnum.CONSTRUCTION,
    'कॉम्प्लेक्स': ProjectTypeEnum.CONSTRUCTION,
}

def transliterate_and_classify(title: str, raw_type: str = "") -> ProjectTypeEnum:
    """
    Standardise Hindi or English raw project titles into internal ProjectTypeEnum values.
    FIX #6: Returns enum members directly, not plain strings, so SQLAlchemy never
    receives a type-mismatched value.
    """
    combined = f"{title} {raw_type}".lower()

    # 1. Check Hindi map
    for hindi_keyword, enum_val in HINDI_MAP.items():
        if hindi_keyword in combined:
            return enum_val

    # 2. English fallbacks
    if any(k in combined for k in ['road', 'highway', 'street', 'expressway', 'path', 'flyover']):
        return ProjectTypeEnum.ROAD
    if any(k in combined for k in ['water', 'pipe', 'sewer', 'electric', 'power', 'cable', 'drain']):
        return ProjectTypeEnum.UTILITY
    if any(k in combined for k in ['building', 'housing', 'complex', 'plaza', 'park', 'airport']):
        return ProjectTypeEnum.CONSTRUCTION

    return ProjectTypeEnum.CONSTRUCTION  # Default fallback


def standardize_authority(raw_authority: str) -> AuthorityEnum:
    """
    Maps scraped authority names to AuthorityEnum members.
    FIX #6: Returns actual enum members so SQLAlchemy Enum columns never get
    a plain string that might fail a LookupError on insert.
    """
    raw = raw_authority.upper()
    if 'SMART' in raw:
        return AuthorityEnum.SMART_CITY
    if 'NHAI' in raw or 'HIGHWAY' in raw:
        return AuthorityEnum.NHAI
    if 'PWD' in raw or 'PUBLIC WORKS' in raw:
        return AuthorityEnum.PWD_UP
    if 'LMC' in raw or 'MUNICIPAL' in raw or 'NAGAR NIGAM' in raw:
        return AuthorityEnum.LMC
    if 'LDA' in raw or 'LUCKNOW DEV' in raw:
        return AuthorityEnum.LDA
    if 'JAL' in raw or 'WATER' in raw or 'UPJN' in raw:
        return AuthorityEnum.JAL_NIGAM
    if 'UPSIDA' in raw or 'INDUSTRIAL' in raw:
        return AuthorityEnum.UPSIDA
    if 'UPLCL' in raw:
        return AuthorityEnum.UPLCL
    return AuthorityEnum.PWD_UP  # Default
