# Entity Types Configuration for Engineering Specifications KG
# This defines the ontology for technical standards and material specifications

ENGINEERING_ENTITY_TYPES = [
    # Core Specification Entities
    "Specification",          # Internal specs (1E0003, 1E2679, etc.)
    "Standard",              # External standards (ASTM, ISO, JIS, DIN, SAE, AWS, BS, etc.)
    "Grade",                 # Material grades (65-35, WCB, SAE 1025, etc.)
    
    # Material Entities
    "Material",              # Material types (Steel Casting, Alloy, etc.)
    "Composition Element",   # Chemical elements (Carbon, Manganese, Silicon, etc.)
    
    # Property Entities
    "Mechanical Property",   # Tensile Strength, Yield Strength, Hardness, etc.
    "Chemical Property",     # Composition percentages, purity levels
    "Physical Property",     # Density, thermal conductivity, etc.
    "Property Value",        # Specific values or ranges (450 MPa, 0.19-0.29%, etc.)
    
    # Process Entities
    "Process",               # Manufacturing/treatment processes (Welding, Heat Treatment, etc.)
    "Test Method",           # Testing procedures (Hardenability test, Tensile test, etc.)
    
    # Application & Context
    "Application",           # Use cases (Welded Assemblies, Structural Components, etc.)
    "Requirement",           # Specific requirements or criteria
    
    # Organizational
    "Organization",          # Standards bodies (ASTM, ISO, AWS, etc.)
    
    # General
    "Other"                  # Catch-all for entities that don't fit above categories
]

# Relationship Types for Engineering Specifications
ENGINEERING_RELATIONSHIP_TYPES = {
    # Specification Relationships
    "REFERENCES": "Specification references another specification",
    "SUPERSEDES": "Specification replaces an older specification",
    "SUPPLEMENTS": "Specification adds to another specification",
    "REQUIRES": "Specification mandates compliance with another spec",
    
    # Material Relationships
    "SUBSTITUTES_FOR": "Material/spec can replace another",
    "EQUIVALENT_TO": "Material/spec is equivalent to another",
    "APPROVED_BY": "Substitution is approved by specification",
    
    # Composition Relationships
    "HAS_COMPOSITION": "Material contains element/component",
    "HAS_RANGE": "Element/property has value range",
    "HAS_LIMIT": "Property has maximum or minimum limit",
    
    # Property Relationships
    "HAS_PROPERTY": "Material has mechanical/chemical/physical property",
    "HAS_VALUE": "Property has specific value",
    "HAS_MINIMUM_VALUE": "Property has minimum acceptable value",
    "HAS_MAXIMUM_VALUE": "Property has maximum acceptable value",
    
    # Process Relationships
    "REQUIRES_PROCESS": "Material requires specific process",
    "TESTED_BY": "Property measured by test method",
    "APPLIES_PROCESS": "Process applied to material",
    
    # Standard Relationships
    "COMPLIES_WITH": "Material/process complies with standard",
    "DEFINED_BY": "Requirement defined by standard",
    "ISSUED_BY": "Standard issued by organization",
    "HAS_GRADE": "Standard includes grade designation",
    
    # Application Relationships
    "USED_IN": "Material used in application",
    "APPLIES_TO": "Specification applies to application/context",
    "SUITABLE_FOR": "Material suitable for application",
    
    # General
    "RELATED_TO": "General relationship between entities"
}

# Property extraction patterns for better entity recognition
PROPERTY_PATTERNS = {
    "composition": r"(\w+)\s*[:]\s*([\d.]+[-–][\d.]+)\s*%",  # Carbon: 0.19-0.29%
    "property_value": r"([\w\s]+)\s*[:]\s*([\d.]+)\s*(\w+)",  # Tensile Strength: 450 MPa
    "range": r"([\d.]+)\s*[-–]\s*([\d.]+)",  # 0.19-0.29
    "spec_number": r"\b\d[A-Z]\d{4}[A-Z]?\b",  # 1E0003, 1E2349B
    "astm": r"ASTM\s+[A-Z]\d+",  # ASTM A27
    "iso": r"ISO\s+\d+",  # ISO 3755
    "aws": r"AWS\s+[A-Z]\d+\.\d+",  # AWS A5.1
}

# Example usage configuration
ENTITY_TYPE_EXAMPLES = {
    "Specification": ["1E0003", "1E2679", "1E2349B", "1E0024"],
    "Standard": ["ASTM A27", "ASTM A216", "ISO 3755", "JIS G5101", "AWS A5.1", "SAE J435"],
    "Grade": ["65-35", "WCB", "SAE 1025", "E7018", "SC450"],
    "Material": ["Steel Casting", "Carbon Steel", "Alloy Steel", "Cast Iron"],
    "Composition Element": ["Carbon", "Manganese", "Silicon", "Chromium", "Molybdenum"],
    "Mechanical Property": ["Tensile Strength", "Yield Strength", "Elongation", "Hardness"],
    "Property Value": ["450 MPa", "240 MPa", "0.19-0.29%", "4.6 mm Brinell"],
    "Process": ["Welding", "Heat Treatment", "Quenching", "Tempering", "Post Weld Heat Treatment"],
    "Test Method": ["Hardenability Test", "Tensile Test", "Brinell Hardness Test"],
    "Application": ["Welded Assemblies", "Structural Components", "High-Temperature Service"],
}

# Guidelines for entity extraction
EXTRACTION_GUIDELINES = {
    "preserve_exact": [
        "specification_numbers",  # 1E0003 not 1e0003
        "standard_codes",  # ASTM A27 not astm a27
        "units",  # MPa not mpa
        "grades",  # 65-35 not 65-36
    ],
    "include_context": [
        "property_values_with_units",  # "450 MPa" not just "450"
        "ranges_with_percent",  # "0.19-0.29%" not "0.19-0.29"
        "qualifiers",  # "minimum 450 MPa" not just "450 MPa"
    ],
    "decompose": [
        "composition_into_element_and_range",
        "property_into_name_and_value",
        "standard_into_organization_code_and_grade",
    ]
}
