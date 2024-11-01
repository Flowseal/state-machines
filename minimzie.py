import typing

from utils import write_to_file
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class MealyData:
    states: typing.List[str] = field(default_factory=list)
    input_to_transitions: typing.Dict[str, dict] = field(
        default_factory=lambda: defaultdict(dict))  # symbol -> current state -> next state/output

@dataclass
class MooreData:
    states: typing.List[str] = field(default_factory=list)
    state_output: typing.Dict[str, str] = field(default_factory=dict)  # state -> output
    input_to_transitions: typing.Dict[str, dict] = field(
        default_factory=lambda: defaultdict(dict))  # symbol -> current state -> next state/current output
    

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
        moore_data.states.append(state)
        moore_data.state_output[state] = output

    # Save transitions
    for transitions in input_data.splitlines()[2:]:
        input_symbol = transitions.split(";")[0].strip()

        for i, transition in enumerate(transitions.split(";")[1:]):
            next_state = transition.strip()
            current_state = list(moore_data.state_output.keys())[i]
            output = moore_data.state_output[current_state]
            moore_data.input_to_transitions[input_symbol][current_state] = f"{next_state}/{output}"
    
    return moore_data


def split_states_in_groups(
        states: typing.Union[typing.List[str], typing.Dict[str, typing.List]],
        inputs: typing.Dict[str, typing.Dict],
        prev_state_to_group: typing.Optional[typing.Dict[str, str]] = None
        ) -> typing.Tuple[typing.Dict[str, typing.List], typing.Dict[str, typing.List], typing.Dict[str, str]]:
    
    groups: typing.Dict[str, list] = defaultdict(list)  # group name -> list of states
    group_outputs: typing.Dict[str, typing.List] = dict()  # group name -> list of outputs
    state_to_group: typing.Dict[str, str] = dict()  # state -> group name (key of groups)
    
    def do_split(state: str, group_prefix = '_ '):  # prefix needed to make sure that different group elements won't merge
        group_symbols = [group_prefix]
        outputs = []

        for symbol in inputs:
            if prev_state_to_group is None:  # if first splitting
                group_symbol = inputs[symbol][state].split('/')[1]
                group_symbols.append(group_symbol)
                continue

            group_symbol = inputs[symbol][state].split('/')[0]
            outputs.append(inputs[symbol][state].split('/')[1])

            group_name = prev_state_to_group[group_symbol]
            group_symbol = list(dict.fromkeys(prev_state_to_group.values())).index(group_name)
            group_symbols.append(str(group_symbol))
        
        group_symbols_str = ' '.join(group_symbols)
        groups[group_symbols_str].append(state)
        group_outputs[group_symbols_str] = outputs
        state_to_group[state] = group_symbols_str

    # print('PREV', str(prev_state_to_group))

    if isinstance(states, list):
        for state in states:
            do_split(state)
    else:
        for i, group in enumerate(states, start=1):
            for state in states[group]:
                do_split(state, f'\{i}')

    # print(str(groups))

    return groups, group_outputs, state_to_group


def make_groups(data: typing.Union[MealyData, MooreData]) -> typing.Tuple[
    typing.Dict[str, typing.List], typing.Dict[str, typing.List], typing.Dict[str, str]]:

    # First - split states by their outputs
    groups, _, state_to_group = split_states_in_groups(
        data.states, data.input_to_transitions)

    # Second - replace transitions with groups
    groups, _, state_to_group = split_states_in_groups(
            groups, data.input_to_transitions, state_to_group)
    
    # Third - minimize until groups stop splitting
    while True:
        new_groups, group_outputs, state_to_group = split_states_in_groups(
            groups, data.input_to_transitions, state_to_group)
        
        groups_equal = str(new_groups) == str(groups)
        groups = new_groups

        if groups_equal:
            break
    
    return groups, group_outputs


def minimize_mealy(input_file, output_file):
    mealy_data = read_mealy(input_file)
    groups, group_outputs = make_groups(mealy_data)

    # New states
    states_line = [""]
    for i in range(len(groups)):
        states_line.append(f"X{i}")
    
    # Transitions
    transitions_lines = []

    for i, symbol in enumerate(mealy_data.input_to_transitions):
        line = [symbol]
        for group in groups:
            group_states = group.split(' ')[1:]
            state = "X" + str(group_states[i])
            output = group_outputs[group][i]
            line.append(f"{state}/{output}")
            
        transitions_lines.append(line)

    # Write to output
    write_to_file(output_file, states_line, transitions_lines)


def minimize_moore(input_file, output_file):
    moore_data = read_moore(input_file)
    groups, group_outputs = make_groups(moore_data)
    
    # Outputs & New states
    outputs_line = [""]
    states_line = [""]

    for i in range(len(groups)):
        states_line.append(f"X{i}")
        
        output = group_outputs[list(groups.keys())[i]][0]
        outputs_line.append(output)
    
    # Transitions
    transitions_lines = []

    for i, symbol in enumerate(moore_data.input_to_transitions):
        line = [symbol]
        for group in groups:
            group_states = group.split(' ')[1:]
            state = "X" + str(group_states[i])
            line.append(f"{state}")
            
        transitions_lines.append(line)

    # Write to output
    write_to_file(output_file, outputs_line, states_line, transitions_lines)