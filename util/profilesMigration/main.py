from lxml import etree
import json
import os
import argparse

SCHEMA = ""  #Input Schema Path
NS = {'ns': 'http://soap.sforce.com/2006/04/metadata'}

def main():
    with open(SCHEMA, "r") as f:
        profile2ps_schema = json.load(f)
        
    list_keys       = list(profile2ps_schema.keys())
    args            = parse_args()
    output_path     = args.output
    profiles_path   = args.profilePath
    
    tabVisibility_mapping = {
        "Hidden": "None",
        "DefaultOff": "Available",
        "DefaultOn": "Visible"
    }
    
    
    for profile in os.listdir(profiles_path):
        if not profile.startswith("."):
            new_root        = etree.Element('PermissionSet', xmlns='http://soap.sforce.com/2006/04/metadata') 
            nodes           = []
            profile_Name    = profile.split(".profile-meta")[0].replace(" ", "_")
            label_PS        = input('Introduce la label del nuevo PermissionSet: ')
            
            while not label_PS:
                label_PS = input('Introduce la label del nuevo PermissionSet: ')
            
            with open(os.path.join(profiles_path, profile), 'rb') as file:
                xml                                                      = file.read()
                etree.SubElement(new_root, 'label').text                 = label_PS
                etree.SubElement(new_root, 'hasActivationRequired').text = "false"
                
                root = etree.fromstring(xml)
                for child in root:
                    if child.xpath('local-name()') in list_keys:
                        profileTagName  = list(profile2ps_schema[child.xpath('local-name()')].keys())[0]
                        psTagNames      = profile2ps_schema[child.xpath('local-name()')][profileTagName]
                        
                        new_child       = etree.SubElement(new_root, profileTagName)
                        
                        for subchild in child:
                            if subchild.xpath('local-name()') in psTagNames:
                                new_subchild = etree.SubElement(new_child, subchild.xpath('local-name()'))

                                if profileTagName == "tabSettings" and subchild.xpath('local-name()') == "visibility":
                                    new_subchild.text = tabVisibility_mapping.get(subchild.text)
                                else:
                                    new_subchild.text = subchild.text
                        nodes.append(new_child)
                        
                    elif child.xpath('local-name()') == "userLicense":
                        new_child       = etree.SubElement(new_root, 'license')
                        new_child.text  = child.text
                        nodes.append(new_child)
                        
                    elif child.xpath('local-name()') == "description":
                        new_child       = etree.SubElement(new_root, 'description')
                        new_child.text  = child.text
                        nodes.append(new_child)

            nodes.sort(key=lambda x: x.xpath('local-name()'))
            
            for node in nodes:
                new_root.append(node)
            
            with open(os.path.join(output_path,'EasyPS_{profile_Name}.permissionset-meta.xml'), 'wb') as file:
                file.write(etree.tostring(new_root, pretty_print=True, xml_declaration=True))   

def parse_args():
    parser = argparse.ArgumentParser(description='Convert profiles to permission sets.')
    parser.add_argument('--output', '-o', type=str, required=True, help='Output path to save the generated Permission Sets')
    parser.add_argument('--profilePath', '-p', type=str, required=True, help='Path where are the profiles to convert.')
    return parser.parse_args()

if __name__ == '__main__':
    main()
    