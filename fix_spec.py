filepath = '/root/android-app/buildozer.spec'
with open(filepath) as f:
    lines = f.readlines()
# Remove duplicate android.add_src
new_lines = []
seen = set()
for line in lines:
    stripped = line.strip()
    if stripped.startswith('android.add_src'):
        if stripped in seen:
            continue
        seen.add(stripped)
    new_lines.append(line)
with open(filepath, 'w') as f:
    f.writelines(new_lines)
print("Fixed buildozer.spec - removed duplicate line")
