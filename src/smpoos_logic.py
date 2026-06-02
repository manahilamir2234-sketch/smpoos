"""
SMPOOS Core Logic
Author: Manahil
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import csv
import os

import pandas as pd


class UserRole(Enum):
    HARBOURMASTER = "Harbourmaster"
    OPERATIONS_SUPERVISOR = "Operations Supervisor"
    SAFETY_OFFICER = "Safety Officer"
    CRANE_OPERATOR = "Crane Operator"
    MAINTENANCE_ENGINEER = "Maintenance Engineer"
    SECURITY_OFFICER = "Security Officer"
    STEVEDORE = "Stevedore"
    LOGISTICS_COORDINATOR = "Logistics Coordinator"
    ADMINISTRATOR = "Administrator"


class AlertType(Enum):
    EQUIPMENT_FAILURE = "Equipment Failure"
    HAZARDOUS_CARGO = "Hazardous Cargo Warning"
    BERTH_CLOSURE = "Berth Closure"
    WEATHER_WARNING = "Weather Warning"
    CONGESTION_ALERT = "Congestion Alert"
    SECURITY_NOTICE = "Security Notice"


class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LocationType(Enum):
    BERTH = "Berth"
    STORAGE_YARD = "Storage Yard"
    FUEL_DOCK = "Fuel Dock"
    CUSTOMS_ZONE = "Customs Zone"
    MAINTENANCE_AREA = "Maintenance Area"


class RouteType(Enum):
    SHIPPING_LANE = "Shipping Lane"
    TUGBOAT_TRANSIT = "Tugboat Transit Path"
    AGV_ROUTE = "Automated Guided Vehicle Route"
    TRUCK_PATH = "Truck Path"


class EntityStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    UNDER_MAINTENANCE = "Under Maintenance"
    OPEN = "Open"
    RESTRICTED = "Restricted"
    CLOSED = "Closed"


class PortEntity(ABC):
    @abstractmethod
    def to_dict(self):
        """Convert to dict"""
        pass

    @abstractmethod
    def validate(self):
        """Validate entity data integrity.
        """
        pass

    def __repr__(self):
        """String representation of the entity."""
        return f"{self.__class__.__name__}({self.to_dict()})"




class Location(PortEntity):
    def __init__(self, location_id, name, loc_type, status, capacity_tonnes):
        self.location_id = location_id
        self.name = name
        self.type = loc_type
        self.status = status
        self.capacity_tonnes = float(capacity_tonnes)

    def to_dict(self):
        return {
            'location_id': self.location_id,
            'name': self.name,
            'type': self.type.value if isinstance(self.type, LocationType) else self.type,
            'status': self.status.value if isinstance(self.status, EntityStatus) else self.status,
            'capacity_tonnes': self.capacity_tonnes
        }

    def validate(self):
        return bool(self.location_id) and bool(self.name)


class Route(PortEntity):
    def __init__(self, route_id, start_location, end_location, route_type, distance_km, status):
        self.route_id = route_id
        self.start_location = start_location
        self.end_location = end_location
        self.route_type = route_type
        self.distance_km = float(distance_km)
        self.status = status

    def to_dict(self):
        return {
            'route_id': self.route_id,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'route_type': self.route_type.value if isinstance(self.route_type, RouteType) else self.route_type,
            'distance_km': self.distance_km,
            'status': self.status.value if isinstance(self.status, EntityStatus) else self.status
        }

    def validate(self):
        return bool(self.route_id) and bool(self.start_location)


class Notification(PortEntity):
    def __init__(self, notification_id, alert_type, location_id, severity, message, timestamp):
        self.notification_id = notification_id
        self.alert_type = alert_type
        self.location_id = location_id
        self.severity = severity
        self.message = message
        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'alert_type': self.alert_type.value if isinstance(self.alert_type, AlertType) else self.alert_type,
            'location_id': self.location_id,
            'severity': self.severity.value if isinstance(self.severity, Severity) else self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        }

    def validate(self):
        return bool(self.notification_id) and bool(self.message)


class User(PortEntity):
    def __init__(self, user_id, name, role, email, active):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.email = email
        if isinstance(active, bool):
            self.active = "Yes" if active else "No"
        else:
            self.active = active

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role,
            'email': self.email,
            'active': self.active
        }

    def validate(self):
        return bool(self.user_id) and bool(self.email)

    def is_active(self):
        return self.active == "Yes"




class SMPOOS:
    """Central Controller for the Smart Maritime Port Operations Optimisation System.

    Manages all port entities including locations, routes, notifications, and users.
    Provides CRUD operations, persistence to CSV files, and system statistics.
    """

    def __init__(self, data_dir):
        """Initialize the SMPOOS controller.
        """
        if data_dir is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        self.locations = {}
        self.routes = {}
        self.notifications = {}
        self.users = {}
        self._audit_log = []

        self._initialize_data()

    def _log_audit(
        self,
        action,
        entity_type,
        entity_id,
        details: str = ""
    ) -> None:
        """Log an audit entry for create/update/delete operations.
        """
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details
        })

    def get_audit_log(self):
        """Retrieve the audit log.
        """
        return self._audit_log.copy()

    def _initialize_data(self):
        """Load data from CSVs"""
        try:
            self._load_locations()
            self._load_routes()
            self._load_notifications()
            self._load_users()
        except FileNotFoundError as e:
            print(f"CRITICAL ERROR during initialization: {e}")

    def _load_locations(self):
        """Load locations from CSV file."""
        path = os.path.join(self.data_dir, "smpoos_locations.csv")
        with open(path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse type enum if possible
                loc_type = row['type']
                try:
                    loc_type = LocationType(loc_type)
                except ValueError:
                    pass  # Keep as string if not matching enum

                # Parse status enum if possible
                status = row['status']
                try:
                    status = EntityStatus(status)
                except ValueError:
                    pass  # Keep as string if not matching enum

                obj = Location(
                    row['location_id'],
                    row['name'],
                    loc_type,
                    status,
                    row['capacity_tonnes']
                )
                self.locations[obj.location_id] = obj

    def _load_routes(self) -> None:
        """Load routes from CSV file."""
        path = os.path.join(self.data_dir, "smpoos_routes.csv")
        with open(path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse route_type enum if possible
                route_type = row['route_type']
                try:
                    route_type = RouteType(route_type)
                except ValueError:
                    pass  # Keep as string if not matching enum

                # Parse status enum if possible
                status = row['status']
                try:
                    status = EntityStatus(status)
                except ValueError:
                    pass  # Keep as string if not matching enum

                obj = Route(
                    row['route_id'],
                    row['start_location'],
                    row['end_location'],
                    route_type,
                    row['distance_km'],
                    status
                )
                self.routes[obj.route_id] = obj

    def _load_notifications(self) -> None:
        """Load notifications from CSV file."""
        path = os.path.join(self.data_dir, "smpoos_notifications.csv")
        with open(path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse alert_type enum if possible
                alert_type = row['alert_type']
                try:
                    alert_type = AlertType(alert_type)
                except ValueError:
                    pass  # Keep as string if not matching enum

                # Parse severity enum if possible
                severity = row['severity']
                try:
                    severity = Severity(severity)
                except ValueError:
                    pass  # Keep as string if not matching enum

                obj = Notification(
                    row['notification_id'],
                    alert_type,
                    row['location_id'],
                    severity,
                    row['message'],
                    row['timestamp']
                )
                self.notifications[obj.notification_id] = obj

    def _load_users(self) -> None:
        """Load users from CSV file."""
        path = os.path.join(self.data_dir, "smpoos_users.csv")
        with open(path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse role enum if possible
                role = row['role']
                try:
                    role = UserRole(role)
                except ValueError:
                    pass  # Keep as string if not matching enum

                obj = User(
                    row['user_id'],
                    row['name'],
                    role,
                    row['email'],
                    row['active']
                )
                self.users[obj.user_id] = obj

    def _save_to_csv(self, entity_type) -> None:
        """Persist entities of the given type to their CSV file.
        """
        if entity_type == 'locations':
            path = os.path.join(self.data_dir, "smpoos_locations.csv")
            entities = list(self.locations.values())
            fieldnames = ['location_id', 'name',
                          'type', 'status', 'capacity_tonnes']
        elif entity_type == 'routes':
            path = os.path.join(self.data_dir, "smpoos_routes.csv")
            entities = list(self.routes.values())
            fieldnames = ['route_id', 'start_location',
                          'end_location', 'route_type', 'distance_km', 'status']
        elif entity_type == 'notifications':
            path = os.path.join(self.data_dir, "smpoos_notifications.csv")
            entities = list(self.notifications.values())
            fieldnames = ['notification_id', 'alert_type',
                          'location_id', 'severity', 'message', 'timestamp']
        elif entity_type == 'users':
            path = os.path.join(self.data_dir, "smpoos_users.csv")
            entities = list(self.users.values())
            fieldnames = ['user_id', 'name', 'role', 'email', 'active']
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")

        with open(path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entity in entities:
                writer.writerow(entity.to_dict())

    

    def add_location(
        self,
        location_id,
        name,
        loc_type,
        status,
        capacity
    ):
        """Create and add a new location.
        """
        location = Location(location_id, name, loc_type, status, capacity)
        self.locations[location_id] = location
        self._save_to_csv('locations')
        self._log_audit('CREATE', 'location', location_id,
                        f"Created location: {name}")
        return location

    def update_location(self, location_id, **kwargs):
        """Update an existing location.
        """
        if location_id not in self.locations:
            return None

        location = self.locations[location_id]

        if 'name' in kwargs:
            location.name = kwargs['name']
        if 'loc_type' in kwargs or 'type' in kwargs:
            location.type = kwargs.get('loc_type') or kwargs.get('type')
        if 'status' in kwargs:
            location.status = kwargs['status']
        if 'capacity' in kwargs or 'capacity_tonnes' in kwargs:
            location.capacity_tonnes = float(kwargs.get(
                'capacity') or kwargs.get('capacity_tonnes'))

        self._save_to_csv('locations')
        self._log_audit('UPDATE', 'location', location_id,
                        f"Updated fields: {list(kwargs.keys())}")
        return location

    def delete_location(self, location_id):
        """Delete a location.
        """
        if location_id not in self.locations:
            return False

        del self.locations[location_id]
        self._save_to_csv('locations')
        self._log_audit('DELETE', 'location', location_id, "Deleted location")
        return True

    def get_locations(self):
        """Get all locations.
        """
        return list(self.locations.values())

    def get_location_by_id(self, location_id):
        """Get a location by its ID.
        """
        return self.locations.get(location_id)

    

    def add_route(
        self,
        route_id,
        start_location,
        end_location,
        route_type,
        distance_km,
        status
    ):
        """Create and add a new route.
        """
        route = Route(route_id, start_location, end_location,
                      route_type, distance_km, status)
        self.routes[route_id] = route
        self._save_to_csv('routes')
        self._log_audit('CREATE', 'route', route_id,
                        f"Created route: {start_location} -> {end_location}")
        return route

    def update_route(self, route_id, **kwargs):
        """Update an existing route.
        """
        if route_id not in self.routes:
            return None

        route = self.routes[route_id]

        if 'start_location' in kwargs:
            route.start_location = kwargs['start_location']
        if 'end_location' in kwargs:
            route.end_location = kwargs['end_location']
        if 'route_type' in kwargs:
            route.route_type = kwargs['route_type']
        if 'distance_km' in kwargs:
            route.distance_km = float(kwargs['distance_km'])
        if 'status' in kwargs:
            route.status = kwargs['status']

        self._save_to_csv('routes')
        self._log_audit('UPDATE', 'route', route_id,
                        f"Updated fields: {list(kwargs.keys())}")
        return route

    def delete_route(self, route_id):
        """Delete a route.
        """
        if route_id not in self.routes:
            return False

        del self.routes[route_id]
        self._save_to_csv('routes')
        self._log_audit('DELETE', 'route', route_id, "Deleted route")
        return True

    def get_routes(self):
        """Get all routes.
        """
        return list(self.routes.values())

    def get_route_by_id(self, route_id):
        """Get a route by its ID.
        """
        return self.routes.get(route_id)

    

    def add_notification(
        self,
        notification_id,
        alert_type,
        location_id,
        severity,
        message,
        timestamp=None
    ):
        """Create and add a new notification.
        """
        if timestamp is None:
            timestamp = datetime.now()

        notification = Notification(
            notification_id, alert_type, location_id, severity, message, timestamp)
        self.notifications[notification_id] = notification
        self._save_to_csv('notifications')
        self._log_audit('CREATE', 'notification', notification_id,
                        f"Created {alert_type} notification")
        return notification

    def update_notification(self, notification_id, **kwargs):
        """Update an existing notification.
        """
        if notification_id not in self.notifications:
            return None

        notification = self.notifications[notification_id]

        if 'alert_type' in kwargs:
            notification.alert_type = kwargs['alert_type']
        if 'location_id' in kwargs:
            notification.location_id = kwargs['location_id']
        if 'severity' in kwargs:
            notification.severity = kwargs['severity']
        if 'message' in kwargs:
            notification.message = kwargs['message']
        if 'timestamp' in kwargs:
            notification.timestamp = kwargs['timestamp']

        self._save_to_csv('notifications')
        self._log_audit('UPDATE', 'notification', notification_id,
                        f"Updated fields: {list(kwargs.keys())}")
        return notification

    def delete_notification(self, notification_id):
        """Delete a notification.
        """
        if notification_id not in self.notifications:
            return False

        del self.notifications[notification_id]
        self._save_to_csv('notifications')
        self._log_audit('DELETE', 'notification',
                        notification_id, "Deleted notification")
        return True

    def get_notifications(self):
        """Get all notifications.
        """
        return list(self.notifications.values())

    def get_notification_by_id(self, notification_id):
        """Get a notification by its ID.
        """
        return self.notifications.get(notification_id)

    

    def add_user(
        self,
        user_id,
        name,
        role,
        email,
        active
    ):
        """Create and add a new user.
        """
        user = User(user_id, name, role, email, active)
        self.users[user_id] = user
        self._save_to_csv('users')
        self._log_audit('CREATE', 'user', user_id, f"Created user: {name}")
        return user

    def update_user(self, user_id, **kwargs):
        """Update an existing user.
        """
        if user_id not in self.users:
            return None

        user = self.users[user_id]

        if 'name' in kwargs:
            user.name = kwargs['name']
        if 'role' in kwargs:
            user.role = kwargs['role']
        if 'email' in kwargs:
            user.email = kwargs['email']
        if 'active' in kwargs:
            user.active = "Yes" if kwargs['active'] else "No" if isinstance(
                kwargs['active'], bool) else kwargs['active']

        self._save_to_csv('users')
        self._log_audit('UPDATE', 'user', user_id,
                        f"Updated fields: {list(kwargs.keys())}")
        return user

    def delete_user(self, user_id):
        """Delete a user.
        """
        if user_id not in self.users:
            return False

        del self.users[user_id]
        self._save_to_csv('users')
        self._log_audit('DELETE', 'user', user_id, "Deleted user")
        return True

    def get_users(self):
        """Get all users.
        """
        return list(self.users.values())

    def get_user_by_id(self, user_id):
        """Get a user by their ID.
        """
        return self.users.get(user_id)

    

    def get_locations_df(self):
        """Get all locations as a pandas DataFrame.
        """
        return pd.DataFrame([loc.to_dict() for loc in self.locations.values()])

    def get_routes_df(self):
        """Get all routes as a pandas DataFrame.
        """
        return pd.DataFrame([route.to_dict() for route in self.routes.values()])

    def get_notifications_df(self):
        """Get all notifications as a pandas DataFrame.
        """
        return pd.DataFrame([notif.to_dict() for notif in self.notifications.values()])

    def get_users_df(self):
        """Get all users as a pandas DataFrame.
        """
        return pd.DataFrame([user.to_dict() for user in self.users.values()])

    

    def get_stats_summary(self):
        """Get a summary of system statistics.
        """
        # Count active locations
        active_locations = len([
            loc for loc in self.locations.values()
            if (isinstance(loc.status, EntityStatus) and loc.status == EntityStatus.ACTIVE)
            or (isinstance(loc.status, str) and loc.status == "Active")
        ])

        # Count active routes (status == "Open")
        active_routes = len([
            r for r in self.routes.values()
            if (isinstance(r.status, EntityStatus) and r.status == EntityStatus.OPEN)
            or (isinstance(r.status, str) and r.status == "Open")
        ])

        # Count critical alerts
        critical_alerts = len([
            n for n in self.notifications.values()
            if (isinstance(n.severity, Severity) and n.severity == Severity.CRITICAL)
            or (isinstance(n.severity, str) and n.severity == "Critical")
        ])

        # Count active users
        active_users = len([
            u for u in self.users.values()
            if u.is_active()
        ])

        return {
            "total_locations": len(self.locations),
            "active_locations": active_locations,
            "total_routes": len(self.routes),
            "active_routes": active_routes,
            "total_notifications": len(self.notifications),
            "critical_alerts": critical_alerts,
            "total_users": len(self.users),
            "active_users": active_users
        }

    

    def get_berth_usage_stats(self):
        """
        Calculate berth usage statistics based on routes and notifications.
        """
        import random

        berth_locations = [
            loc for loc in self.locations.values()
            if (isinstance(loc.type, LocationType) and loc.type == LocationType.BERTH)
            or (isinstance(loc.type, str) and loc.type == "Berth")
        ]

        data = []
        for loc in berth_locations:
            # Simulate usage score based on capacity and random factor
            base_score = loc.capacity_tonnes / 1000
            random_factor = random.uniform(0.5, 1.5)
            usage_score = base_score * random_factor

            data.append({
                'berth_id': loc.location_id,
                'berth_name': loc.name,
                'usage_score': round(usage_score, 2)
            })

        return pd.DataFrame(data)

    def get_peak_hours_analysis(self):
        """
        Analyze notification timestamps to find peak activity hours.
        """
        from datetime import datetime

        notifications = list(self.notifications.values())
        if not notifications:
            return pd.DataFrame(columns=['hour', 'activity_count'])

        hour_counts = {}
        for notif in notifications:
            try:
                if isinstance(notif.timestamp, datetime):
                    hour = notif.timestamp.hour
                else:
                    hour = datetime.fromisoformat(str(notif.timestamp)).hour

                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                pass

        # Fill in missing hours with 0
        for h in range(24):
            if h not in hour_counts:
                hour_counts[h] = 0

        df = pd.DataFrame([
            {'hour': h, 'activity_count': hour_counts[h]}
            for h in sorted(hour_counts.keys())
        ])

        return df

    def get_route_efficiency_metrics(self):
        """
        Calculate route efficiency based on distance and status.
        """
        import random

        data = []
        for route in self.routes.values():
            # Efficiency = 100 - (distance penalty + status penalty)
            distance_penalty = min(30, route.distance_km / 10)

            status = route.status.value if isinstance(
                route.status, EntityStatus) else route.status
            status_penalty = 0 if status == "Open" else (
                20 if status == "Restricted" else 50)

            efficiency = max(0, 100 - distance_penalty -
                             status_penalty + random.uniform(-5, 5))

            data.append({
                'route_id': route.route_id,
                'route_type': route.route_type.value if isinstance(route.route_type, RouteType) else route.route_type,
                'distance_km': route.distance_km,
                'status': status,
                'efficiency': round(efficiency, 1)
            })

        return pd.DataFrame(data)

    def get_alert_trends(self):
        """
        Group notifications by date and severity for trend analysis.
        """
        from datetime import datetime
        import pandas as pd

        notifications = list(self.notifications.values())
        if not notifications:
            return pd.DataFrame(columns=['date', 'severity', 'count'])

        trends = []
        for notif in notifications:
            try:
                if isinstance(notif.timestamp, datetime):
                    date = notif.timestamp.strftime('%Y-%m-%d')
                else:
                    date = datetime.fromisoformat(
                        str(notif.timestamp)).strftime('%Y-%m-%d')

                severity = notif.severity.value if isinstance(
                    notif.severity, Severity) else notif.severity

                trends.append({
                    'date': date,
                    'severity': severity
                })
            except:
                pass

        if not trends:
            return pd.DataFrame(columns=['date', 'severity', 'count'])

        df = pd.DataFrame(trends)
        trend_counts = df.groupby(
            ['date', 'severity']).size().reset_index(name='count')

        return trend_counts
