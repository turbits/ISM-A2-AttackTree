"""The main file for the ISM-A2-AttackTree application."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser
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
def on_select():
    """Sets the selected item field values when user selects a node in the treeview."""
    selected = attack_tree.focus()
    values = attack_tree.item(selected, "values")
    itemUpdateEntry.delete(0, "end")
    probabilityUpdateEntry.delete(0, "end")
    costUpdateEntry.delete(0, "end")
    itemUpdateEntry.insert(0, attack_tree.item(selected, "text"))
    probabilityUpdateEntry.insert(0, values[0])
    costUpdateEntry.insert(0, values[1])


# update buttons
def update_node():
    """Updates the selected node in the treeview with the values in the entry fields."""
    # get current selected item
    selected = attack_tree.focus()
    # update the selected item
    attack_tree.item(selected, text=itemUpdateEntry.get(), values=(probabilityUpdateEntry.get(), costUpdateEntry.get()))


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
    item = itemUpdateEntry.get()
    probability = probabilityUpdateEntry.get()
    cost = costUpdateEntry.get()

    if item == "" or probability == "" or cost == "":
        return
    # add a new item to the treeview under the selected item
    if selected:
        attack_tree.insert(selected, "end", item, text=item, values=(probability, cost))
        # clear the entry fields (commented this out, kinda annoying)
        # itemUpdateEntry.delete(0, "end")
        # probabilityUpdateEntry.delete(0, "end")
        # costUpdateEntry.delete(0, "end")
        # expand the selected node to show the new item
        attack_tree.item(selected, open=True)
    else:
        attack_tree.insert("", "end", item, text=item, values=(probability, cost))


# ============================ [UNIMPLEMENTED] PROMOTE/DEMOTE ============================
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


def calculate_totals(prob_label, cost_label, prob_avg_label, cost_avg_label):
    """Calculate the total and average probability and cost of the attack tree."""
    tree = attack_tree
    print("calculating totals")

    num_nodes = 0
    total_probability = 0
    total_cost = 0
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

    # update the totals labels
    prob_label.config(text=str("{:.2f}%".format(total_probability)))  # pylint: disable=consider-using-f-string
    cost_label.config(text=str("${:.2f}".format(total_cost)))  # pylint: disable=consider-using-f-string
    prob_avg_label.config(text=str("{:.2f}%".format(total_probability / num_nodes)))  # pylint: disable=consider-using-f-string
    cost_avg_label.config(text=str("${:.2f}".format(total_cost / num_nodes)))  # pylint: disable=consider-using-f-string


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

# endregion ============================ END FUNCTIONS ============================


# =================== HEADER ===================
label = tk.Label(root, text="Attack Tree", font=("Arial", 20, "bold"))
label.pack(side="top", fill="x")
labelSub = tk.Label(root, text="Information Security Management - Assignment 2", font=("Arial", 10))
labelSub.pack(side="top", fill="x")
labelAuthor = tk.Label(root, text="Trevor Woodman", font=("Arial", 10))
labelAuthor.pack(side="top", fill="x")
labelAuthor2 = tk.Label(root, text="https://github.com/turbits/ISM-A2-AttackTree", fg="#4e757a", font=("Arial", 10), cursor="hand2")
labelAuthor2.pack(side="top")
labelAuthor2.bind("<Button-1>", lambda e: open_link("https://github.com/turbits/ISM-A2-AttackTree"))


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
attack_tree.insert("", "end", "node1", text="Node 1", values=(63, 45))
attack_tree.insert("node1", "end", "node1.1", text="Node 1.1", values=(0.69, 3535))
attack_tree.insert("node1", "end", "node1.2", text="Node 1.2", values=(63, 102550))
attack_tree.insert("node1.1", "end", "node1.1.1", text="Node 1.1.1", values=(0.9, 567777))
attack_tree.insert("node1.1", "end", "node1.1.2", text="Node 1.1.2", values=(23.59, 1))
attack_tree.insert("node1.2", "end", "node1.2.1", text="Node 1.2.1", values=(90.99, 10140))
attack_tree.insert("node1.2", "end", "node1.2.2", text="Node 1.2.2", values=(63, 10560))
expand_all_nodes()

# =================== UPDATE RECORDS SECTION ===================
# set up of update records section
updateRecordsFrame = tk.Frame(root)
updateRecordsFrame.pack(side="bottom", fill="x")
updateRecordsButtonsFrame = tk.Frame(root)
updateRecordsButtonsFrame.pack(side="bottom", fill="x")

# update section labels and entry fields
itemUpdateLabel = tk.Label(updateRecordsFrame, text="Item:")
itemUpdateLabel.grid(row=0, column=0)
itemUpdateEntry = tk.Entry(updateRecordsFrame)
itemUpdateEntry.grid(row=0, column=1)

probabilityUpdateLabel = tk.Label(updateRecordsFrame, text="Probability:")
probabilityUpdateLabel.grid(row=1, column=0)
probabilityUpdateEntry = tk.Entry(updateRecordsFrame)
probabilityUpdateEntry.grid(row=1, column=1)

costUpdateLabel = tk.Label(updateRecordsFrame, text="Cost:")
costUpdateLabel.grid(row=2, column=0)
costUpdateEntry = tk.Entry(updateRecordsFrame)
costUpdateEntry.grid(row=2, column=1)

# calculate totals labels
totalProbabilityLabel = tk.Label(updateRecordsFrame, text="Total Probability:")
totalProbabilityLabel.grid(row=3, column=0)
totalProbabilityValue = tk.Label(updateRecordsFrame, text="0")
totalProbabilityValue.grid(row=3, column=1)

totalCostLabel = tk.Label(updateRecordsFrame, text="Total Cost:")
totalCostLabel.grid(row=4, column=0)
totalCostValue = tk.Label(updateRecordsFrame, text="0")
totalCostValue.grid(row=4, column=1)

averageProbabilityLabel = tk.Label(updateRecordsFrame, text="Average Probability:")
averageProbabilityLabel.grid(row=5, column=0)
averageProbabilityValue = tk.Label(updateRecordsFrame, text="0")
averageProbabilityValue.grid(row=5, column=1)

averageCostLabel = tk.Label(updateRecordsFrame, text="Average Cost:")
averageCostLabel.grid(row=6, column=0)
averageCostValue = tk.Label(updateRecordsFrame, text="0")
averageCostValue.grid(row=6, column=1)


# ============================ BUTTONS ============================
# set up buttons
addButton = tk.Button(updateRecordsButtonsFrame, text="Add", command=add_node)
addButton.grid(row=0, column=2, sticky="ew")
updateButton = tk.Button(updateRecordsButtonsFrame, text="Update", command=update_node)
updateButton.grid(row=0, column=0, sticky="ew")
deleteButton = tk.Button(updateRecordsButtonsFrame, text="Delete", command=delete_node)
deleteButton.grid(row=0, column=1, sticky="ew")
loadButton = tk.Button(updateRecordsButtonsFrame, text="Load", command=load_from_yaml)
loadButton.grid(row=1, column=0, sticky="ew")
saveButton = tk.Button(updateRecordsButtonsFrame, text="Save", command=save_to_yaml)
saveButton.grid(row=1, column=1, sticky="ew")
# calculate totals button
calculateTotalsButton = tk.Button(updateRecordsButtonsFrame, text="Calculate Totals", command=calculate_totals(totalProbabilityValue, totalCostValue, averageProbabilityValue, averageCostValue))
calculateTotalsButton.grid(row=1, column=2, sticky="ew")
# expand all nodes button
expandAllButton = tk.Button(updateRecordsButtonsFrame, text="Expand All", command=expand_all_nodes)
expandAllButton.grid(row=0, column=3, sticky="ew")
# collapse all nodes button
collapseAllButton = tk.Button(updateRecordsButtonsFrame, text="Collapse All", command=collapse_all_nodes)
collapseAllButton.grid(row=1, column=3, sticky="ew")


# ============================ EVENT BINDING/MISC ============================
# when the user selects something in the treeview, it will run the on_select function (sets the entry fields to the selected item values)
attack_tree.bind("<<TreeviewSelect>>", on_select)


# ============================ MAIN ============================
def main():
    """The main function for the ISM-A2-AttackTree application."""
    # run app
    root.mainloop()


if __name__ == "__main__":
    main()
