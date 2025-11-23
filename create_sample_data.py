"""Create sample recycling data for testing"""
import json

# Sample data with realistic materials
sample_data = {
    'categories': {
        'Weapons': [
            {
                'name': 'Assault Rifle',
                'category': 'Weapons',
                'url': 'https://arcraiders.wiki/wiki/Assault_Rifle',
                'materials': [
                    {'name': 'Steel', 'quantity': 15},
                    {'name': 'Polymer', 'quantity': 8},
                    {'name': 'Electronics', 'quantity': 3}
                ]
            },
            {
                'name': 'Sniper Rifle',
                'category': 'Weapons',
                'url': 'https://arcraiders.wiki/wiki/Sniper_Rifle',
                'materials': [
                    {'name': 'Steel', 'quantity': 20},
                    {'name': 'Optics', 'quantity': 2},
                    {'name': 'Electronics', 'quantity': 5}
                ]
            },
            {
                'name': 'Shotgun',
                'category': 'Weapons',
                'url': 'https://arcraiders.wiki/wiki/Shotgun',
                'materials': [
                    {'name': 'Steel', 'quantity': 12},
                    {'name': 'Polymer', 'quantity': 6}
                ]
            }
        ],
        'Augments': [
            {
                'name': 'Shield Booster',
                'category': 'Augments',
                'url': 'https://arcraiders.wiki/wiki/Shield_Booster',
                'materials': [
                    {'name': 'Electronics', 'quantity': 10},
                    {'name': 'Rare Alloy', 'quantity': 3}
                ]
            },
            {
                'name': 'Speed Enhancer',
                'category': 'Augments',
                'url': 'https://arcraiders.wiki/wiki/Speed_Enhancer',
                'materials': [
                    {'name': 'Electronics', 'quantity': 8},
                    {'name': 'Polymer', 'quantity': 5}
                ]
            }
        ],
        'Shields': [
            {
                'name': 'Energy Shield',
                'category': 'Shields',
                'url': 'https://arcraiders.wiki/wiki/Energy_Shield',
                'materials': [
                    {'name': 'Rare Alloy', 'quantity': 5},
                    {'name': 'Electronics', 'quantity': 12},
                    {'name': 'Power Cell', 'quantity': 2}
                ]
            }
        ],
        'Healing': [
            {
                'name': 'Med Kit',
                'category': 'Healing',
                'url': 'https://arcraiders.wiki/wiki/Med_Kit',
                'materials': [
                    {'name': 'Polymer', 'quantity': 3},
                    {'name': 'Medical Supplies', 'quantity': 8}
                ]
            }
        ],
        'Quick Use': [
            {
                'name': 'Repair Tool',
                'category': 'Quick Use',
                'url': 'https://arcraiders.wiki/wiki/Repair_Tool',
                'materials': [
                    {'name': 'Steel', 'quantity': 5},
                    {'name': 'Electronics', 'quantity': 4}
                ]
            }
        ],
        'Grenades': [
            {
                'name': 'Frag Grenade',
                'category': 'Grenades',
                'url': 'https://arcraiders.wiki/wiki/Frag_Grenade',
                'materials': [
                    {'name': 'Steel', 'quantity': 8},
                    {'name': 'Explosives', 'quantity': 6}
                ]
            },
            {
                'name': 'EMP Grenade',
                'category': 'Grenades',
                'url': 'https://arcraiders.wiki/wiki/EMP_Grenade',
                'materials': [
                    {'name': 'Electronics', 'quantity': 15},
                    {'name': 'Rare Alloy', 'quantity': 2}
                ]
            }
        ],
        'Traps': [
            {
                'name': 'Proximity Mine',
                'category': 'Traps',
                'url': 'https://arcraiders.wiki/wiki/Proximity_Mine',
                'materials': [
                    {'name': 'Steel', 'quantity': 6},
                    {'name': 'Electronics', 'quantity': 8},
                    {'name': 'Explosives', 'quantity': 10}
                ]
            }
        ]
    },
    'metadata': {
        'version': '1.0',
        'scraped_at': '2025-11-23T14:20:00Z',
        'total_items': 10,
        'categories_count': 7,
        'elapsed_seconds': 0,
        'failed_categories': 0,
        'failed_items': 0
    }
}

# Save to output folder
with open('output/recycling_data.json', 'w', encoding='utf-8') as f:
    json.dump(sample_data, f, indent=2, ensure_ascii=False)

print("✅ Sample data created with 10 items and 9 unique materials")
print("   Materials: Steel, Polymer, Electronics, Optics, Rare Alloy, Power Cell, Medical Supplies, Explosives")
print("\nRun: python main.py")
print("Then open: output/recycling_tracker.html")
