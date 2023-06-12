# EasyPermissionSet Generator Script Documentation

---

This script converts Salesforce profile metadata files into Permission Set metadata files.
## Requirements
- Python 3.x
- lxml library
- json library
- os library
- argparse library

## Constants
- **SCHEMA**: The path to the JSON file containing the schema for mapping profile tags to permission set tags.
- **NS**: Namespace for XML elements.

## Functions
### main()
This function reads the schema from the JSON file and iterates over each profile metadata file in the specified directory. For each profile, it creates a new permission set XML tree with a root element of PermissionSet. The user is prompted to enter a label for the new permission set. The function then reads the profile metadata file and maps its elements to the corresponding permission set elements using the schema. The tabVisibility values are mapped using the _tabVisibility_mapping_ dictionary. The resulting permission set XML tree is then written to a new file in the specified output directory.

### parse_args()
This function uses the argparse library to parse command line arguments. It defines two required arguments: --output (or -o) for specifying the output path to save the generated permission sets, and --profilePath (or -p) for specifying the path to the directory containing the profile metadata files.

## Usage
To use this script, **make sure that the SCHEMA constant is set to the correct path.** Then, run the script using a Python 3 interpreter and provide the required command line arguments. For example:

> python3 script.py --output /path/to/output/dir --profilePath /path/to/profiles/dir

You will be prompted to enter a label for each permission set that is generated.