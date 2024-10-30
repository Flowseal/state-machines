import sys
from minimzie import minimize_mealy
from convert import moore_to_mealy, mealy_to_moore

if __name__ == "__main__":
    if sys.argv[1].lower() == "mealy":
        minimize_mealy(sys.argv[2], sys.argv[3])

    elif sys.argv[1].lower() == "moore":
        moore_to_mealy(sys.argv[2], "moore_mealy.csv")
        minimize_mealy("moore_mealy.csv", sys.argv[3])
        mealy_to_moore(sys.argv[3], sys.argv[3])
