import urllib.request
import os

url = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt'
urllib.request.urlretrieve(url, 'wordlist.txt')
size = os.path.getsize('wordlist.txt')
with open('wordlist.txt') as f:
    lines = f.read().strip().split('\n')
print(f"Downloaded {size} bytes, {len(lines)} words")
print(f"Sample: {lines[:10]}")
