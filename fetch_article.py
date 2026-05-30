import subprocess, re

result = subprocess.run(
    ['curl', '-sL', '-A', 'Mozilla/5.0',
     'https://mp.weixin.qq.com/s/ACMCprYq59T8VRYMkjNHnA'],
    capture_output=True, text=True, timeout=15
)
html = result.stdout

# Find all div ids to understand the structure
ids = re.findall(r'id="([^"]+)"', html)
print("Found IDs:", ids[:20])

# Check for rich_media_content
if 'js_content' in html:
    # Find position
    idx = html.find('js_content')
    print("\nContext around js_content:")
    print(html[max(0,idx-200):idx+500])
elif 'rich_media_content' in html:
    idx = html.find('rich_media_content')
    print("\nContext around rich_media_content:")
    print(html[max(0,idx-200):idx+800])
else:
    # Print first 3000 chars to understand
    print("\nFirst 3000 chars:")
    print(html[:3000])
