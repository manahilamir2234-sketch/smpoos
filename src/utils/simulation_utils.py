"""
SMPOOS Real-Time Simulation Utilities
Provides functions for simulating live data changes in the port operations system.
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List


def simulate_berth_occupancy_change(locations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulate changes in berth occupancy and capacity.

    Args:
        locations_df: Current locations DataFrame

    Returns:
        Updated DataFrame with simulated changes
    """
    df = locations_df.copy()

    # Only modify berth-type locations
    berth_mask = df['type'] == 'Berth'
    berths = df[berth_mask]

    if len(berths) == 0:
        return df

    # Randomly select 1-2 berths to change status
    num_changes = random.randint(1, min(2, len(berths)))
    selected_indices = random.sample(berths.index.tolist(), num_changes)

    for idx in selected_indices:
        current_status = df.loc[idx, 'status']

        # Randomly change status
        status_changes = {
            'Active': ['Under Maintenance', 'Active'],
            'Under Maintenance': ['Active', 'Under Maintenance'],
            'Inactive': ['Active', 'Inactive']
        }

        if current_status in status_changes:
            new_status = random.choice(status_changes[current_status])
            df.loc[idx, 'status'] = new_status

        # Slightly adjust capacity (±5%)
        current_capacity = df.loc[idx, 'capacity_tonnes']
        change_factor = random.uniform(0.95, 1.05)
        df.loc[idx, 'capacity_tonnes'] = round(
            current_capacity * change_factor, 2)

    return df


def simulate_route_traffic(routes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulate changes in route status and traffic.

    Args:
        routes_df: Current routes DataFrame

    Returns:
        Updated DataFrame with simulated changes
    """
    df = routes_df.copy()

    if len(df) == 0:
        return df

    # Randomly select 1 route to change status
    idx = random.randint(0, len(df) - 1)
    current_status = df.loc[idx, 'status']

    # Status transition logic
    status_transitions = {
        'Open': ['Open', 'Open', 'Restricted'],  # More likely to stay open
        'Restricted': ['Open', 'Restricted', 'Closed'],
        'Closed': ['Restricted', 'Closed']
    }

    if current_status in status_transitions:
        new_status = random.choice(status_transitions[current_status])
        df.loc[idx, 'status'] = new_status

    return df


def generate_random_notification(system) -> Dict:
    """
    Generate a random notification/alert.

    Args:
        system: SMPOOS system instance

    Returns:
        Dictionary with notification data
    """
    alert_types = [
        "Equipment Failure",
        "Hazardous Cargo Warning",
        "Berth Closure",
        "Weather Warning",
        "Congestion Alert",
        "Security Notice"
    ]

    severities = ["Critical", "High", "Medium", "Low"]
    severity_weights = [0.1, 0.2, 0.4, 0.3]  # Probability distribution

    # Get random location
    locations = system.get_locations()
    if not locations:
        return None

    location = random.choice(locations)

    # Generate notification ID
    notif_id = f"N{random.randint(1000, 9999)}"

    # Select alert type and severity
    alert_type = random.choice(alert_types)
    severity = random.choices(severities, weights=severity_weights, k=1)[0]

    # Generate realistic messages
    messages = {
        "Equipment Failure": f"Crane {location.location_id} experiencing mechanical issues",
        "Hazardous Cargo Warning": f"Hazardous materials detected at {location.name}",
        "Berth Closure": f"{location.name} temporarily closed for maintenance",
        "Weather Warning": f"Severe weather alert affecting {location.name} area",
        "Congestion Alert": f"High traffic congestion detected at {location.name}",
        "Security Notice": f"Security incident reported near {location.name}"
    }

    message = messages.get(alert_type, f"Alert at {location.name}")

    return {
        'notification_id': notif_id,
        'alert_type': alert_type,
        'location_id': location.location_id,
        'severity': severity,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }


def simulate_analytics_metrics() -> Dict:
    """
    Generate simulated analytics metrics for dashboard display.

    Returns:
        Dictionary with various metrics
    """
    # Simulate berth usage rate (60-95%)
    berth_usage_rate = random.uniform(60, 95)

    # Simulate peak hours (morning and afternoon peaks)
    peak_hours = {
        'morning': {'hour': random.randint(7, 10), 'activity': random.uniform(70, 95)},
        'afternoon': {'hour': random.randint(13, 16), 'activity': random.uniform(65, 90)}
    }

    # Simulate route efficiency (70-98%)
    route_efficiency = random.uniform(70, 98)

    # Simulate vessel waiting time (15-120 minutes)
    avg_waiting_time = random.uniform(15, 120)

    # Simulate daily throughput (500-2000 TEU)
    daily_throughput = random.randint(500, 2000)

    return {
        'berth_usage_rate': round(berth_usage_rate, 1),
        'peak_hours': peak_hours,
        'route_efficiency': round(route_efficiency, 1),
        'avg_waiting_time': round(avg_waiting_time, 1),
        'daily_throughput': daily_throughput
    }


def generate_peak_hours_data() -> pd.DataFrame:
    """
    Generate simulated port activity data by hour.

    Returns:
        DataFrame with hour and activity_level columns
    """
    hours = list(range(24))

    # Simulate realistic port activity pattern
    # Higher activity during working hours (6 AM - 10 PM)
    activity_levels = []
    for hour in hours:
        if 6 <= hour <= 10:  # Morning peak
            activity = random.uniform(70, 95)
        elif 11 <= hour <= 14:  # Midday
            activity = random.uniform(60, 80)
        elif 15 <= hour <= 18:  # Afternoon peak
            activity = random.uniform(75, 95)
        elif 19 <= hour <= 22:  # Evening
            activity = random.uniform(40, 65)
        else:  # Night (low activity)
            activity = random.uniform(10, 35)

        activity_levels.append(activity)

    return pd.DataFrame({
        'hour': hours,
        'activity_level': [round(a, 1) for a in activity_levels]
    })


def generate_alert_trend_data(days: int = 7) -> pd.DataFrame:
    """
    Generate simulated alert trend data over time.

    Args:
        days: Number of days to generate data for

    Returns:
        DataFrame with date, severity, and alert_count columns
    """
    severities = ['Critical', 'High', 'Medium', 'Low']
    data = []

    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

        for severity in severities:
            # Different alert frequencies by severity
            if severity == 'Critical':
                count = random.randint(0, 3)
            elif severity == 'High':
                count = random.randint(1, 6)
            elif severity == 'Medium':
                count = random.randint(3, 12)
            else:  # Low
                count = random.randint(5, 20)

            data.append({
                'date': date,
                'severity': severity,
                'alert_count': count
            })

    return pd.DataFrame(data)


def generate_capacity_forecast_data(days: int = 14) -> pd.DataFrame:
    """
    Generate simulated capacity utilization forecast.

    Args:
        days: Number of days to forecast

    Returns:
        DataFrame with date and capacity_usage columns
    """
    data = []
    base_capacity = random.uniform(65, 75)

    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')

        # Simulate gradual increase with some fluctuation
        trend = base_capacity + (i * 0.5)  # Slight upward trend
        fluctuation = random.uniform(-5, 5)
        usage = min(100, max(0, trend + fluctuation))

        data.append({
            'date': date,
            'capacity_usage': round(usage, 1)
        })

    return pd.DataFrame(data)
