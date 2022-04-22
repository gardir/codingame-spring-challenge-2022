import re


file_list = [
	'main.py'
]
import_patterns = map(re.compile, [r"from .* import .*"])

with open('codingame.py', 'w') as outfile:
	for f in file_list:
		with open(f) as reader:
			for line in reader:
				to_be_added = True
				for pattern in import_patterns:
					matches = re.match(pattern, line)
					if matches:
						to_be_added = False
						break
				if to_be_added:
					outfile.write(line)

print("Done!")
