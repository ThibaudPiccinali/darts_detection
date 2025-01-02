import matplotlib.pyplot as plt
import numpy as np

# Define dartboard parameters
radius = 215 # mm
inner_bull_radius = 6.35  # mm
outer_bull_radius = 15.9  # mm
inner_triple_radius = 99  # mm
outer_triple_radius = 107  # mm
inner_double_radius = 162  # mm
outer_double_radius = 170  # mm

# Define scoring segments
segments = 20  # Number of scoring segments (1 to 20)
angles = np.linspace(-2 * np.pi/20+2 * np.pi/40, 2 * np.pi + 2 * np.pi/40 - 2 * np.pi/20, segments + 1)
scores = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]

# Define colors for the segments and scoring areas
segment_colors = ['#FFFFFF', '#000000']  # Alternate white and black for the segments
triple_colors = ['#0F9536', '#E62F2B']  # Green for white sections, red for black sections
double_colors = ['#0F9536', '#E62F2B']  # Same as triple colors

# Create the dartboard
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-radius, radius)
ax.set_ylim(-radius, radius)
ax.set_aspect('equal')
ax.axis('off')

# Ajouter un cercle noir avec un rayon de 10 unités et centré à (0, 0)
circle = plt.Circle((0, 0), radius, color='black', zorder=0)
# Ajouter le cercle à l'axe
ax.add_artist(circle)

# Draw the scoring segments (full pie sections)
for i in range(segments):
    start_angle = angles[i]
    end_angle = angles[i + 1]
    segment_arc = np.linspace(start_angle, end_angle, 100)
    outer_arc = [(outer_double_radius * np.cos(a), outer_double_radius * np.sin(a)) for a in segment_arc]
    wedge = plt.Polygon(
        [(0, 0)] + outer_arc,
        closed=True,
        color=segment_colors[i % 2],
        zorder=0
    )
    ax.add_patch(wedge)

# Draw the inner and outer scoring areas (triple and double rings)
for i in range(segments):
    start_angle = angles[i]
    end_angle = angles[i + 1]
    triple_color = triple_colors[i % 2]
    double_color = double_colors[i % 2]

    # Triple ring
    triple_inner_arc = [(inner_triple_radius * np.cos(a), inner_triple_radius * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
    triple_outer_arc = [(outer_triple_radius * np.cos(a), outer_triple_radius * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
    triple_ring = plt.Polygon(
        triple_inner_arc + triple_outer_arc,
        closed=True,
        color=triple_color,
        zorder=1
    )
    ax.add_patch(triple_ring)

    # Double ring
    double_inner_arc = [(inner_double_radius * np.cos(a), inner_double_radius * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
    double_outer_arc = [(outer_double_radius * np.cos(a), outer_double_radius * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
    double_ring = plt.Polygon(
        double_inner_arc + double_outer_arc,
        closed=True,
        color=double_color,
        zorder=1
    )
    ax.add_patch(double_ring)

# Draw inner and outer rings for bullseye
bullseye_colors = ['#0F9536', '#E62F2B']  # Green for inner bull, red for outer bull
for radius, color in zip([outer_bull_radius,inner_bull_radius], bullseye_colors):
    bull = plt.Circle((0, 0), radius, color=color, zorder=2)
    ax.add_artist(bull)

# Annotate the scores
for i, score in enumerate(scores):
    angle = (angles[i] + angles[i + 1]) / 2
    x = (outer_double_radius + 15) * np.cos(angle)
    y = (outer_double_radius + 15) * np.sin(angle)
    ax.text(x, y, str(score), ha='center', va='center', fontweight='bold', fontsize=15, color='white')

plt.savefig("dartboard_image.png", bbox_inches='tight', pad_inches=0.1, transparent=True)
