import json

def check_and_fix_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            json.loads(content)  # Attempt to load JSON data
    except json.JSONDecodeError as e:
        print(f"Error in {file_path}: {e}")

        # Try to fix the JSON formatting by removing extra curly braces at the end
        while content.endswith('}') and content[:-1].count('{') > content[:-1].count('}'):
            content = content[:-1].rstrip()

        # Write the corrected content back to the file
        with open(file_path, 'w') as file:
            file.write(content)
        
        print("JSON formatting issue fixed.")
    else:
        print("No JSON formatting issues found.")

# Example usage:
check_and_fix_credentials("credentials.json")
