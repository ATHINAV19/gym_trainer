import os
import sys

def main():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    vbs_path = os.path.join(base_dir, "run_hidden.vbs")

    os.startfile(vbs_path)

if __name__ == "__main__":
    main()