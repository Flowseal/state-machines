import sys
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class StateDesc:
    final: bool = False
    transitions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

type StateMachine = dict[str, StateDesc]
EPSILON = "ε"
STATE_PREFIX = "S"
START_STATE_INDEX = 0


def read_state_matchine(file_name: str) -> tuple[StateMachine, str, str]:
    with open(file_name, "r", encoding="utf-8") as f:
        data = f.read().splitlines()
    
    state_machine: dict[str, StateDesc] = defaultdict(StateDesc)
    final_symbols = data[0].strip().split(";")
    states = data[1].strip().split(";")
    start_state = states[1]
    final_state = states[final_symbols.index("F")]
    
    for line in data[2:]:
        if not line.strip(): 
            continue

        line = line.strip().split(";")
        symbol = line[0]
        
        for i, transition in enumerate(line[1:], start=1):
            transition = transition.strip()
            state_machine[states[i]].final = final_state == states[i]
            state_machine[states[i]].transitions[symbol] = transition.split(",") if transition else []
    
    return state_machine, start_state, final_state


def get_epsilon_transitions(state_machine: StateMachine) -> dict:
    transitions = {}
    states = list(state_machine.keys())
    
    for state in states:
        visited, q = [], [state]
        while q:
            s = q.pop()
            if s not in visited:
                visited.append(s)
                q.extend(state_machine[s].transitions.get(EPSILON, []))

        transitions[state] = visited[:]

    return transitions


def eclosure(states, epsilon_transitions) -> list:
    eclosures_list = list()
    for state in states:
        eclosures_list.extend([state] + epsilon_transitions[state])

    return list(dict.fromkeys(eclosures_list))


def get_transitions_for_state(current_eclosure: list, symbol: str, state_machine: StateMachine) -> list[str]:
    transitions = []
    for s in current_eclosure:
        transitions.extend(state_machine[s].transitions[symbol])
    return list(dict.fromkeys(transitions))


def find_or_create_state(transitions: list[str], states_eclosures: dict[str, list[str]], states: list[str]) -> str:
    if not transitions:
        return ''
        
    for k, v in states_eclosures.items():
        if sorted(transitions) == sorted(v):
            return k
        
    new_state = f"{STATE_PREFIX}{len(states)+START_STATE_INDEX}"
    states.append(new_state)
    states_eclosures[new_state] = transitions
    return new_state


def determine_state_machine(state_machine: StateMachine, start_state: str, final_state: str) -> StateMachine:
    epsilon_transitions = get_epsilon_transitions(state_machine)
    states_eclosures = {f"{STATE_PREFIX}{START_STATE_INDEX}": [start_state]}
    states_to_process = [f"{STATE_PREFIX}{START_STATE_INDEX}"]
    determined_state_machine: StateMachine = defaultdict(StateDesc)

    for state in states_to_process:
        current_eclosure = eclosure(states_eclosures[state], epsilon_transitions)
        determined_state_machine[state].final = final_state in current_eclosure

        for symbol in state_machine[start_state].transitions:
            if symbol == EPSILON: continue

            transitions = get_transitions_for_state(current_eclosure, symbol, state_machine)
            next_state = find_or_create_state(transitions, states_eclosures, states_to_process)
            determined_state_machine[state].transitions[symbol] = [next_state]

    return determined_state_machine


def save_state_machine(state_machine: StateMachine, file_name: str) -> None:
    symbols = sorted({symbol for state in state_machine for symbol in state_machine[state].transitions})
    f_line = [""] + ["F" if state_machine[state].final else '' for state in state_machine]
    states_line = [""] + list(state_machine.keys())

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(';'.join(f_line) + "\n")
        f.write(';'.join(states_line) + "\n")
        for symbol in symbols:
            transitions = [state_machine[state].transitions[symbol][0] for state in states_line[1:]]
            f.write(';'.join([symbol] + transitions) + "\n")


def main():
    state_machine, start_state, final_state = read_state_matchine(sys.argv[1])
    determined_state_machine = determine_state_machine(state_machine, start_state, final_state)
    save_state_machine(determined_state_machine, sys.argv[2])


if __name__ == "__main__":
    sys.exit(main())