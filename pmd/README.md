# PMD

Creates a customizable report from a PMD analysis.

## Params

```
-r --reportFile     Path where PMD report is stored
-o --outputFile     Path where report will be saved
-s --srcPath        Path where src is located
```

## Customizable Sections

Files [sections](/resources/sections.json) and [subSections](/resources/subSections.json) allow to create different sections and classify PMD issues into these sections.

### Params

- **level**: first classification level. Can be used to classify issues by risk (critical, high, medium, low).
- **section**: group issues by category (Nomenclature, Documentation, Readability, ..).
- **subSection**: group issues by type (Standard Cyclomatic Complexity, Total Cyclomatic Complexity, NNCS Line Count, ..).
- **classification**: group issues by subtype (class, method, constructor, ..).

Example:

```
"level"             : "Medium",
"section"           : "Readability", 
"subSection"        : "NNCS Line Count", 
"classification"    : "Constructor" 
```

Parameters section, subSection and classification are not mandatory. If they are blank, issue will be added to 'Not Classified' group.

### Sections JSON

The script will check if any issue matchs a key value from sections.json. To add a new item, copy issue message as a new key and add the desired classification.

Example:

```
    "Hardcoding Ids is bound to break when changing environments." : { 
        "level"             : "Critical",
        "section"           : "Hardcoded Ids" 
    },
```

### SubSections JSON

The script will check if any issue contains key values from subSections.json. It can be used when several issues share a common message but differ in type of element, such as the following rule:

```
The [constructor|method|type] has an NCSS line count of
```

To add a new item, copy the common segment from issue message and add as a new key. Then, add each variation as an inner key with their respective classification.

Example:

```
    "has an NCSS line count of" : { 
        "The constructor " : { 
            "level"             : "Medium",
            "section"           : "Readability", 
            "subSection"        : "NNCS Line Count", 
            "classification"    : "Constructor" 
        },
        "The method " : { 
            "level"             : "Medium",
            "section"           : "Readability", 
            "subSection"        : "NNCS Line Count", 
            "classification"    : "Method"
        },
        "The type " : { 
            "level"             : "Medium",
            "section"           : "Readability", 
            "subSection"        : "NNCS Line Count", 
            "classification"    : "Method"
        }
    }
```