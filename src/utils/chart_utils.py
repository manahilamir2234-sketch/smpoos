"""
Static chart helpers using matplotlib and seaborn.

The assessment brief lists matplotlib and seaborn for berth utilisation,
congestion and environmental-style visualisations. These helpers write PNG
files that can be embedded in the report appendix.
"""

import os


def generate_static_analytics(system, output_dir):
    """
    Build a small set of static charts from live CSV-backed data.

    Returns a list of written file paths.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    os.makedirs(output_dir, exist_ok=True)
    written = []

    loc_df = system.get_locations_df()
    notif_df = system.get_notifications_df()

    # Berth / asset capacity by type
    fig, ax = plt.subplots(figsize=(8, 4))
    capacity = loc_df.groupby("type")["capacity_tonnes"].sum().reset_index()
    sns.barplot(data=capacity, x="type", y="capacity_tonnes", ax=ax, color="#0f766e")
    ax.set_title("Total Capacity by Location Type")
    ax.set_xlabel("Location type")
    ax.set_ylabel("Capacity (tonnes)")
    ax.tick_params(axis="x", rotation=25)
    path = os.path.join(output_dir, "berth_capacity.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    written.append(path)

    # Alert severity distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    order = ["Critical", "High", "Medium", "Low"]
    counts = notif_df["severity"].value_counts().reindex(order).fillna(0)
    sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="Reds_r")
    ax.set_title("Alert Severity Distribution")
    ax.set_ylabel("Count")
    path = os.path.join(output_dir, "alert_severity.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    written.append(path)

    # Simple activity heatmap by hour and severity
    fig, ax = plt.subplots(figsize=(8, 4))
    tmp = notif_df.copy()
    tmp["hour"] = tmp["timestamp"].astype(str).str[11:13]
    pivot = tmp.pivot_table(
        index="severity", columns="hour", values="notification_id",
        aggfunc="count", fill_value=0
    )
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd")
    ax.set_title("Alert Congestion Heatmap")
    path = os.path.join(output_dir, "route_analysis.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    written.append(path)

    return written
