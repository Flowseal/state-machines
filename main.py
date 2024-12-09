import re
import sys
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class StateDesc:
    final: bool = False
    transitions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


def grammar_to_states(raw_gramma: str, pattern: re.Pattern, transitions_pattern: re.Pattern, is_right: bool = True) -> tuple[dict[str, StateDesc], str]:
    start_state = pattern.findall(raw_gramma)[0][0]
    states: dict[str, StateDesc] = defaultdict(StateDesc)
    states["H" if is_right else start_state] = StateDesc(final=True)

    for match in pattern.finditer(raw_gramma):
        state = match.group(1)
        transitions = match.group(2).split("|")

        if state not in states:
            states[state] = StateDesc()

        for transition in transitions:
            match_transition = transitions_pattern.search(transition)

            if is_right:
                symbol = match_transition.group(1)
                next_state = match_transition.group(2) or "H"
                states[state].transitions[symbol].append(next_state)
            else:
                symbol = match_transition.group(2)
                next_state = match_transition.group(1) or "H"
                states[next_state].transitions[symbol].append(state)
    
    return states, start_state if is_right else "H"


def save_states(states: dict[str, StateDesc], output_file, start_state):
    states_list = [start_state] + list(states.keys())
    states_list = list(dict.fromkeys(states_list))
    symbols_list = sorted({symbol for state in states for symbol in states[state].transitions})

    f_line = [''] + ['F' if states[state].final else '' for state in states_list]
    states_line = [''] + [f'q{i}' for i in range(len(states_list))]
    state_index_map = {state: f'q{i}' for i, state in enumerate(states_list)}

    transitions_lines = []
    for symbol in symbols_list:
        row = [symbol] + [''] * len(states_list)
        for state in states_list:
            state_index = states_list.index(state) + 1
            transitions = states[state].transitions.get(symbol, [])
            row[state_index] = ",".join(state_index_map[next_state] for next_state in transitions)
        transitions_lines.append(row)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(';'.join(f_line) + "\n")
        f.write(';'.join(states_line) + "\n")
        for row in transitions_lines:
            f.write(';'.join(row) + "\n")


def parse_grammar(raw_grammar: str):
    rules_count = raw_grammar.count("->")
    left_pattern = re.compile(r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$", re.MULTILINE)
    right_pattern = re.compile(r"^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$", re.MULTILINE)

    if rules_count == len(re.findall(left_pattern, raw_grammar)):
        transitions_pattern = re.compile(r"^\s*(?:<(\w*)>)?\s*([\wε]*)\s*$")
        return grammar_to_states(raw_grammar, left_pattern, transitions_pattern, is_right=False)
    else:
        transitions_pattern = re.compile(r"^\s*([\wε]*)\s*(?:<(\w*)>)?\s*$")
        return grammar_to_states(raw_grammar, right_pattern, transitions_pattern, is_right=True)


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as file:
        input_text = file.read()
    
    states, start_state = parse_grammar(input_text)
    save_states(states, sys.argv[2], start_state)


if __name__ == "__main__":
    main()