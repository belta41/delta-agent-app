import sys
filepath = sys.argv[1]
with open(filepath) as f:
    c = f.read()

old = 'self.agent = EliteAgent(api_key=VjbVGYo3MnYskcbQxvcoYK0DXTHnHO, api_secret=hPBLh7YajFYeGf9O0aneHKxrlOVobrl7gzSacxEr38YuEHbgBLhimGXmeRYE)'
new = 'self.agent = EliteAgent(api_key="VjbVGYo3MnYskcbQxvcoYK0DXTHnHO", api_secret="hPBLh7YajFYeGf9O0aneHKxrlOVobrl7gzSacxEr38YuEHbgBLhimGXmeRYE")'

if old in c:
    c = c.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(c)
    print("Keys fixed with quotes")
else:
    print("Pattern not found - checking current state:")
    for line in c.split('\n'):
        if 'EliteAgent(api_key' in line:
            print(f"  Found: {line.strip()}")
