from auth import User, Query, db
from app import app
import json

with app.app_context():
    # Get the latest query
    latest = Query.query.order_by(Query.timestamp.desc()).first()
    
    if latest:
        print("="*80)
        print("ORIGINAL QUERY:")
        print("-"*80)
        print(latest.original_query)
        
        print("\n" + "="*80)
        print("DETECTED ENTITIES:")
        print("-"*80)
        entities = json.loads(latest.detected_entities)
        for entity_type, items in entities.items():
            if items:
                print(f"{entity_type}:")
                for item in items:
                    if isinstance(item, dict):
                        print(f"  - {item.get('text')}")
                    else:
                        print(f"  - {item}")
        
        print("\n" + "="*80)
        print("RISK SCORE:")
        print("-"*80)
        print(f"Score: {latest.risk_score}/100")
        
        print("\n" + "="*80)
        print("MASKED QUERY (Sent to AI):")
        print("-"*80)
        print(latest.masked_query)
        
        print("\n" + "="*80)
        print("AI RESPONSE:")
        print("-"*80)
        print(latest.ai_response[:1000] if latest.ai_response else "No response")
        
        print("\n" + "="*80)
        print("UNMASKED RESPONSE:")
        print("-"*80)
        print(latest.unmasked_response[:1000] if latest.unmasked_response else "No response")
    else:
        print("No queries found in database")
