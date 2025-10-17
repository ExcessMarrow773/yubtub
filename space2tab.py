import os

def convert_file_spaces_to_tabs(file_path, output_path=None):
	with open(file_path, 'r', encoding='utf-8') as f:
		lines = f.readlines()

	converted_lines = []
	for line in lines:
		leading_spaces = len(line) - len(line.lstrip(' '))
		if leading_spaces % 3 != 0:
			print(f"Warning: Line not divisible by 3 spaces:\n{line}")
		tab_count = leading_spaces // 3
		stripped_line = line.lstrip(' ')
		new_line = '\t' * tab_count + stripped_line
		converted_lines.append(new_line)

	out_path = output_path or file_path
	with open(out_path, 'w', encoding='utf-8') as f:
		f.writelines(converted_lines)
	print(f"Converted: {file_path} -> {out_path}")

# Example usage
if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Convert 3-space indented Python files to tab-indented.")
	parser.add_argument("files", nargs='+', help="Python files to convert.")
	parser.add_argument("--inplace", action='store_true', help="Modify files in-place.")
	args = parser.parse_args()

	for file in args.files:
		if not file.endswith('.py'):
			print(f"Skipping non-Python file: {file}")
			continue
		output_file = None if args.inplace else f"{os.path.splitext(file)[0]}_tabs.py"
		convert_file_spaces_to_tabs(file, output_file)
