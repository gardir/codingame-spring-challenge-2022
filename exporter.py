import re


file_list = [
	'constants',
	'base',
	'entity',
	'hero',
	'monster',
	'player',
	'main'
]
import_pattern = re.compile(r"from .+ import .+")


with open('codingame.py', 'w') as outfile:
	for f in file_list:
		with open(f"{f}.py") as reader:
			for line in reader:
				matches = re.match(import_pattern, line)
				if not matches:
					outfile.write(line)

print("Done!")
