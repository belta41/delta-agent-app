filepath = '/root/android-app/buildozer.spec'
with open(filepath) as f:
    lines = f.readlines()
# Remove all lines containing android.add_src except the first one
count = 0
new_lines = []
for line in lines:
    if 'android.add_src' in line:
        count += 1
        if count > 1:
            continue
    new_lines.append(line)
with open(filepath, 'w') as f:
    f.writelines(new_lines)
print(f"Removed {count-1} duplicate android.add_src lines")
