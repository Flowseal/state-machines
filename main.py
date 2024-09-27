import sys
import enum

from collections import defaultdict

class Modes(str, enum.Enum):
    mealy_to_moore = "mealy-to-moore"
    moore_to_mealy = "moore-to-mealy"


def mealy_to_moore(input_file, output_file):
    with open(input_file) as f:
        input_data = f.read()
        
    replacements: dict[str, str] = dict()
    state_outputs: dict[str, set[str]] = defaultdict(set)

    # Save input symbols and state/outputs pairs
    for transitions in input_data.splitlines()[1:]:
        for transition in transitions.split(";")[1:]:
            state, output = transition.split("/")   
            state_outputs[state].add(output)

    state_outputs = dict(sorted(state_outputs.items()))
    for state in state_outputs:
        state_outputs[state] = sorted(state_outputs[state])   
    
    # Create replacement for states without transitions in themselves
    for state in input_data.splitlines()[0].split(";")[1:]:
        if state not in state_outputs:
            replacements[state] = "R" + str(len(replacements))

    # Create replacement for transitions
    for state, outputs in state_outputs.items():
        for output in outputs:
            transition = f"{state}/{output}"
            if transition not in replacements:
                replacements[transition] = "R" + str(len(replacements))

    # Convert to moore
    outputs_line = [""]
    states_line = [""]


# Mealy
#   ; F1 ; F2 ; F3 
# b1;F1/0;F1/1;F1/2 
# b2;F2/1;F2/0;F2/1
# b3;F3/2;F3/1;F3/0

# Moore
#   ;0 ;1 ;2 ;0 ;1 ;0 ;1 ;2 
#   ;R0;R1;R2;R3;R4;R5;R6;R7
# b1;R0;R0;R0;R1;R1;R2;R2;R2  
# b2;R4;R4;R4;R3;R3;R4;R4;R4  
# b3;R7;R7;R7;R6;R6;R5;R5;R5


def moore_to_mealy(input_file, output_file):
    ... 


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in Modes._value2member_map_:
        raise Exception("Wrong arguments. Usage: main.py mealy-to-moore mealy.csv moore.csv")
    
    if sys.argv[1] == Modes.mealy_to_moore:
        mealy_to_moore(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == Modes.moore_to_mealy:
        moore_to_mealy(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()