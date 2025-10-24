import sys

def check_syntax(filename):
    with open(filename, 'r') as f:
        try:
            compile(f.read(), filename, 'exec')
            print(f"No syntax errors in {filename}")
        except SyntaxError as e:
            print(f"Syntax error in {filename} at line {e.lineno}, position {e.offset}:")
            print(f"  {e.text.strip()}")
            print(f"  {' ' * (e.offset - 1)}^")
            print(f"Error message: {str(e)}")
        except Exception as e:
            print(f"Error checking {filename}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python syntax_check.py <filename>")
    else:
        check_syntax(sys.argv[1])
