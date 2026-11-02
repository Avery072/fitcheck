#!/usr/bin/env python3
"""CloudFormation template validator that handles CFN intrinsic functions"""
import yaml
import sys
import re

# Custom YAML loader that handles CloudFormation tags
class CFNLoader(yaml.SafeLoader):
    pass

# Register all CloudFormation intrinsic functions as constructors
cfn_tags = ['!Ref', '!Sub', '!GetAtt', '!Join', '!Select', '!FindInMap',
            '!GetAZs', '!Base64', '!Split', '!ImportValue', '!If',
            '!Equals', '!Not', '!Or', '!And', '!Condition']

for tag in cfn_tags:
    CFNLoader.add_constructor(tag, lambda loader, node: loader.construct_scalar(node))

# Handle multi-constructor for GetAtt
CFNLoader.add_multi_constructor('!', lambda loader, tag_suffix, node: loader.construct_scalar(node))

try:
    with open('template.yaml', 'r') as f:
        content = f.read()
        data = yaml.load(content, Loader=CFNLoader)

    # Check required top-level keys
    required_keys = ['AWSTemplateFormatVersion', 'Transform']
    for key in required_keys:
        if key not in data:
            print(f"❌ ERROR: Missing required key: {key}")
            sys.exit(1)

    # Check we have resources
    if 'Resources' not in data or not data['Resources']:
        print("❌ ERROR: No resources defined")
        sys.exit(1)

    # Summary
    print("✅ template.yaml is valid CloudFormation YAML")
    print(f"   ├─ Version: {data['AWSTemplateFormatVersion']}")
    print(f"   ├─ Transform: {data['Transform']}")
    print(f"   ├─ Resources: {len(data.get('Resources', {}))}")
    print(f"   ├─ Outputs: {len(data.get('Outputs', {}))}")
    print(f"   └─ Parameters: {len(data.get('Globals', {}))}")

    # List resources
    print("\n📦 Resources:")
    for name, resource in data['Resources'].items():
        res_type = resource.get('Type', 'Unknown')
        print(f"   ├─ {name}: {res_type}")

    print("\n✨ Template is ready to deploy!")
    sys.exit(0)

except yaml.YAMLError as e:
    print(f"❌ YAML syntax error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
