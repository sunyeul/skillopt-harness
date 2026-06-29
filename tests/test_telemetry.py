from __future__ import annotations

import builtins
import unittest
from pathlib import Path
from unittest import mock

from skillopt_harness import telemetry


class TelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        telemetry._CONFIGURED = False
        telemetry._CONFIGURE_FAILED = False

    def tearDown(self) -> None:
        telemetry._CONFIGURED = False
        telemetry._CONFIGURE_FAILED = False

    def test_import_and_configure_are_noop_when_disabled(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertFalse(telemetry.is_enabled())
            telemetry.configure_telemetry()

            with telemetry.start_span("skillopt.test") as span:
                telemetry.set_attributes(span, {"skillopt.workspace": Path("workspace")})
                telemetry.add_event(span, "skillopt.event", {"skillopt.count": 1})

    def test_configure_does_not_raise_when_enabled_without_opentelemetry(self) -> None:
        real_import = builtins.__import__

        def fake_import(name: str, *args: object, **kwargs: object) -> object:
            if name.startswith("opentelemetry"):
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        with (
            mock.patch.dict("os.environ", {"SKILLOPT_OTEL_ENABLED": "1"}, clear=True),
            mock.patch("builtins.__import__", side_effect=fake_import),
        ):
            self.assertTrue(telemetry.is_enabled())
            telemetry.configure_telemetry()

            with telemetry.start_span("skillopt.test") as span:
                telemetry.set_attributes(span, {"skillopt.score": 1.0})


if __name__ == "__main__":
    unittest.main()
