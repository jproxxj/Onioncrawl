from pyvis.network import Network
import json

# Load data
with open("db_dump.json", "r") as f:
    data = json.load(f)

# Create Network object
net = Network(
    height="800px",
    width="100%",
    directed=True,
    bgcolor="#111111",
    font_color="white"
)

# Add nodes with smaller size and labels
for item in data:
    node = item.get("domain")
    parent = item.get("parent")
    label = item.get("header") or node

    if not node:
        continue

    net.add_node(
        node,
        label=label[:20],   # shorter labels
        title=node,         # tooltip for full domain
        size=5               # smaller nodes
    )

    # Add edges
    if parent:
        net.add_node(parent, label=parent[:20], title=parent)
        net.add_edge(parent, node)

# Apply the Barnes-Hut physics simulation (best for large graphs)
net.barnes_hut(gravity=-8000, central_gravity=0.3)

# Enable physics (for layout)
net.toggle_physics(True)

# Optional: Show control buttons for user interaction (zoom, pan)
net.show_buttons()

# Now, generate HTML to visualize the graph
net.write_html("graph.html")  # Use .show to render the graph interactively
