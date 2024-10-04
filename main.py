import sys
import enum

from collections import defaultdict

class Modes(str, enum.Enum):
    mealy_to_moore = "mealy-to-moore"
    moore_to_mealy = "moore-to-mealy"


def mealy_to_moore(input_file, output_file):
    with open(input_file) as f:
        input_data = f.read().strip()
        
    replacements: dict[str, str] = dict()  # example: "F1/0" -> "R0", "F1/1" -> "R1" 
    states: list[str] = list()  # literally splitted first line of mealy input file
    state_outputs: dict[str, set[str]] = defaultdict(set)  # state -> set of produced output symbols
    input_to_transitions: dict[str, dict[str, str]] = defaultdict(dict)  # symbol -> current state -> next state/output

    # Save states
    for state in input_data.splitlines()[0].split(";")[1:]:
        states.append(state.strip())

    # Save transitions
    for transitions in input_data.splitlines()[1:]:
        input_symbol = transitions.split(";")[0].strip()

        for i, transition in enumerate(transitions.split(";")[1:]):
            state, output = transition.strip().split("/")
            state_outputs[state].add(output)
            input_to_transitions[input_symbol][states[i]] = f"{state}/{output}"

    # Sort transitions
    state_outputs = dict(sorted(state_outputs.items()))
    for state in state_outputs:
        state_outputs[state] = sorted(state_outputs[state])

    # Create replacement for states and transitions
    for state in states:
        if state not in state_outputs: 
            replacements[state] = "R" + str(len(replacements))
        else:
            for output in state_outputs[state]:
                transition = f"{state}/{output}"
                replacements[transition] = "R" + str(len(replacements))

    # Convert to moore
    outputs_line = [""]
    states_line = [""]
    input_lines = []

    # Outputs and states lines
    for state in states:
        if state not in state_outputs:
            outputs_line.append("")
            states_line.append(replacements[state])
        else:
            for output in state_outputs[state]:
                outputs_line.append(output)
                states_line.append(replacements[f"{state}/{output}"])

    # Input lines
    for symbol in input_to_transitions:
        line = []
        line.append(symbol)

        for current_state in input_to_transitions[symbol]:
            next_state = input_to_transitions[symbol][current_state]
            repeats = 1 if current_state not in state_outputs else len(state_outputs[current_state])

            for _ in range(repeats):
                line.append(replacements[next_state])
        
        input_lines.append(line)
    
    # Write to output
    with open(output_file, "w") as f:
        f.write(";".join(outputs_line) + "\n")
        f.write(";".join(states_line))
        for line in input_lines:
            f.write("\n" + ";".join(line))


def moore_to_mealy(input_file, output_file):
    with open(input_file) as f:
        input_data = f.read().strip()
    
    state_output: dict[str, str] = dict()  # state -> output
    input_to_transitions: dict[str, dict[str, str]] = defaultdict(dict)  # symbol -> current state -> next state/output

    # Save state with his output
    input_outputs_line = input_data.splitlines()[0].split(";")[1:]
    input_states_line = input_data.splitlines()[1].split(";")[1:]

    for output, state in zip(input_outputs_line, input_states_line):
        state_output[state] = output

    # Save transitions
    for transitions in input_data.splitlines()[2:]:
        input_symbol = transitions.split(";")[0].strip()

        for i, transition in enumerate(transitions.split(";")[1:]):
            state = transition.strip()
            output = state_output[state]
            input_to_transitions[input_symbol][list(state_output.keys())[i]] = f"{state}/{output}"
    
    # Convert to mealy
    states_line = [""]
    states_line.extend(list(state_output.keys()))
    input_lines = []
    
    # Input lines
    for symbol in input_to_transitions:
        line = []
        line.append(symbol)

        for current_state in input_to_transitions[symbol]:
            transition = input_to_transitions[symbol][current_state]
            line.append(transition)
        
        input_lines.append(line)
    
    # Write to output
    with open(output_file, "w") as f:
        f.write(";".join(states_line))
        for line in input_lines:
            f.write("\n" + ";".join(line))


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in Modes._value2member_map_:
        raise Exception("Wrong arguments. Usage: main.py mealy-to-moore mealy.csv moore.csv")
    
    if sys.argv[1] == Modes.mealy_to_moore:
        mealy_to_moore(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == Modes.moore_to_mealy:
        moore_to_mealy(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()