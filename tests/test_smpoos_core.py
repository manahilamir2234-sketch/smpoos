"""
Unit tests for SMPOOS core logic, validation, RBAC and persistence.
Run from the project root with:  python -m pytest tests/ -v
"""

import os
import shutil
import tempfile

import pytest

from src.smpoos_logic import (
    Location, Route, Notification, User, SMPOOS,
    LocationType, EntityStatus, AlertType, Severity, UserRole,
)
from src.utils.rbac_utils import can_modify_data, severities_for_role
from src.utils.auth_utils import verify_admin_credentials
from src.utils.email_utils import send_notification_email, get_email_log


@pytest.fixture
def temp_system():
    """Copy Moodle CSVs into a temp folder so tests never alter live data."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_data = os.path.join(root, "data")
    tmp = tempfile.mkdtemp()
    for name in os.listdir(src_data):
        if name.endswith(".csv"):
            shutil.copy(os.path.join(src_data, name), os.path.join(tmp, name))
    system = SMPOOS(data_dir=tmp)
    yield system
    shutil.rmtree(tmp, ignore_errors=True)


class TestEntityValidation:
    def test_location_rejects_negative_capacity(self):
        loc = Location("LX", "Test", LocationType.BERTH, EntityStatus.ACTIVE, -10)
        assert loc.validate() is False

    def test_location_accepts_valid(self):
        loc = Location("LX", "Test", LocationType.BERTH, EntityStatus.ACTIVE, 100)
        assert loc.validate() is True

    def test_user_rejects_bad_email(self):
        user = User("UX", "Ada", UserRole.HARBOURMASTER, "not-an-email", "Yes")
        assert user.validate() is False

    def test_user_accepts_good_email(self):
        user = User("UX", "Ada", UserRole.HARBOURMASTER, "ada@port.com", "Yes")
        assert user.validate() is True

    def test_notification_requires_message(self):
        n = Notification("NX", AlertType.WEATHER_WARNING, "L001",
                         Severity.HIGH, "", "2024-01-01T00:00:00")
        assert n.validate() is False


class TestCRUD:
    def test_add_and_get_location(self, temp_system):
        before = len(temp_system.get_locations())
        temp_system.add_location("LTEST1", "Berth Test", "Berth", "Active", 500)
        assert len(temp_system.get_locations()) == before + 1
        assert temp_system.get_location_by_id("LTEST1") is not None

    def test_update_location(self, temp_system):
        temp_system.add_location("LTEST2", "Old Name", "Berth", "Active", 100)
        temp_system.update_location("LTEST2", name="New Name", status="Inactive")
        loc = temp_system.get_location_by_id("LTEST2")
        assert loc.name == "New Name"
        assert loc.status == "Inactive"

    def test_delete_location(self, temp_system):
        temp_system.add_location("LTEST3", "To Delete", "Berth", "Active", 50)
        assert temp_system.delete_location("LTEST3") is True
        assert temp_system.get_location_by_id("LTEST3") is None

    def test_add_route(self, temp_system):
        temp_system.add_route("RTEST1", "L0001", "L0002", "Shipping Lane", 12.5, "Open")
        assert temp_system.get_route_by_id("RTEST1") is not None

    def test_add_notification_writes_audit(self, temp_system):
        temp_system.add_notification(
            "NTEST1", "Weather Warning", "L0001", "High", "Storm approaching"
        )
        log = temp_system.get_audit_log()
        assert any(e["entity_id"] == "NTEST1" for e in log)

    def test_csv_persistence_roundtrip(self, temp_system):
        temp_system.add_location("LPERS", "Persist", "Berth", "Active", 77)
        reloaded = SMPOOS(data_dir=temp_system.data_dir)
        assert reloaded.get_location_by_id("LPERS") is not None


class TestRBAC:
    def test_harbourmaster_can_write(self):
        assert can_modify_data("Harbourmaster") is True

    def test_stevedore_is_readonly(self):
        assert can_modify_data("Stevedore") is False

    def test_safety_officer_focuses_critical_high(self):
        assert severities_for_role("Safety Officer") == ["Critical", "High"]

    def test_harbourmaster_sees_all(self):
        assert severities_for_role("Harbourmaster") is None


class TestAuthAndEmail:
    def test_default_admin_credentials(self):
        assert verify_admin_credentials("admin", "admin123") is True
        assert verify_admin_credentials("admin", "wrong") is False

    def test_email_simulation_logs_delivery(self):
        before = len(get_email_log())
        send_notification_email("ops@port.com", "Test", "Body")
        assert len(get_email_log()) == before + 1


class TestAnalyticsHelpers:
    def test_stats_summary_keys(self, temp_system):
        stats = temp_system.get_stats_summary()
        for key in ("total_locations", "active_routes", "critical_alerts", "active_users"):
            assert key in stats

    def test_gdpr_export_and_erase(self, temp_system):
        temp_system.add_user("UGDPR", "Test User", "Stevedore", "t@port.com", "Yes")
        exported = temp_system.export_user_data("UGDPR")
        assert exported["email"] == "t@port.com"
        assert temp_system.erase_user_data("UGDPR") is True
        assert temp_system.export_user_data("UGDPR") is None
