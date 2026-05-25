import os
import glob

dirs_needing_init = [
    "backend/app",
    "backend/app/core",
    "backend/app/integrations",
    "backend/app/repositories",
    "backend/app/validation",
    "backend/workers",
    "backend/workers/flows",
    "backend/workers/tasks",
    "backend/scripts",
    "backend/migration"

]

for dir_path in dirs_needing_init:
    init_file = os.path.join(dir_path, "__init__.py")
    with open(init_file, "w") as f:
        pass  # Create empty __init__.py file
print("Created __init__.py files in all specified directories.")
