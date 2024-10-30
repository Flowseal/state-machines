import typing

from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class MealyData:
    states: typing.List[str] = field(default_factory=list)
    state_outputs: typing.Dict[str, typing.Set[str]] = field(
        default_factory=lambda: defaultdict(set))  # state -> set of produced output symbols
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


def split_states_in_groups(
        states: typing.Union[typing.List[str], typing.Dict[str, typing.List]],
        inputs: typing.Dict[str, typing.Dict],
        split_index: int
        ) -> typing.Tuple[typing.Dict[str, typing.List]]:
    
    groups: dict[str, list] = defaultdict(list)  # outputs -> list of states with these outputs
    group_names: dict[str, str] = dict()  # state -> group name (key of groups)
    
    def do_split(state: str):
        outputs = []
        for symbol in inputs:
            outputs.append(inputs[symbol][state].split('/')[split_index])
        
        outputs_str = ' '.join(outputs)
        groups[outputs_str].append(state)
        group_names[state] = outputs_str

    if isinstance(states, list):
        for state in states:
                do_split(state)
    else:
        for group in states:
            for state in states[group]:
                do_split(state)

    return groups


def minimize_mealy(input_file, output_file):
    mealy_data = read_mealy(input_file)
    SPLIT_BY_STATE = 0
    SPLIT_BY_OUTPUT = 1

    # First - split states by their outputs
    groups = split_states_in_groups(
        mealy_data.states, mealy_data.input_to_transitions, SPLIT_BY_OUTPUT)

    # Second - replace transitions with groups
    groups = split_states_in_groups(
            groups, mealy_data.input_to_transitions, SPLIT_BY_STATE)
    
    # Third - minimize until groups stop splitting
    while True:
        new_groups = split_states_in_groups(
            groups, mealy_data.input_to_transitions, SPLIT_BY_STATE)
        
        groups_equal = str(new_groups) == str(groups)
        groups = new_groups

        if groups_equal:
            break
    
    