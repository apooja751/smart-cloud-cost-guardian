import sys, os, base64
path, mode_str, b64_content = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.dirname(path), exist_ok=True)
mode = 'ab' if mode_str == 'append' else 'wb'
padded = b64_content + '=' * (-len(b64_content) % 4)
open(path, mode).write(base64.b64decode(padded))
print('Written:', path)
