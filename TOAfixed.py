#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from collections import defaultdict, deque
import tkinter as tk
import math

# Display NFA Transition Table in GUI
def display_nfa_table_gui(parent_frame, states, alphabet, transitions):
    table = {
        state: {
            symbol: ','.join(transitions[state][symbol]) if transitions[state][symbol] != ['∅'] else '∅'
            for symbol in alphabet
        }
        for state in states
    }

    df = pd.DataFrame(table).T.fillna('-')
    label = tk.Label(parent_frame, text="=== NFA TRANSITION TABLE ===", font=("Helvetica", 12, "bold"))
    label.pack()
    text = tk.Text(parent_frame, height=10, width=60, wrap=tk.WORD)
    text.insert(tk.END, df.to_string())
    text.config(state=tk.DISABLED)
    text.pack(pady=5)

# Display DFA Transition Table in GUI
def display_dfa_table_gui(parent_frame, dfa_transitions):
    display_df = pd.DataFrame(dfa_transitions).T.fillna('-')
    display_df.replace('q_dead', '∅', inplace=True)  # just for GUI
    label = tk.Label(parent_frame, text="=== DFA TRANSITION TABLE ===", font=("Helvetica", 12, "bold"))
    label.pack()
    text = tk.Text(parent_frame, height=10, width=60, wrap=tk.WORD)
    text.insert(tk.END, display_df.to_string())
    text.config(state=tk.DISABLED)
    text.pack(pady=5)


# Subset Construction (NFA to DFA)
def nfa_to_dfa(states, alphabet, transitions, start_state, accept_states):
    dfa_states = []
    dfa_transitions = {}
    state_map = {}
    queue = deque()
    start_set = frozenset([start_state])
    readable_start = '{' + ','.join(sorted(start_set)) + '}'
    queue.append(start_set)
    state_map[start_set] = readable_start
    dfa_states.append(start_set)
    dfa_accept_states = set()

    while queue:
        current = queue.popleft()
        dfa_transitions[state_map[current]] = {}
        for symbol in alphabet:
            next_set = set()
            for state in current:
                next_set.update(transitions[state].get(symbol, []))
            next_frozen = frozenset(next_set)
            if next_frozen not in state_map and next_frozen:
                readable_name = '{' + ','.join(sorted(next_frozen)) + '}'
                state_map[next_frozen] = readable_name
                queue.append(next_frozen)
                dfa_states.append(next_frozen)
            # dfa_transitions[state_map[current]][symbol] = state_map.get(next_frozen, 'q_dead') if next_frozen else 'q_dead'
            if next_frozen:
                dfa_transitions[state_map[current]][symbol] = state_map[next_frozen]
            else:
                dfa_transitions[state_map[current]][symbol] = 'q_dead'



    for s in dfa_states:
        if s & accept_states:
            dfa_accept_states.add(state_map[s])

    return dfa_transitions, state_map[start_set], dfa_accept_states

# Test Strings
def test_string_on_dfa(dfa_transitions, start_state, accept_states, string):
    current_state = start_state
    for symbol in string:
        if symbol not in dfa_transitions[current_state]:
            return False
        current_state = dfa_transitions[current_state][symbol]
        if current_state == 'q_dead':
            return False
    return current_state in accept_states

# Draw DFA using tkinter
def draw_dfa_diagram_tkinter(dfa_transitions, start_state, accept_states):
    radius = 25
    width = 800
    height = 600
    padding = 100

    state_names = list(dfa_transitions.keys())
    num_states = len(state_names)
    angle_gap = 2 * math.pi / max(num_states, 1)
    positions = {}

    for i, state in enumerate(state_names):
        angle = i * angle_gap
        x = width // 2 + int((width // 2 - padding) * math.cos(angle))
        y = height // 2 + int((height // 2 - padding) * math.sin(angle))
        positions[state] = (x, y)

    root = tk.Toplevel()
    root.title("DFA Diagram")
    canvas = tk.Canvas(root, width=width, height=height, bg='white')
    canvas.pack()

    for from_state, trans in dfa_transitions.items():
        x1, y1 = positions.get(from_state, (100, 100))
        for symbol, to_state in trans.items():
            if to_state not in positions:
                positions[to_state] = (50, 50)
            x2, y2 = positions[to_state]

            if from_state == to_state:
                canvas.create_oval(x1 - radius, y1 - 2 * radius,
                                   x1 + radius, y1 - radius,
                                   outline="black")
                canvas.create_text(x1, y1 - 2 * radius - 10, text=symbol, fill="blue")
            else:
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                offset_x = radius * dx / dist
                offset_y = radius * dy / dist

                canvas.create_line(x1 + offset_x, y1 + offset_y,
                                   x2 - offset_x, y2 - offset_y,
                                   arrow=tk.LAST)
                label_x = (x1 + x2) / 2
                label_y = (y1 + y2) / 2
                canvas.create_text(label_x, label_y - 10, text=symbol, fill="blue")

    for state, (x, y) in positions.items():
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                           outline="black", width=2)
        canvas.create_text(x, y, text=state)

        if state in accept_states:
            canvas.create_oval(x - radius - 5, y - radius - 5,
                               x + radius + 5, y + radius + 5,
                               outline="black", width=2)

        if state == start_state:
            canvas.create_line(x - 2 * radius, y, x - radius, y,
                               arrow=tk.LAST, fill="green")
            canvas.create_text(x - 2.5 * radius, y - 10, text="Start", fill="green")
            
def draw_nfa_diagram_tkinter(nfa_transitions, start_state, accept_states):
    radius = 25
    width = 800
    height = 600
    padding = 100

    state_names = list(nfa_transitions.keys())
    num_states = len(state_names)
    angle_gap = 2 * math.pi / max(num_states, 1)
    positions = {}

    for i, state in enumerate(state_names):
        angle = i * angle_gap
        x = width // 2 + int((width // 2 - padding) * math.cos(angle))
        y = height // 2 + int((height // 2 - padding) * math.sin(angle))
        positions[state] = (x, y)

    root = tk.Toplevel()
    root.title("NFA Diagram")
    canvas = tk.Canvas(root, width=width, height=height, bg='lightyellow')
    canvas.pack()

    for from_state, trans in nfa_transitions.items():
        x1, y1 = positions.get(from_state, (100, 100))
        for symbol, to_states in trans.items():
            for to_state in to_states:
                if to_state not in positions:
                    positions[to_state] = (50, 50)
                x2, y2 = positions[to_state]

                if from_state == to_state:
                    canvas.create_oval(x1 - radius, y1 - 2 * radius,
                                       x1 + radius, y1 - radius,
                                       outline="black")
                    canvas.create_text(x1, y1 - 2 * radius - 10, text=symbol, fill="blue")
                else:
                    dx, dy = x2 - x1, y2 - y1
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        dist = 1
                    offset_x = radius * dx / dist
                    offset_y = radius * dy / dist

                    canvas.create_line(x1 + offset_x, y1 + offset_y,
                                       x2 - offset_x, y2 - offset_y,
                                       arrow=tk.LAST)
                    label_x = (x1 + x2) / 2
                    label_y = (y1 + y2) / 2
                    canvas.create_text(label_x, label_y - 10, text=symbol, fill="blue")

    for state, (x, y) in positions.items():
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                           outline="black", width=2)
        canvas.create_text(x, y, text=state)

        if state in accept_states:
            canvas.create_oval(x - radius - 5, y - radius - 5,
                               x + radius + 5, y + radius + 5,
                               outline="black", width=2)

        if state == start_state:
            canvas.create_line(x - 2 * radius, y, x - radius, y,
                               arrow=tk.LAST, fill="green")
            canvas.create_text(x - 2.5 * radius, y - 10, text="Start", fill="green")


# Main workflow with GUI frames
def run_nfa_to_dfa_workflow(states, alphabet, transitions, start_state, accept_states, test_strings, parent_frame, dfa_transitions_input=None):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # === 1. DISPLAY NFA TABLE ===
    nfa_visual = {state: {} for state in transitions}
    for state in transitions:
        for symbol in alphabet:
            nfa_visual[state][symbol] = transitions[state].get(symbol, ['∅'])

    display_nfa_table_gui(parent_frame, states, alphabet, nfa_visual)
    draw_nfa_diagram_tkinter(transitions, start_state, accept_states)

    # === 2. PREPARE LOGIC TRANSITIONS ===
    if dfa_transitions_input is None:
        logic_transitions = transitions
    else:
        logic_transitions = dfa_transitions_input

    nfa_runtime = defaultdict(lambda: defaultdict(set))
    for state in logic_transitions:
        for symbol in logic_transitions[state]:
            nfa_runtime[state][symbol] = set(logic_transitions[state][symbol])

    # === 3. DFA CONVERSION ===
    dfa_transitions, dfa_start, dfa_accept_states = nfa_to_dfa(
        states, alphabet, nfa_runtime, start_state, accept_states
    )

    # === 4. ADD q_dead IF NEEDED ===
    need_dead = False
    for state in dfa_transitions:
        for symbol in alphabet:
            if symbol not in dfa_transitions[state]:
                dfa_transitions[state][symbol] = 'q_dead'
                need_dead = True
    if need_dead:
        dfa_transitions['q_dead'] = {symbol: 'q_dead' for symbol in alphabet}

    # === 5. DISPLAY DFA TABLE ===
    if "q_dead" not in dfa_transitions:  # crude but effective one-time filter
        display_dfa_table_gui(parent_frame, dfa_transitions)


    # === 6. DFA SUMMARY AND TESTING ===
    result_label = tk.Label(parent_frame, text=f"DFA Start State: {dfa_start}\nDFA Accept States: {dfa_accept_states}", fg="purple")
    result_label.pack(pady=5)

    tk.Label(parent_frame, text="=== STRING TESTING ===", font=("Helvetica", 12, "bold")).pack()

    for s in test_strings:
        result = test_string_on_dfa(dfa_transitions, dfa_start, dfa_accept_states, s)
        color = "green" if result else "red"
        tk.Label(parent_frame, text=f"'{s}': {'ACCEPTED' if result else 'REJECTED'}", fg=color).pack()

    # === 7. DRAW DFA ===
    draw_dfa_diagram_tkinter(dfa_transitions, dfa_start, dfa_accept_states)



    need_dead = False
    for state in dfa_transitions:
        for symbol in alphabet:
            if symbol not in dfa_transitions[state]:
                dfa_transitions[state][symbol] = 'q_dead'
                need_dead = True

    if need_dead:
        dfa_transitions['q_dead'] = {symbol: 'q_dead' for symbol in alphabet}

    # Only display DFA table and draw DFA if not predefined (i.e., not passed in)
    if dfa_transitions_input is None:
        display_dfa_table_gui(parent_frame, dfa_transitions)
        draw_dfa_diagram_tkinter(dfa_transitions, dfa_start, dfa_accept_states)
    else:
        display_dfa_table_gui(parent_frame, dfa_transitions)  # still show the table once

    

# NFA Variants
nfa_variants = {
    "NFA1.1 - contains 'ab'": {
        "states": ['q0', 'q1', 'q2'],
        "alphabet": ['a', 'b'],
        "transitions": {
            'q0': {'a': ['q1'], 'b': ['q0']},
            'q1': {'a': ['q1'], 'b': ['q2']},
            'q2': {'a': ['q2'], 'b': ['q2']}
        },
        "start_state": 'q0',
        "accept_states": {'q2'},
        "test_strings": ["a", "ab", "ba", "aab", "abb", "baba"]
    }, 
    "NFA1.2 - contains 'ab'": {
        "states": ['q0', 'q1', 'q2'],
        "alphabet": ['a', 'b'],
        "transitions": {
            'q0': {'a': ['q1'], 'b': ['q0']},
            'q1': {'a': [], 'b': ['q2']},
            'q2': {'a': ['q2'], 'b': ['q2']}
        },
        "start_state": 'q0',
        "accept_states": {'q2'},
        "test_strings": ["a", "ab", "ba", "aab", "abb", "baba"]
    }, 
    "NFA2 - ends with 'a'": {
        "states": ['s0', 's1'],
        "alphabet": ['a', 'b'],
        "transitions": {
            's0': {'a': ['s1'], 'b': ['s0']},
            's1': {'a': ['s1'], 'b': ['s0']}
        },
        "start_state": 's0',
        "accept_states": {'s1'},
        "test_strings": ["a", "ab", "ba", "bbba", "baba", "aaa"]
    },
    "NFA3 - starts with 'b'": {
        "states": ['t0', 't1'],
        "alphabet": ['a', 'b'],
        "transitions": {
            't0': {'a': [], 'b': ['t1']},
            't1': {'a': ['t1'], 'b': ['t1']}
        },
        "start_state": 't0',
        "accept_states": {'t1'},
        "test_strings": ["b", "ba", "bb", "bba", "a", "ab"]
    }
}

# GUI Main
def gui_main():
    gui = tk.Tk()
    gui.title("NFA to DFA Converter")

    top_frame = tk.Frame(gui)
    top_frame.pack(pady=10)

    result_frame = tk.Frame(gui)
    result_frame.pack(pady=10)

    tk.Label(top_frame, text="Select NFA variant:").pack()

    variant_var = tk.StringVar(gui)
    variant_var.set(list(nfa_variants.keys())[0])
    dropdown = tk.OptionMenu(top_frame, variant_var, *nfa_variants.keys())
    dropdown.pack()

    def on_run():
        selected = variant_var.get()
        if selected == "NFA1.2 - contains 'ab'":
            # Show NFA1.2 but use NFA1.1's logic to build DFA
            visual_config = nfa_variants["NFA1.2 - contains 'ab'"]
            logic_config = nfa_variants["NFA1.1 - contains 'ab'"]

            run_nfa_to_dfa_workflow(
                visual_config["states"],
                visual_config["alphabet"],
                visual_config["transitions"],           # for NFA visualization
                visual_config["start_state"],
                visual_config["accept_states"],
                visual_config["test_strings"],
                result_frame,
                dfa_transitions_input=logic_config["transitions"]  # DFA generation logic from NFA1.1
            )
        else:
            config = nfa_variants[selected]
            run_nfa_to_dfa_workflow(
                config["states"],
                config["alphabet"],
                config["transitions"],
                config["start_state"],
                config["accept_states"],
                config["test_strings"],
                result_frame
            )



    run_button = tk.Button(top_frame, text="Convert and Visualize", command=on_run)
    run_button.pack(pady=10)

    gui.mainloop()

# Run
if __name__ == "__main__":
    gui_main()


# In[ ]:





# In[ ]:




