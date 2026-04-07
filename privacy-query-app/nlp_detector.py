"""
NLP-based PII detection using SpaCy Named Entity Recognition (NER).
Detects PERSON, ORG, GPE, and LOC entities from text.
"""

import spacy
from typing import Dict, List


class NLPDetector:
    """
    Uses SpaCy's pre-trained models for Named Entity Recognition.
    Identifies persons, organizations, locations, and geographic entities.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NLP detector with a SpaCy model.
        
        Args:
            model_name: SpaCy model to load (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"Model '{model_name}' not found. Install with: python -m spacy download {model_name}"
            )
    
    def detect_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Detect named entities in text using SpaCy NER.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary mapping entity types to list of entities with positions:
            {
                'PERSON': [{'text': 'John', 'start': 0, 'end': 4}, ...],
                'ORG': [...],
                'GPE': [...],
                'LOC': [...]
            }
        """
        doc = self.nlp(text)
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'LOC': []
        }
        
        # Extract entities organized by type
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.start_char + len(ent.text),
                    'label': ent.label_
                })
        
        return entities
    
    def get_entity_summary(self, entities: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Get count of each entity type.
        
        Args:
            entities: Dictionary from detect_entities()
            
        Returns:
            Dictionary with entity type counts
        """
        return {
            entity_type: len(entity_list) 
            for entity_type, entity_list in entities.items()
        }


def create_nlp_detector(model_name: str = "en_core_web_sm") -> NLPDetector:
    """
    Factory function to create NLP detector instance.
    
    Args:
        model_name: SpaCy model name to use
        
    Returns:
        Initialized NLPDetector instance
    """
    return NLPDetector(model_name)
