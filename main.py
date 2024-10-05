import sys
import enum
import typing

from dataclasses import dataclass, field
from collections import defaultdict

class Modes(str, enum.Enum):
    mealy_to_moore = "mealy-to-moore"
    moore_to_mealy = "moore-to-mealy"

@dataclass
class MealyData:
    states: typing.List[str] = field(default_factory=list)
    state_outputs: typing.Dict[str, typing.Set[str]] = field(
        default_factory=lambda: defaultdict(set))  # state -> set of produced output symbols
    input_to_transitions: typing.Dict[str, dict] = field(
        default_factory=lambda: defaultdict(dict))  # symbol -> current state -> next state/output

@dataclass
class MooreData:
    state_output: typing.Dict[str, str] = field(default_factory=dict)  # state -> output
    input_to_transitions: typing.Dict[str, dict] = field(
        default_factory=lambda: defaultdict(dict))  # symbol -> current state -> next state/output


def read_mealy(filename: str) -> MealyData:
    with open(filename) as f:
        input_data = f.read().strip()
        
    mealy_data = MealyData()

    # Save states
    for state in input_data.splitlines()[0].split(";")[1:]:
        mealy_data.states.append(state.strip())

    # Save transitions
    for transitions in input_data.splitlines()[1:]:
        input_symbol = transitions.split(";")[0].strip()

        for i, transition in enumerate(transitions.split(";")[1:]):
            state, output = transition.strip().split("/")
            mealy_data.state_outputs[state].add(output)
            mealy_data.input_to_transitions[input_symbol][mealy_data.states[i]] = f"{state}/{output}"
    
    return mealy_data


def read_moore(filename: str) -> MooreData:
    with open(filename) as f:
        input_data = f.read().strip()
        
    moore_data = MooreData()

    # Save state with his output
    input_outputs_line = input_data.splitlines()[0].split(";")[1:]
    input_states_line = input_data.splitlines()[1].split(";")[1:]

    for output, state in zip(input_outputs_line, input_states_line):
        moore_data.state_output[state] = output

    # Save transitions
    for transitions in input_data.splitlines()[2:]:
        input_symbol = transitions.split(";")[0].strip()

        for i, transition in enumerate(transitions.split(";")[1:]):
            state = transition.strip()
            output = moore_data.state_output[state]
            moore_data.input_to_transitions[input_symbol][
                list(moore_data.state_output.keys())[i]] = f"{state}/{output}"
    
    return moore_data


def write_line(file: typing.IO, line):
    if not line:
        file.write("\n")
        
    elif isinstance(line[0], str):
        file.write(";".join(line) + "\n")

    elif isinstance(line[0], list):
        for array in line:
            write_line(file, array)


def write_to_file(filename: str, *lines: list):
    with open(filename, "w") as f:
        for line in lines:
            write_line(f, line)


def prepare_transitions(
    input_to_transitions: typing.Dict[str, typing.Dict[str, str]],
    state_outputs:  dict = None, 
    replacements: dict = None) -> list:

    input_lines = list()

    for symbol in input_to_transitions:
        line = [symbol]

        for current_state in input_to_transitions[symbol]:
            next_state = input_to_transitions[symbol][current_state]

            if state_outputs:
                repeats = len(state_outputs.get(current_state, [1]))
                line.extend(replacements[next_state] for _ in range(repeats))
            else:
                line.append(next_state)
        
        input_lines.append(line)

    return input_lines


def mealy_to_moore(input_file, output_file):
    mealy_data = read_mealy(input_file)
    replacements: dict[str, str] = dict()  # example: "F1/0" -> "R0", "F1/1" -> "R1" 

    # Sort transitions
    state_outputs = dict(sorted(mealy_data.state_outputs.items()))
    for state in state_outputs:
        state_outputs[state] = sorted(state_outputs[state])

    # Create replacement for states and transitions
    for state in mealy_data.states:
        if state not in state_outputs: 
            replacements[state] = "R" + str(len(replacements))
        else:
            for output in state_outputs[state]:
                transition = f"{state}/{output}"
                replacements[transition] = "R" + str(len(replacements))

    # Convert to moore
    outputs_line = [""]
    states_line = [""]

    # Outputs and states lines
    for state in mealy_data.states:
        if state not in state_outputs:
            outputs_line.append("")
            states_line.append(replacements[state])
        else:
            for output in state_outputs[state]:
                outputs_line.append(output)
                states_line.append(replacements[f"{state}/{output}"])

    # Transitions lines
    transitions_lines = prepare_transitions(mealy_data.input_to_transitions, state_outputs, replacements)
    
    # Write to output
    write_to_file(output_file, outputs_line, states_line, transitions_lines)


def moore_to_mealy(input_file, output_file):
    moore_data = read_moore(input_file)
    
    # Convert to mealy
    states_line = ["", *moore_data.state_output]
    
    # Transitions lines
    transitions_lines = prepare_transitions(moore_data.input_to_transitions)
    
    # Write to output
    write_to_file(output_file, states_line, transitions_lines)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in Modes._value2member_map_:
        raise Exception("Wrong arguments. Usage: main.py mealy-to-moore mealy.csv moore.csv")
    
    if sys.argv[1] == Modes.mealy_to_moore:
        mealy_to_moore(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == Modes.moore_to_mealy:
        moore_to_mealy(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()