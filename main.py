import sys
from minimzie import minimize_mealy, minimize_moore

if __name__ == "__main__":
    if sys.argv[1].lower() == "mealy":
        minimize_mealy(sys.argv[2], sys.argv[3])

    elif sys.argv[1].lower() == "moore":
        minimize_moore(sys.argv[2], sys.argv[3])
