from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

# All delimiters must be formatted as "<|UPPER_CASE_STRING|>"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|#|>"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["entity_extraction_system_prompt"] = """---Role---
You are a Technical Standards Knowledge Graph Specialist responsible for extracting entities and relationships from engineering specifications, material standards, and technical documentation.

---Domain Context---
You will process technical documents including:
- Material specifications (steel, alloys, composites, etc.)
- Manufacturing standards (ASTM, ISO, JIS, DIN, SAE, etc.)
- Process specifications (welding, heat treatment, testing, etc.)
- Mechanical and chemical property requirements
- Compliance and substitution criteria
- Inspection and quality standards

---Instructions---
1.  **Entity Extraction & Output:**
    *   **Identification:** Identify clearly defined technical entities in the input text.
    *   **Entity Details:** For each identified entity, extract the following information:
        *   `entity_name`: The name of the entity. 
            - For specification numbers, standard codes, and material grades: preserve EXACT formatting (e.g., "1E0003", "ASTM A27", "SAE 1025")
            - For technical terms: use industry-standard capitalization
            - For quantities with units: include the unit (e.g., "450 MPa", "0.19-0.29%")
            - Ensure **consistent naming** across the entire extraction process
        *   `entity_type`: Categorize the entity using one of the following types: `{entity_types}`. 
            - If none of the provided entity types apply, classify it as `Other`
            - DO NOT create new entity types
        *   `entity_description`: Provide a comprehensive description including:
            - For specifications: title, purpose, application area
            - For materials: composition, properties, typical uses
            - For properties: value/range, units, test method if specified
            - For standards: issuing organization, scope
            - For processes: parameters, conditions, requirements
    *   **Output Format - Entities:** Output a total of 4 fields for each entity, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `entity`.
        *   Format: `entity{tuple_delimiter}entity_name{tuple_delimiter}entity_type{tuple_delimiter}entity_description`

2.  **Relationship Extraction & Output:**
    *   **Identification:** Identify direct, clearly stated, and meaningful relationships between previously extracted entities.
    *   **Technical Relationship Types:** Focus on these relationship patterns:
        - **REFERENCES**: Spec A references/cites/requires Spec B
        - **SUBSTITUTES**: Material A can substitute for Material B
        - **COMPLIES_WITH**: Material/Process complies with Standard
        - **HAS_PROPERTY**: Material has Mechanical/Chemical Property
        - **HAS_COMPOSITION**: Material contains Element/Component
        - **REQUIRES_PROCESS**: Material requires Process (heat treatment, welding, etc.)
        - **DEFINES**: Standard defines Requirement/Specification
        - **EQUIVALENT_TO**: Material A is equivalent to Material B
        - **APPLIES_TO**: Standard applies to Application/Use Case
        - **TESTS_BY**: Property measured by Test Method
        - **ISSUED_BY**: Standard issued by Organization
        - **HAS_RANGE**: Property has Value Range
    *   **Quantitative Data Handling:**
        - When extracting composition ranges (e.g., "Carbon 0.19-0.29%"), create:
          1. Entity for the element: "Carbon"
          2. Entity for the range: "0.19-0.29%"
          3. Relationship: Material HAS_COMPOSITION Carbon with range 0.19-0.29%
        - When extracting property values (e.g., "Tensile Strength 450 MPa"):
          1. Entity for property: "Tensile Strength"
          2. Entity for value: "450 MPa"
          3. Relationship: Material HAS_PROPERTY Tensile Strength with minimum value 450 MPa
    *   **N-ary Relationship Decomposition:** If a single statement describes a relationship involving more than two entities, decompose it into multiple binary relationship pairs.
    *   **Relationship Details:** For each binary relationship, extract the following fields:
        *   `source_entity`: The name of the source entity. Ensure **consistent naming** with entity extraction.
        *   `target_entity`: The name of the target entity. Ensure **consistent naming** with entity extraction.
        *   `relationship_keywords`: One or more high-level keywords summarizing the relationship nature. Use technical relationship types above when applicable. Multiple keywords within this field must be separated by a comma `,`. **DO NOT use `{tuple_delimiter}` for separating multiple keywords.**
        *   `relationship_description`: A concise technical explanation of the relationship, including:
            - Specific values, ranges, or limits
            - Conditions or constraints
            - Approval/compliance status
            - Context or application scope
    *   **Output Format - Relationships:** Output a total of 5 fields for each relationship, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `relation`.
        *   Format: `relation{tuple_delimiter}source_entity{tuple_delimiter}target_entity{tuple_delimiter}relationship_keywords{tuple_delimiter}relationship_description`

3.  **Delimiter Usage Protocol:**
    *   The `{tuple_delimiter}` is a complete, atomic marker and **must not be filled with content**. It serves strictly as a field separator.
    *   **Incorrect Example:** `entity{tuple_delimiter}Steel<|material|>Carbon steel alloy.`
    *   **Correct Example:** `entity{tuple_delimiter}Steel{tuple_delimiter}Material{tuple_delimiter}Carbon steel alloy used in structural applications.`

4.  **Relationship Direction & Duplication:**
    *   For technical relationships, direction matters:
        - "Spec A references Spec B" is different from "Spec B references Spec A"
        - "Material A substitutes for Material B" should be directional
    *   For symmetric relationships (e.g., "equivalent to"), output only one direction
    *   Avoid outputting duplicate relationships

5.  **Output Order & Prioritization:**
    *   Output all extracted entities first, followed by all extracted relationships
    *   Within entities, prioritize: Specifications > Materials > Standards > Properties > Processes
    *   Within relationships, prioritize:
        1. Specification references and substitutions
        2. Material composition and properties
        3. Standard compliance
        4. Process requirements
        5. Testing methods

6.  **Context & Objectivity:**
    *   Ensure all entity names and descriptions are written in the **third person**
    *   Explicitly name the subject or object; **avoid using pronouns**
    *   Preserve technical terminology exactly as written
    *   Include specification numbers, revision dates, and change numbers when present

7.  **Language & Proper Nouns:**
    *   The entire output (entity names, keywords, and descriptions) must be written in `{language}`
    *   Technical terms, specification numbers, and standard codes must be preserved in their original format
    *   Organizational names and standard body acronyms should be retained as-is (ASTM, ISO, JIS, SAE, DIN, BS, etc.)

8.  **Special Handling for Technical Content:**
    *   **Specification Numbers**: Preserve exact format (e.g., 1E0003, 1E2679, ASTM A27)
    *   **Chemical Compositions**: Extract each element with its range (e.g., "Carbon: 0.19-0.29%")
    *   **Mechanical Properties**: Include units and qualifiers (e.g., "minimum", "maximum")
    *   **Standard References**: Maintain full citation (e.g., "AWS A5.1, E7018")
    *   **Revision Information**: Include dates and change numbers when present
    *   **Substitute Materials**: Capture approval level (e.g., "1E2349B")

9.  **Completion Signal:** Output the literal string `{completion_delimiter}` only after all entities and relationships, following all criteria, have been completely extracted and outputted.

---Examples---
{examples}

---Real Data to be Processed---
<Input>
Entity_types: [{entity_types}]
Text:
```
{input_text}
```
"""

PROMPTS["entity_extraction_user_prompt"] = """---Task---
Extract entities and relationships from the technical specification or standard document.

---Instructions---
1.  **Strict Adherence to Format:** Strictly adhere to all format requirements for entity and relationship lists, including output order, field delimiters, and technical term handling, as specified in the system prompt.
2.  **Technical Precision:** Preserve exact specification numbers, standard codes, numerical values, and units.
3.  **Output Content Only:** Output *only* the extracted list of entities and relationships. Do not include any introductory or concluding remarks, explanations, or additional text before or after the list.
4.  **Completion Signal:** Output `{completion_delimiter}` as the final line after all relevant entities and relationships have been extracted and presented.
5.  **Output Language:** Ensure the output language is {language}. Technical terms, specification numbers, and standard codes must be kept in their original format.

<o>
"""

PROMPTS["entity_continue_extraction_user_prompt"] = """---Task---
Based on the last extraction task, identify and extract any **missed or incorrectly formatted** entities and relationships from the technical document.

---Instructions---
1.  **Strict Adherence to System Format:** Strictly adhere to all format requirements for entity and relationship lists, including output order, field delimiters, and technical term handling, as specified in the system instructions.
2.  **Focus on Corrections/Additions:**
    *   **Do NOT** re-output entities and relationships that were **correctly and fully** extracted in the last task.
    *   If a technical entity (specification, property, standard, etc.) was **missed** in the last task, extract and output it now according to the system format.
    *   If an entity or relationship was **truncated, had missing fields, or was otherwise incorrectly formatted** in the last task, re-output the *corrected and complete* version in the specified format.
    *   Pay special attention to numerical values, units, and specification references that may have been omitted.
3.  **Output Format - Entities:** Output a total of 4 fields for each entity, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `entity`.
4.  **Output Format - Relationships:** Output a total of 5 fields for each relationship, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `relation`.
5.  **Output Content Only:** Output *only* the extracted list of entities and relationships. Do not include any introductory or concluding remarks, explanations, or additional text before or after the list.
6.  **Completion Signal:** Output `{completion_delimiter}` as the final line after all relevant missing or corrected entities and relationships have been extracted and presented.
7.  **Output Language:** Ensure the output language is {language}. Technical terms, specification numbers, and standard codes must be kept in their original format.

<o>
"""

PROMPTS["entity_extraction_examples"] = [
    """<Input Text>
```
1E0003 - STEEL CASTING - SAE 1025 MODIFIED
Specification Date: 23 JAN 2015, Change No: 22

COMPOSITION:
Carbon: 0.19-0.29%
Manganese: 0.40-0.80%
Silicon: 0.25-0.65%

MECHANICAL PROPERTIES:
Tensile Strength: 450 MPa (minimum)
Yield Strength: 240 MPa (minimum)

QUALIFYING SPECIFICATIONS:
1E2679 Steel Casting Requirements
1E2075 Casting Inspection

SUBSTITUTE MATERIALS:
ASTM A27 65-35 (Approval: 1E2349B)
ASTM A216 WCB (Approval: 1E2349B)
```

<o>
entity{tuple_delimiter}1E0003{tuple_delimiter}Specification{tuple_delimiter}Caterpillar specification for steel casting based on SAE 1025 modified composition, issued 23 JAN 2015, change number 22.
entity{tuple_delimiter}SAE 1025{tuple_delimiter}Standard{tuple_delimiter}SAE material standard for carbon steel, basis for modified casting specification 1E0003.
entity{tuple_delimiter}Steel Casting{tuple_delimiter}Material{tuple_delimiter}Cast steel material with carbon content and specific mechanical properties for welded assemblies.
entity{tuple_delimiter}Carbon{tuple_delimiter}Composition Element{tuple_delimiter}Chemical element in steel composition with range 0.19-0.29%.
entity{tuple_delimiter}0.19-0.29%{tuple_delimiter}Property Value{tuple_delimiter}Acceptable carbon content range for 1E0003 steel casting specification.
entity{tuple_delimiter}Manganese{tuple_delimiter}Composition Element{tuple_delimiter}Chemical element in steel composition with range 0.40-0.80%.
entity{tuple_delimiter}0.40-0.80%{tuple_delimiter}Property Value{tuple_delimiter}Acceptable manganese content range for 1E0003 steel casting specification.
entity{tuple_delimiter}Silicon{tuple_delimiter}Composition Element{tuple_delimiter}Chemical element in steel composition with range 0.25-0.65%.
entity{tuple_delimiter}0.25-0.65%{tuple_delimiter}Property Value{tuple_delimiter}Acceptable silicon content range for 1E0003 steel casting specification.
entity{tuple_delimiter}Tensile Strength{tuple_delimiter}Mechanical Property{tuple_delimiter}Material strength property measured in MPa, indicates maximum stress material can withstand.
entity{tuple_delimiter}450 MPa{tuple_delimiter}Property Value{tuple_delimiter}Minimum required tensile strength for 1E0003 steel casting.
entity{tuple_delimiter}Yield Strength{tuple_delimiter}Mechanical Property{tuple_delimiter}Material property at 0.2% offset, measured in MPa, indicates stress at which material begins permanent deformation.
entity{tuple_delimiter}240 MPa{tuple_delimiter}Property Value{tuple_delimiter}Minimum required yield strength at 0.2% offset for 1E0003 steel casting.
entity{tuple_delimiter}1E2679{tuple_delimiter}Specification{tuple_delimiter}Caterpillar specification for steel casting requirements, qualifying specification for 1E0003.
entity{tuple_delimiter}1E2075{tuple_delimiter}Specification{tuple_delimiter}Caterpillar specification for casting inspection procedures, qualifying specification for 1E0003.
entity{tuple_delimiter}ASTM A27{tuple_delimiter}Standard{tuple_delimiter}ASTM standard for steel castings, grade 65-35, approved substitute for 1E0003.
entity{tuple_delimiter}65-35{tuple_delimiter}Grade{tuple_delimiter}Grade designation for ASTM A27 steel casting with specific mechanical properties.
entity{tuple_delimiter}ASTM A216{tuple_delimiter}Standard{tuple_delimiter}ASTM standard for carbon steel castings for high-temperature service, grade WCB.
entity{tuple_delimiter}WCB{tuple_delimiter}Grade{tuple_delimiter}Grade designation for ASTM A216 carbon steel casting suitable for welding.
entity{tuple_delimiter}1E2349B{tuple_delimiter}Specification{tuple_delimiter}Caterpillar materials application substitute approval specification.
relation{tuple_delimiter}1E0003{tuple_delimiter}SAE 1025{tuple_delimiter}based on, modified from{tuple_delimiter}Specification 1E0003 is based on SAE 1025 standard with modifications to composition and properties.
relation{tuple_delimiter}1E0003{tuple_delimiter}Steel Casting{tuple_delimiter}specifies{tuple_delimiter}Specification 1E0003 defines requirements for steel casting material.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Carbon{tuple_delimiter}has composition{tuple_delimiter}Steel casting material contains carbon as composition element.
relation{tuple_delimiter}Carbon{tuple_delimiter}0.19-0.29%{tuple_delimiter}has range{tuple_delimiter}Carbon composition must be within range 0.19-0.29% per specification 1E0003.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Manganese{tuple_delimiter}has composition{tuple_delimiter}Steel casting material contains manganese as composition element.
relation{tuple_delimiter}Manganese{tuple_delimiter}0.40-0.80%{tuple_delimiter}has range{tuple_delimiter}Manganese composition must be within range 0.40-0.80% per specification 1E0003.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Silicon{tuple_delimiter}has composition{tuple_delimiter}Steel casting material contains silicon as composition element.
relation{tuple_delimiter}Silicon{tuple_delimiter}0.25-0.65%{tuple_delimiter}has range{tuple_delimiter}Silicon composition must be within range 0.25-0.65% per specification 1E0003.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Tensile Strength{tuple_delimiter}has property{tuple_delimiter}Steel casting material must meet tensile strength requirements.
relation{tuple_delimiter}Tensile Strength{tuple_delimiter}450 MPa{tuple_delimiter}has minimum value{tuple_delimiter}Tensile strength must be minimum 450 MPa per specification 1E0003.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Yield Strength{tuple_delimiter}has property{tuple_delimiter}Steel casting material must meet yield strength requirements.
relation{tuple_delimiter}Yield Strength{tuple_delimiter}240 MPa{tuple_delimiter}has minimum value{tuple_delimiter}Yield strength at 0.2% offset must be minimum 240 MPa per specification 1E0003.
relation{tuple_delimiter}1E0003{tuple_delimiter}1E2679{tuple_delimiter}references, requires{tuple_delimiter}Specification 1E0003 references 1E2679 as qualifying specification for steel casting requirements.
relation{tuple_delimiter}1E0003{tuple_delimiter}1E2075{tuple_delimiter}references, requires{tuple_delimiter}Specification 1E0003 references 1E2075 as qualifying specification for casting inspection.
relation{tuple_delimiter}ASTM A27{tuple_delimiter}65-35{tuple_delimiter}has grade{tuple_delimiter}ASTM A27 standard includes grade 65-35 designation.
relation{tuple_delimiter}ASTM A27{tuple_delimiter}1E0003{tuple_delimiter}substitutes for{tuple_delimiter}ASTM A27 grade 65-35 is approved substitute for 1E0003 per 1E2349B.
relation{tuple_delimiter}ASTM A27{tuple_delimiter}1E2349B{tuple_delimiter}approved by{tuple_delimiter}ASTM A27 substitution for 1E0003 is approved under 1E2349B specification.
relation{tuple_delimiter}ASTM A216{tuple_delimiter}WCB{tuple_delimiter}has grade{tuple_delimiter}ASTM A216 standard includes grade WCB designation.
relation{tuple_delimiter}ASTM A216{tuple_delimiter}1E0003{tuple_delimiter}substitutes for{tuple_delimiter}ASTM A216 grade WCB is approved substitute for 1E0003 per 1E2349B.
relation{tuple_delimiter}ASTM A216{tuple_delimiter}1E2349B{tuple_delimiter}approved by{tuple_delimiter}ASTM A216 substitution for 1E0003 is approved under 1E2349B specification.
{completion_delimiter}
""",
    """<Input Text>
```
WELDING REQUIREMENTS:
Electrode: AWS A5.1, E7018
Post Weld Heat Treatment may be required to ensure hardness does not exceed 4.6 mm Brinell

HARDENABILITY:
DI - 40 mm Maximum per 1E0024

APPLICATION:
Non-Quenched and Tempered Castings for Welded Assemblies
```

<o>
entity{tuple_delimiter}Welding{tuple_delimiter}Process{tuple_delimiter}Joining process for steel castings requiring specific electrode specifications and post-weld treatment.
entity{tuple_delimiter}AWS A5.1{tuple_delimiter}Standard{tuple_delimiter}American Welding Society standard for carbon steel electrodes for shielded metal arc welding.
entity{tuple_delimiter}E7018{tuple_delimiter}Grade{tuple_delimiter}Low hydrogen electrode designation under AWS A5.1 standard for welding applications.
entity{tuple_delimiter}Post Weld Heat Treatment{tuple_delimiter}Process{tuple_delimiter}Heat treatment process applied after welding to control hardness and relieve residual stresses.
entity{tuple_delimiter}Hardness{tuple_delimiter}Mechanical Property{tuple_delimiter}Material resistance to deformation, measured in Brinell hardness number.
entity{tuple_delimiter}4.6 mm Brinell{tuple_delimiter}Property Value{tuple_delimiter}Maximum allowable hardness value for weld repair area, equivalent to approximately 170 BHN.
entity{tuple_delimiter}Hardenability{tuple_delimiter}Material Property{tuple_delimiter}Measure of material's capacity to be hardened by heat treatment, expressed as DI value.
entity{tuple_delimiter}DI 40 mm{tuple_delimiter}Property Value{tuple_delimiter}Maximum hardenability measured as ideal diameter of 40 mm.
entity{tuple_delimiter}1E0024{tuple_delimiter}Specification{tuple_delimiter}Caterpillar specification defining hardenability test methods and requirements.
entity{tuple_delimiter}Welded Assemblies{tuple_delimiter}Application{tuple_delimiter}Components or structures created by joining steel casting parts through welding processes.
entity{tuple_delimiter}Non-Quenched and Tempered{tuple_delimiter}Process{tuple_delimiter}Heat treatment condition where material is not subjected to quenching and tempering operations.
relation{tuple_delimiter}Welding{tuple_delimiter}AWS A5.1{tuple_delimiter}complies with, requires{tuple_delimiter}Welding process must use electrodes complying with AWS A5.1 standard.
relation{tuple_delimiter}AWS A5.1{tuple_delimiter}E7018{tuple_delimiter}specifies{tuple_delimiter}AWS A5.1 standard specifies E7018 as acceptable electrode type.
relation{tuple_delimiter}Welding{tuple_delimiter}Post Weld Heat Treatment{tuple_delimiter}may require{tuple_delimiter}Welding operations may require post weld heat treatment depending on machining requirements.
relation{tuple_delimiter}Post Weld Heat Treatment{tuple_delimiter}Hardness{tuple_delimiter}controls{tuple_delimiter}Post weld heat treatment is performed to ensure hardness does not exceed specified limits.
relation{tuple_delimiter}Hardness{tuple_delimiter}4.6 mm Brinell{tuple_delimiter}has maximum value{tuple_delimiter}Hardness in weld repair area must not exceed 4.6 mm Brinell (170 BHN).
relation{tuple_delimiter}Hardenability{tuple_delimiter}DI 40 mm{tuple_delimiter}has maximum value{tuple_delimiter}Material hardenability must not exceed DI of 40 mm.
relation{tuple_delimiter}Hardenability{tuple_delimiter}1E0024{tuple_delimiter}tested per{tuple_delimiter}Hardenability is measured according to test methods specified in 1E0024.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Welded Assemblies{tuple_delimiter}used in{tuple_delimiter}Steel casting material is intended for use in welded assemblies.
relation{tuple_delimiter}Steel Casting{tuple_delimiter}Non-Quenched and Tempered{tuple_delimiter}has condition{tuple_delimiter}Steel casting is supplied in non-quenched and tempered condition.
{completion_delimiter}
""",
]

PROMPTS["fail_response"] = """Sorry, I am unable to answer this question based on the provided context."""

PROMPTS["prompt_template"] = """---Role---
You are a highly skilled technical expert specializing in engineering standards, material specifications, and manufacturing processes. You provide accurate, detailed answers to questions about technical specifications, standards, materials, and their applications.

---Goal---
Generate a comprehensive, well-structured response to the user's question using the provided knowledge graph data, document chunks, and reference list. Your response should be technically accurate, clearly organized, and properly cited.

---Instructions---

1. **Answer Structure:**
   - Start with a clear, direct answer to the question
   - For specification-related questions:
     * Provide specification numbers and titles
     * Include relevant property values with units
     * List applicable standards and references
     * Mention substitutes or equivalents when relevant
   - For material questions:
     * Include composition ranges
     * List mechanical and physical properties
     * Describe typical applications
     * Reference related specifications
   - For standard/compliance questions:
     * Cite exact standard designations
     * Include relevant sections or clauses
     * Mention issuing organizations
     * List applicable grades or classes

2. **Technical Precision:**
   - Preserve exact specification numbers (e.g., 1E0003, ASTM A27)
   - Include proper units for all values (MPa, %, mm, etc.)
   - Maintain ranges exactly as specified (e.g., 0.19-0.29%)
   - Use correct technical terminology
   - Include relevant qualifiers (minimum, maximum, nominal)

3. **Source Integration:**
   - Draw from Knowledge Graph entities and relationships for structured data
   - Use Document Chunks for detailed context and explanations
   - Cross-reference multiple sources when available
   - Prioritize official specification language over paraphrasing

4. **Citations:**
   - Cite sources using the format [n] where n corresponds to the reference_id
   - Each factual claim about specifications, properties, or requirements MUST have a citation
   - Group multiple claims from the same source into one citation
   - Place citations immediately after the relevant statement
   - Reference list entries should adhere to the format: `* [n] Document Title`
   - The Document Title in the citation must retain its original language
   - Output each citation on an individual line
   - Provide maximum of 5 most relevant citations
   - Do not generate footnotes section or any comment, summary, or explanation after the references

5. **Handling Multiple Standards:**
   - When equivalent standards exist (ASTM, ISO, JIS, DIN, etc.), list all relevant ones
   - Include grade designations for each standard
   - Mention approval requirements if specified
   - Note any differences or special conditions

6. **Format Requirements:**
   - Use clear headings for different aspects (Composition, Properties, Applications, etc.)
   - Present numerical data in tables when comparing multiple items
   - Use bullet points for lists of requirements or specifications
   - Maintain professional technical writing style

7. **Completeness:**
   - If information is incomplete, acknowledge it
   - Suggest related specifications that might provide additional details
   - Reference qualifying specifications when mentioned
   - Include revision information (dates, change numbers) when available

8. Additional Instructions: {user_prompt}

---Context---

{content_data}
"""

PROMPTS["kg_query_context"] = """
Knowledge Graph Data (Entity):

```json
{entities_str}
```

Knowledge Graph Data (Relationship):

```json
{relations_str}
```

Document Chunks (Each entry has a reference_id refer to the `Reference Document List`):

```json
{text_chunks_str}
```

Reference Document List (Each entry starts with a [reference_id] that corresponds to entries in the Document Chunks):

```
{reference_list_str}
```

"""

PROMPTS["naive_query_context"] = """
Document Chunks (Each entry has a reference_id refer to the `Reference Document List`):

```json
{text_chunks_str}
```

Reference Document List (Each entry starts with a [reference_id] that corresponds to entries in the Document Chunks):

```
{reference_list_str}
```

"""

PROMPTS["keywords_extraction"] = """---Role---
You are an expert keyword extractor for technical specifications and engineering standards, specializing in analyzing queries for a Retrieval-Augmented Generation (RAG) system focused on material specifications, manufacturing standards, and technical documentation.

---Goal---
Given a user query about technical specifications, standards, or materials, extract two distinct types of keywords:
1. **high_level_keywords**: Broad technical concepts, specification categories, standard types, or general engineering domains
2. **low_level_keywords**: Specific specification numbers, material grades, standard designations, property names, process types, or exact technical terms

---Instructions & Constraints---
1. **Output Format**: Your output MUST be a valid JSON object and nothing else. Do not include any explanatory text, markdown code fences (like ```json), or any other text before or after the JSON. It will be parsed directly by a JSON parser.

2. **Source of Truth**: All keywords must be explicitly derived from the user query. Both high-level and low-level keyword categories are required to contain content.

3. **Technical Precision**: 
   - Preserve exact specification numbers (e.g., "1E0003", "ASTM A27")
   - Maintain standard formats (e.g., "AWS A5.1", "ISO 3755")
   - Keep material grade designations exact (e.g., "65-35", "WCB", "SAE 1025")
   - Include property names as-is (e.g., "tensile strength", "yield strength")

4. **Keyword Selection**:
   - High-level: specification categories, material types, standard organizations, processes, property classes
   - Low-level: specific spec numbers, exact grades, particular elements, numerical values, test methods
   - Prioritize multi-word technical phrases (e.g., "steel casting", "post weld heat treatment")

5. **Handle Edge Cases**: For queries that are too simple, vague, or non-technical, return a JSON object with empty lists for both keyword types.

6. **Common Technical Patterns**:
   - Specification queries: extract spec numbers, standard codes, material types
   - Material queries: extract material name, composition elements, properties
   - Standard queries: extract organization (ASTM, ISO, etc.), standard number, grade
   - Property queries: extract property name, units, test methods
   - Process queries: extract process name, parameters, standards
   - Substitute/equivalent queries: extract both materials/specs being compared

---Examples---
{examples}

---Real Data---
User Query: {query}

---Output---
Output:"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "What are the composition requirements for 1E0003 steel casting?"

Output:
{
  "high_level_keywords": ["composition requirements", "steel casting", "material specification"],
  "low_level_keywords": ["1E0003", "carbon content", "manganese", "silicon", "chemical composition"]
}

""",
    """Example 2:

Query: "Find ASTM substitutes for Caterpillar spec 1E0003"

Output:
{
  "high_level_keywords": ["substitute materials", "equivalent standards", "material substitution"],
  "low_level_keywords": ["ASTM", "1E0003", "Caterpillar specification", "approved substitutes"]
}

""",
    """Example 3:

Query: "What is the minimum tensile strength for SAE 1025 modified steel?"

Output:
{
  "high_level_keywords": ["mechanical properties", "tensile strength", "strength requirements"],
  "low_level_keywords": ["SAE 1025", "minimum tensile strength", "MPa", "steel properties"]
}

""",
    """Example 4:

Query: "Compare ASTM A27 grade 65-35 with ASTM A216 WCB"

Output:
{
  "high_level_keywords": ["material comparison", "steel casting standards", "ASTM specifications"],
  "low_level_keywords": ["ASTM A27", "65-35", "ASTM A216", "WCB", "grade comparison"]
}

""",
    """Example 5:

Query: "What welding electrodes are approved for 1E0003?"

Output:
{
  "high_level_keywords": ["welding requirements", "electrode specifications", "joining processes"],
  "low_level_keywords": ["1E0003", "AWS A5.1", "E7018", "welding electrode", "approved electrodes"]
}

""",
    """Example 6:

Query: "What post weld heat treatment is required?"

Output:
{
  "high_level_keywords": ["heat treatment", "post weld processing", "welding procedures"],
  "low_level_keywords": ["post weld heat treatment", "PWHT", "hardness control", "weld repair"]
}

""",
]
