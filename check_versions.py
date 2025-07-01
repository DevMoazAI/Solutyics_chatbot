import importlib.metadata
import ast

# List of files to check
files_to_check = ['main.py', 'chat_util.py', 'thread.py']

# Set to hold unique libraries
libraries = set()

# Function to extract libraries from a file
def extract_libraries_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Parse the content to find import statements
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    libraries.add(alias.name.split('.')[0])  # Add only the main package
            elif isinstance(node, ast.ImportFrom):
                if node.module:  # Check if module is not None
                    libraries.add(node.module.split('.')[0])  # Add only the main package

# Extract libraries from each specified file
for file in files_to_check:
    extract_libraries_from_file(file)

# Print the versions of the libraries
for library in libraries:
    try:
        version = importlib.metadata.version(library)
        print(f"{library}: {version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{library}: Not installed")