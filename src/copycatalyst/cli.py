import argparse
from .app import FileSelectorApp

def main():
    parser = argparse.ArgumentParser(description="File selection and content copying tool.")
    parser.add_argument("path", help="The root directory to start selection from")
    parser.add_argument("-A", "--all", action="store_true", help="Automatically select all files")
    args = parser.parse_args()

    app = FileSelectorApp(args.path, auto_select_all=args.all)
    app.run()

if __name__ == "__main__":
    main()