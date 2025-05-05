import math
import matplotlib
matplotlib.use("Agg")             # headless backend
import matplotlib.pyplot as plt

# ----------------- helper utilities -------------------------------------
def deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


def draw_ring(nodes, data, title, outfile):
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, polar=True)

    # Dashed circumference
    circle_theta = [i * math.pi / 180.0 for i in range(361)]
    ax.plot(circle_theta, [1.0] * len(circle_theta),
            linestyle="--", linewidth=0.7, color="#888888", zorder=0)

    # Sorted node angles for boundary "pizza slices"
    node_angles = sorted(nodes.values())
    for deg in node_angles:
        rad = deg2rad(deg)
        ax.plot([rad, rad], [0, 1],
                color="#bbbbbb", linewidth=0.8, zorder=0)

    # Node markers + labels
    for name, deg in nodes.items():
        rad = deg2rad(deg)
        ax.scatter(rad, 1, marker="o", s=90, zorder=3)
        ax.text(rad, 1.22, name, ha="center", va="center",
                fontsize=9, weight="bold", zorder=3)

    # Data key markers + labels
    if data:
        for key, deg in data.items():
            rad = deg2rad(deg)
            ax.scatter(rad, 1, marker="^", s=70, zorder=3)
            ax.text(rad, 0.88, key, ha="center", va="center",
                    fontsize=8, zorder=3)

    # Aesthetics
    ax.set_rticks([])
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.grid(False)

    # Manual title placement to avoid overlap
    fig.text(0.02, 0.95, title, ha="left", va="top",
             fontsize=11, weight="bold")

    fig.tight_layout()
    fig.savefig(outfile, dpi=120)
    plt.close(fig)


# ----------------- scenarios --------------------------------------------
nodes_abc   = {"Node A": 0, "Node B": 120, "Node C": 240}
nodes_add_d = {"Node A": 0, "Node D": 80,  "Node B": 120, "Node C": 240}
nodes_no_b  = {"Node A": 0, "Node D": 80,  "Node C": 240}

# Consistent key set
data_keys = {"K1": 100, "K2": 200, "K3": 330}

draw_ring(nodes_abc,   None,       "Nodes A, B, C",            "ring_nodes.png")
draw_ring(nodes_abc,   data_keys,  "Nodes + Data Keys",        "ring_nodes_data.png")
draw_ring(nodes_add_d, data_keys,  "Add Node D","ring_add_node_d.png")
draw_ring(nodes_no_b,  data_keys,  "Remove Node B",    "ring_remove_node_b.png")

print("✓ Diagrams generated:")
for png in ("ring_nodes.png", "ring_nodes_data.png",
            "ring_add_node_d.png", "ring_remove_node_b.png"):
    print("  └─ ", png)
