import sys

import yaml
import app_config

from main import app

print("---")
print("Updating configuration...")
try:
    app_config.create_configuration_documentation("docs/DefaultConfiguration.md")
    print("Done.")
    print("---")
except Exception as e:
    print("Updating the Configuration failed.")
    print(e)
    sys.exit(1)

print("Updating OpenAPI documents...")
try:
    openapi_spec = app.openapi()
    try:
        with open("./docs/openapi.yaml", "w") as openapi_output_file:
            yaml.dump(openapi_spec, openapi_output_file, sort_keys=False)
    except Exception as e:
        print("Failed to create OpenAPI document")
        print(e)
        raise ValueError("Failed to create OpenAPI document")
except Exception as e:
    print("Updating OpenAPI documents failed.")
    print(e)
    sys.exit(1)
