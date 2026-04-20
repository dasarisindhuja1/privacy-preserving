"""
Regex-based PII detection for structured data patterns.
Detects emails, phone numbers, credit cards, Aadhaar, PAN, passwords, etc.
"""

import re
from typing import Dict, List
from enum import Enum


class PIIType(Enum):
    """Enumeration of PII types we detect."""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    AADHAAR = "AADHAAR"  # 12-digit Indian ID
    PAN = "PAN"  # Personal Account Number (India)
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    IP_ADDRESS = "IP_ADDRESS"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    PASSWORD = "PASSWORD"
    API_KEY = "API_KEY"
    SSN = "SSN"  # Social Security Number (US)


class RegexDetector:
    """
    Regex-based PII detector for pattern-matching common PII formats.
    """
    
    def __init__(self):
        """Initialize regex patterns for various PII types."""
        self.patterns = {
            PIIType.EMAIL: re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            ),
            
            PIIType.PHONE: re.compile(
                r'\b(?:\+91[\-\s]?|0)?[6-9]\d{9}\b|'   # India (strict 10-digit starting 6-9)
                r'\b(?:\+1[\-\s]?)?(?:\([2-9]\d{2}\)|[2-9]\d{2})[\-\s]?\d{3}[\-\s]?\d{4}\b'  # US (valid area code)
            ),
            
            PIIType.AADHAAR: re.compile(
                r'\b\d{4}\s?\d{4}\s?\d{4}\b'  # 12 digits in groups (Aadhaar format)
            ),
            
            PIIType.PAN: re.compile(
                r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'  # PAN format: AAAAA0000A
            ),
            
            PIIType.CREDIT_CARD: re.compile(
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|'  # Visa
                r'5[1-5][0-9]{14}|'  # Mastercard
                r'3[47][0-9]{13})\b'  # American Express
            ),
            
            PIIType.DEBIT_CARD: re.compile(
                r'\b(?:6011[0-9]{12}|'  # Discover
                r'3(?:0[0-5]|[68][0-9])[0-9]{11})\b'  # Diners Club
            ),
            
            PIIType.IP_ADDRESS: re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            
            PIIType.BANK_ACCOUNT: re.compile(
                r'\b\d{9,18}\b'  # 9-18 digit account numbers
            ),
            
            PIIType.DATE_OF_BIRTH: re.compile(
                r'\b(?:[0-3]?[0-9][-/])?(?:0?[1-9]|1[0-2])[-/](?:19|20)\d{2}\b'
            ),
            
            PIIType.SSN: re.compile(
                r'\b(?!000-|666-)(?!9\d{2})\d{3}-?\d{2}-?\d{4}\b'
            ),
        }
    
    def detect_pii(self, text: str) -> Dict[str, List[Dict]]:
        """
        Detect PII in text using regex patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary mapping PII types to list of detected items:
            {
                'EMAIL': [{'text': 'user@example.com', 'start': 0, 'end': 18}, ...],
                'PHONE': [...],
                ...
            }
        """
        detected = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = list(pattern.finditer(text))
            if matches:
                detected[pii_type.value] = [
                    {
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'type': pii_type.value
                    }
                    for match in matches
                ]
        
        return detected
    
    def detect_passwords(self, text: str) -> List[Dict]:
        """
        Detect potential passwords using keyword matching and pattern analysis.
        IMPORTANT: Tries to avoid false positives by checking context.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected password patterns
        """
        passwords = []
        
        # Keywords that indicate passwords
        password_keywords = [
            r'password\s*(?:is|=|:)\s*[\'"]*([^\s\'"]+)',
            r'pwd\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
            r'pass\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
            r'my\s+password\s*(?:is|=)\s*[\'"]*([^\s\'"]+)',
            r'api_key\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
            r'api[-_]key\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
            r'token\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
            r'secret\s*(?:=|:)\s*[\'"]*([^\s\'"]+)',
        ]
        
        for pattern_str in password_keywords:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                password_text = match.group(1) if match.groups() else match.group(0)
                
                if password_text and len(password_text) >= 6:
                    passwords.append({
                        'text': password_text,
                        'start': match.start(),
                        'end': match.end(),
                        'type': 'PASSWORD'
                    })
        
        return passwords
    
    def get_pii_summary(self, detected_pii: Dict) -> Dict[str, int]:
        """
        Get count of each PII type detected.
        
        Args:
            detected_pii: Dictionary from detect_pii()
            
        Returns:
            Dictionary with PII type counts
        """
        return {
            pii_type: len(items) 
            for pii_type, items in detected_pii.items()
        }


# Placeholder mapping for masking
PLACEHOLDER_MAP = {
    'PERSON': '[NAME]',
    'ORG': '[ORGANIZATION]',
    'GPE': '[LOCATION]',
    'LOC': '[LOCATION]',
    'EMAIL': '[EMAIL]',
    'PHONE': '[PHONE]',
    'AADHAAR': '[AADHAAR]',
    'PAN': '[PAN]',
    'CREDIT_CARD': '[CARD]',
    'DEBIT_CARD': '[CARD]',
    'IP_ADDRESS': '[IP_ADDRESS]',
    'BANK_ACCOUNT': '[ACCOUNT]',
    'DATE_OF_BIRTH': '[DOB]',
    'PASSWORD': '[PASSWORD]',
    'API_KEY': '[API_KEY]',
    'SSN': '[SSN]',
}


class PII_Masker:
    """
    Handles masking and unmasking of PII in text.
    Maintains bidirectional mapping between original and masked values.
    """
    
    def __init__(self):
        """Initialize masker with empty mapping dictionary."""
        self.mask_map = {}  # Original -> Masked
        self.unmask_map = {}  # Masked -> Original
    
    def mask_entity(self, entity_text: str, entity_type: str) -> str:
        """
        Create a masked version of an entity with consistent mapping.
        
        Args:
            entity_text: Original text to mask
            entity_type: Type of entity (from PIIType)
            
        Returns:
            Masked placeholder string
        """
        # Check if already masked
        if entity_text in self.mask_map:
            return self.mask_map[entity_text]
        
        # Get placeholder for this type
        placeholder = PLACEHOLDER_MAP.get(entity_type, '[REDACTED]')
        
        # If multiple items of same type, add counter
        count = sum(1 for k, v in self.mask_map.items() if v == placeholder)
        if count > 0:
            placeholder = f"{placeholder[:-1]}{count + 1}]"
        
        # Store mapping
        self.mask_map[entity_text] = placeholder
        self.unmask_map[placeholder] = entity_text
        
        return placeholder
    
    def unmask_text(self, text: str) -> str:
        """
        Replace masked placeholders with original values.
        
        Args:
            text: Text with placeholders to unmask
            
        Returns:
            Text with original values restored
        """
        unmasked = text
        for placeholder, original in self.unmask_map.items():
            unmasked = unmasked.replace(placeholder, original)
        return unmasked
    
    def get_mapping(self) -> Dict[str, str]:
        """Get current mask mapping."""
        return self.mask_map.copy()
    
    def get_reverse_mapping(self) -> Dict[str, str]:
        """Get reverse mapping (masked -> original)."""
        return self.unmask_map.copy()
    
    def clear(self):
        """Clear all mappings."""
        self.mask_map.clear()
        self.unmask_map.clear()


def create_regex_detector() -> RegexDetector:
    """Factory function to create regex detector instance."""
    return RegexDetector()


def create_masker() -> PII_Masker:
    """Factory function to create masker instance."""
    return PII_Masker()
