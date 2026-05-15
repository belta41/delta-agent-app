with open('app/main.py', 'r') as f:
    content = f.read()

content = content.replace(
    "delta_key = os.environ.get('DELTA_API_KEY', '')",
    "delta_key = 'VjbVGYo3MnYskcbQxvcoYK0DXTHnHO'"
)
content = content.replace(
    "delta_secret = os.environ.get('DELTA_API_SECRET', '')",
    "delta_secret = 'hPBLh7YajFYeGf9O0aneHKxrlOVobrl7gzSacxEr38YuEHbgBLhimGXmeRYE'"
)

with open('app/main.py', 'w') as f:
    f.write(content)

print("API keys embedded in main.py")
