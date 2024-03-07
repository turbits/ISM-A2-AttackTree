"""The main file for the ISM-A2-AttackTree application."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser
import math
import yaml


# =================== APP/ROOT SETUP ===================
root = tk.Tk()
# sizing and centering of window
# REF: Multiple Authors (2015). Stack Overflow: "How to center a window on the screen in Tkinter?". Available at: https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter [Accessed 05 March 2024] # pylint: disable=line-too-long
APP_WIDTH = 800
APP_HEIGHT = 500
APP_WIDTH_MIN = 500
APP_HEIGHT_MIN = 500
root.eval('tk::PlaceWindow . center')
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
xCoord = (screenWidth / 2) - (APP_WIDTH / 2)
yCoord = (screenHeight / 2) - (APP_HEIGHT / 2)
root.geometry("{}x{}+{}+{}".format(APP_WIDTH, APP_HEIGHT, int(xCoord), int(yCoord)))  # pylint: disable=consider-using-f-string
root.minsize(APP_WIDTH_MIN, APP_HEIGHT_MIN)
# other settings
root.title("ISM-A2-AttackTree")
root.iconbitmap("icon.ico")
# listen for esc keypress (temp indev hotkey to easily close program)
root.bind("<Escape>", lambda e: root.quit())


# region ============================ FUNCTIONS ============================
def open_link(url):
    """Open a link in the default web browser."""
    webbrowser.open_new(url)


# set the selected item values in the attack_tree to the entry fields
def on_select(event=None):  # pylint: disable=unused-argument
    """Sets the selected item field values when user selects a node in the treeview."""
    selected = attack_tree.focus()
    values = attack_tree.item(selected, "values")
    item_update_entry_field.delete(0, "end")
    probability_update_entry_field.delete(0, "end")
    cost_update_entry_field.delete(0, "end")
    item_update_entry_field.insert(0, attack_tree.item(selected, "text"))
    probability_update_entry_field.insert(0, values[0])
    cost_update_entry_field.insert(0, values[1])


# update buttons
def update_node():
    """Updates the selected node in the treeview with the values in the entry fields."""
    # get current selected item
    selected = attack_tree.focus()
    # update the selected item
    attack_tree.item(selected, text=item_update_entry_field.get(), values=(probability_update_entry_field.get(), cost_update_entry_field.get()))


# delete button
def delete_node():
    """Deletes the selected node in the treeview."""
    # get current selected item
    selected = attack_tree.focus()
    # delete the selected item
    attack_tree.delete(selected)


# add button
def add_node():
    """Adds a child node to the currently selected node with the values that are currently entered in the entry fields."""
    selected = attack_tree.focus()
    # get the entry values
    item = item_update_entry_field.get()
    probability = probability_update_entry_field.get()
    cost = cost_update_entry_field.get()

    if item == "" or probability == "" or cost == "":
        return
    # add a new item to the treeview under the selected item
    if selected:
        attack_tree.insert(selected, "end", item, text=item, values=(probability, cost))
        # clear the entry fields (commented this out, kinda annoying)
        # item_update_entry_field.delete(0, "end")
        # probability_update_entry_field.delete(0, "end")
        # cost_update_entry_field.delete(0, "end")
        # expand the selected node to show the new item
        attack_tree.item(selected, open=True)
    else:
        attack_tree.insert("", "end", item, text=item, values=(probability, cost))


# ============================ [UNIMPLEMENTED] PROMOTE/DEMOTE ============================
# This was sort of working but was more confusing than helpful, so I removed the associated buttons and obviously commented this block out. This is just for reference.
# ============================
# def promote_node(item_id):
#     tree = attack_tree
#     parent_id = tree.parent(item_id)
#     if not parent_id:
#         # already at root level
#         return

#     index = tree.index(parent_id)
#     tree.move(item_id, '', index)
#     # update children parent_id to match new parents id
#     children = tree.get_children(item_id)
#     for child_id in children:
#         tree.move(child_id, item_id, 'end')


# def demote_node(item_id):
#     tree = attack_tree
#     previous_sibling_id = tree.prev(item_id)
#     if not previous_sibling_id:
#         # already at bottom level
#         return

#     tree.move(item_id, previous_sibling_id, 'end')


# def add_promotedemote_buttons_to_tree():
#     for item_id in attack_tree.get_children(''):
#         promoteButton = tk.Button(attack_tree, text=">", command=lambda item_id=item_id: promote_node(item_id))
#         promoteButton.place(relx=0.0, rely=0.5, anchor="w")
#         demoteButton = tk.Button(attack_tree, text="<", command=lambda item_id=item_id: demote_node(item_id))
#         demoteButton.place(relx=0.0, rely=0.5, anchor="w")


def load_from_yaml():
    """Load an attack tree from a YAML file."""
    tree = attack_tree

    def deserialize_node(data, parent=''):
        for text, node_data in data.items():
            if isinstance(node_data, dict):
                values = (node_data['probability'], node_data['cost'])
                new_node = tree.insert(parent, "end", text=text, values=values)
                children_data = node_data['children'] if 'children' in node_data else node_data
                deserialize_node(children_data, new_node)
            elif isinstance(node_data, int):
                tree.insert(parent, 'end', values=(node_data, 0), text=text)
            elif isinstance(node_data, float):
                tree.insert(parent, 'end', values=(node_data, 0), text=text)
            else:
                tree.insert(parent, 'end', values=(node_data['probability'], node_data['cost']), text=text)
    # tree.delete(*tree.get_children())
    filename = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml")])
    if filename:
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            deserialize_node(data)

    expand_all_nodes()


def save_to_yaml():
    """Save the attack tree to a YAML file."""
    tree = attack_tree

    def serialize_node(tree, node):
        item = tree.item(node)
        text = item['text']
        values = item['values']
        children = tree.get_children(node)
        if children:
            children_data = {}
            for child in children:
                children_data.update(serialize_node(tree, child))
            return {text: {'probability': float(values[0]), 'cost': float(values[1]), **children_data}}
        else:
            return {text: {'probability': float(values[0]), 'cost': float(values[1])}}

    root_children = tree.get_children('')
    data = {}
    for child in root_children:
        data.update(serialize_node(tree, child))

    # open save file dialog
    filename = filedialog.asksaveasfilename(defaultextension=".yaml", filetypes=[("YAML files", "*.yaml")])
    if filename:
        with open(filename, "w", encoding="utf-8") as file:
            yaml.dump(data, file, default_flow_style=False, default_style='', sort_keys=True)


def calculate_totals(tree, _rating_value, _rating_value_raw, prob_value, cost_value, prob_avg_value, cost_avg_value):  # pylint: disable=too-many-locals
    """Calculate the total and average probability and cost of the attack tree."""
    num_nodes = 0
    total_probability = 0
    total_cost = 0
    avg_probability = 0
    avg_cost = 0
    stack = ['']

    while stack:
        item_id = stack.pop()
        children = tree.get_children(item_id)
        for child_id in children:
            values = tree.item(child_id, "values")
            if values:
                probability, cost = map(float, values)
                total_probability += probability
                total_cost += cost

            stack.append(child_id)
            num_nodes += 1

    if num_nodes == 0:
        return

    avg_probability = total_probability / num_nodes
    avg_cost = total_cost / num_nodes
    rating_letter, rating_raw = calculate_rating(avg_probability, avg_cost)

    # update the totals labels
    prob_value.config(text=str("{:.2f}%".format(total_probability)))  # pylint: disable=consider-using-f-string
    cost_value.config(text=str("${:.2f}".format(total_cost)))  # pylint: disable=consider-using-f-string
    prob_avg_value.config(text=str("{:.2f}%".format(avg_probability)))  # pylint: disable=consider-using-f-string
    cost_avg_value.config(text=str("${:.2f}".format(avg_cost)))  # pylint: disable=consider-using-f-string
    _rating_value.config(text=str(rating_letter))
    _rating_value_raw.config(text=str(rating_raw))


def expand_all_nodes(item_id=''):
    """Expands all nodes in the treeview."""
    tree = attack_tree
    children = tree.get_children(item_id)
    for child in children:
        tree.item(child, open=True)
        expand_all_nodes(child)


def collapse_all_nodes(item_id=''):
    """Collapses all nodes in the treeview."""
    tree = attack_tree
    children = tree.get_children(item_id)
    for child in children:
        tree.item(child, open=False)
        collapse_all_nodes(child)


# delete all nodes function with confirmation dialog box
def delete_all_nodes():
    """Deletes all nodes in the treeview with a confirmation dialog box."""
    if tk.messagebox.askyesno("Delete the entire tree", "Are you sure you want to delete all nodes in this tree (IRREVERSIBLE)?"):
        attack_tree.delete(*attack_tree.get_children(''))


def calculate_rating(probability_avg, cost_avg):
    """Calculate totally arbitrary rating of the attack tree based on the sum of the average probability and cost divided by 100."""
    rating_raw = math.ceil(probability_avg + cost_avg / 100)
    rating_letter = 'X'
    if rating_raw >= 0 and rating_raw <= 499:
        rating_letter = 'AA'
    elif rating_raw >= 500 and rating_raw <= 999:
        rating_letter = 'A'
    elif rating_raw >= 1000 and rating_raw <= 1499:
        rating_letter = 'B'
    elif rating_raw >= 1500 and rating_raw <= 2499:
        rating_letter = 'C'
    elif rating_raw >= 2500 and rating_raw <= 3999:
        rating_letter = 'D'
    elif rating_raw >= 4000 and rating_raw <= 7999:
        rating_letter = 'E'
    elif rating_raw >= 8000:
        rating_letter = 'F'
    return rating_letter, rating_raw

# endregion ============================ END FUNCTIONS ============================


# =================== HEADER ===================
label = tk.Label(root, text="Attack Tree", font=("Arial", 20, "bold"))
label.pack(side="top", fill="x")
label_sub = tk.Label(root, text="Information Security Management - Assignment 2", font=("Arial", 10))
label_sub.pack(side="top", fill="x")
label_author = tk.Label(root, text="Trevor Woodman", font=("Arial", 10))
label_author.pack(side="top", fill="x")
label_author_sub = tk.Label(root, text="https://github.com/turbits/ISM-A2-AttackTree", fg="#4e757a", font=("Arial", 10), cursor="hand2")
label_author_sub.pack(side="top")
label_author_sub.bind("<Button-1>", lambda e: open_link("https://github.com/turbits/ISM-A2-AttackTree"))


# =================== TREEVIEW SETUP ===================
# setting columns, layout, etc. selectmode browse is only allowing single node selection
attack_tree = ttk.Treeview(root, columns=("probability", "cost"), selectmode="browse")
attack_tree.heading("#0", text="Item")
attack_tree.heading("probability", text="Probability (%)")
attack_tree.heading("cost", text="Cost ($)")
attack_tree.pack(side="top", fill="both", expand=True)
# this adds a scrollbar to the treeview
at_scroll = ttk.Scrollbar(attack_tree, orient="vertical", command=attack_tree.yview)
at_scroll.pack(side="right", fill="y")
attack_tree.configure(yscrollcommand=at_scroll.set)


# =================== TEST DATA SEED ===================
# attack_tree.insert("", "end", "node1", text="Node 1", values=(63, 45))
# attack_tree.insert("node1", "end", "node1.1", text="Node 1.1", values=(0.69, 3535))
# attack_tree.insert("node1", "end", "node1.2", text="Node 1.2", values=(63, 102550))
# attack_tree.insert("node1.1", "end", "node1.1.1", text="Node 1.1.1", values=(0.9, 567777))
# attack_tree.insert("node1.1", "end", "node1.1.2", text="Node 1.1.2", values=(23.59, 1))
# attack_tree.insert("node1.2", "end", "node1.2.1", text="Node 1.2.1", values=(90.99, 10140))
# attack_tree.insert("node1.2", "end", "node1.2.2", text="Node 1.2.2", values=(63, 10560))
# expand_all_nodes()


# =================== BOTTOM SECTION ===================
bottom_frame = tk.Frame(root)
bottom_frame.pack(side="bottom", pady=20, fill="both")
bottom_left_frame = tk.Frame(bottom_frame)
bottom_left_frame.pack(side="left", padx=20, fill="both")
bottom_right_frame = tk.Frame(bottom_frame)
bottom_right_frame.pack(side="right", padx=20, fill="both")


# =================== UPDATE RECORDS SECTION ===================
# set up of update records section
update_records_frame = tk.Frame(bottom_left_frame)
update_records_frame.pack(side="bottom", fill="x")
update_records_button_frame = tk.Frame(bottom_left_frame)
update_records_button_frame.pack(side="top", fill="x", anchor="w")

# update section labels and entry fields
item_update_label = tk.Label(update_records_frame, text="Item:")
item_update_label.grid(row=0, column=0)
item_update_entry_field = tk.Entry(update_records_frame)
item_update_entry_field.grid(row=0, column=1)

probability_update_label = tk.Label(update_records_frame, text="Probability:")
probability_update_label.grid(row=1, column=0)
probability_update_entry_field = tk.Entry(update_records_frame)
probability_update_entry_field.grid(row=1, column=1)

cost_update_label = tk.Label(update_records_frame, text="Cost:")
cost_update_label.grid(row=2, column=0)
cost_update_entry_field = tk.Entry(update_records_frame)
cost_update_entry_field.grid(row=2, column=1)

# update records section buttons
add_button = tk.Button(update_records_button_frame, text="Add Node", command=add_node)
add_button.grid(row=0, column=0, sticky="ew")

update_button = tk.Button(update_records_button_frame, text="Update Node", command=update_node)
update_button.grid(row=1, column=0, sticky="ew")

delete_button = tk.Button(update_records_button_frame, text="Delete Node", command=delete_node)
delete_button.grid(row=2, column=0, sticky="ew")

save_tree_button = tk.Button(update_records_button_frame, text="Save Tree", command=save_to_yaml)
save_tree_button.grid(row=0, column=1, sticky="ew")

load_tree_button = tk.Button(update_records_button_frame, text="Load Tree", command=load_from_yaml)
load_tree_button.grid(row=1, column=1, sticky="ew")

expand_all_nodes_button = tk.Button(update_records_button_frame, text="Expand All", command=expand_all_nodes)
expand_all_nodes_button.grid(row=0, column=3, sticky="ew")

collapse_all_nodes_button = tk.Button(update_records_button_frame, text="Collapse All", command=collapse_all_nodes)
collapse_all_nodes_button.grid(row=1, column=3, sticky="ew")

delete_all_nodes_button = tk.Button(update_records_button_frame, text="Delete Tree⚠️", command=delete_all_nodes)
delete_all_nodes_button.grid(row=2, column=3, sticky="ew")


# =================== STATS AND RESULTS SECTION ===================
statsFrame = tk.Frame(bottom_right_frame)
statsFrame.pack(fill="both")

rating_label = tk.Label(statsFrame, text="Rating:", font=("Arial", 12, "bold"))
rating_label.grid(row=1, column=0)
rating_value = tk.Label(statsFrame, text="X", font=("Arial", 12, "bold"))
rating_value.grid(row=1, column=1)

rating_label_raw = tk.Label(statsFrame, text="Rating (Raw):")
rating_label_raw.grid(row=2, column=0)
rating_value_raw = tk.Label(statsFrame, text="0")
rating_value_raw.grid(row=2, column=1)

average_probability_label = tk.Label(statsFrame, text="Average Probability:")
average_probability_label.grid(row=3, column=0)
average_probability_value = tk.Label(statsFrame, text="0")
average_probability_value.grid(row=3, column=1)

average_cost_label = tk.Label(statsFrame, text="Average Cost:")
average_cost_label.grid(row=4, column=0)
average_cost_value = tk.Label(statsFrame, text="0")
average_cost_value.grid(row=4, column=1)

total_probability_label = tk.Label(statsFrame, text="Total Probability:")
total_probability_label.grid(row=5, column=0)
total_probability_value = tk.Label(statsFrame, text="0")
total_probability_value.grid(row=5, column=1)

total_cost_label = tk.Label(statsFrame, text="Total Cost:")
total_cost_label.grid(row=6, column=0)
total_cost_value = tk.Label(statsFrame, text="0")
total_cost_value.grid(row=6, column=1)

# stats section buttons
calculate_totals_button = tk.Button(statsFrame, text="Calculate Totals", command=lambda: calculate_totals(attack_tree, rating_value, rating_value_raw, total_probability_value, total_cost_value, average_probability_value, average_cost_value))
calculate_totals_button.grid(row=7, column=0, columnspan=4, sticky="ew")


# ============================ EVENT BINDING/MISC ============================
# when the user selects something in the treeview, it will run the on_select function (sets the entry fields to the selected item values)
attack_tree.bind("<<TreeviewSelect>>", lambda: on_select)


# ============================ MAIN ============================
def main():
    """The main function for the ISM-A2-AttackTree application."""
    # run app
    root.mainloop()


if __name__ == "__main__":
    main()
