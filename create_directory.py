import os

structure = {
    "backend": {
        "app": {
            "core": [],
            "integrations": [],
            "repositories": [],
            "validation": []
        },
        "scripts": [],
        "workers": {
            "flows": [],
            "tasks": []
        },
        "migration": []
    }
}

def create_structure(path, structure):
    for name, sub_items in structure.items():
        dir_path = os.path.join(path, name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

        if isinstance(sub_items, dict):
            create_structure(dir_path, sub_items)

create_structure(".", structure)
print("\n Directory structure created successfully.")