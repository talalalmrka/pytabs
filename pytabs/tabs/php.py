import webbrowser

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, TabPane, TextArea

from pytabs.config import APP_CONFIG
from pytabs.services.platform import find_php


class IniEditorScreen(ModalScreen):
    def __init__(self, ini_path: Path):
        super().__init__()

        self.ini_path = Path(ini_path).expanduser()

        try:
            self.initial_content = (
                self.ini_path.read_text(encoding="utf-8")
                if self.ini_path.is_file()
                else ""
            )
        except OSError:
            self.initial_content = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="ini-editor-dialog"):
            yield Label(f"Editing: {self.ini_path}", id="ini-editor-title")

            yield TextArea(
                self.initial_content,
                id="ini-editor",
                language="ini",
                soft_wrap=False,
            )

            with Horizontal(id="ini-editor-actions"):
                yield Button("Save", id="ini-save", variant="success")
                yield Button("Cancel", id="ini-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ini-cancel":
            self.dismiss(False)
            return

        if event.button.id != "ini-save":
            return

        content = self.query_one("#ini-editor", TextArea).text

        try:
            self.ini_path.parent.mkdir(parents=True, exist_ok=True)
            self.ini_path.write_text(content, encoding="utf-8")

        except OSError as error:
            self.notify(
                f"Unable to save php.ini: {error}",
                title="Save failed",
                severity="error",
            )
            return

        self.notify("php.ini saved successfully", severity="information")
        self.dismiss(True)


class PhpTab(TabPane):
    def __init__(self, **kwargs):
        super().__init__("PHP", **kwargs)

        self.config = APP_CONFIG.php

        self.document_root = Path(self.config.root).expanduser()
        self.ini_path = Path(self.config.ini_path).expanduser()
        self.router_path = Path(self.config.router_path).expanduser()
        self.dashboard_path = Path(self.config.dashboard_path).expanduser()
        self.php_info_path = Path(self.config.php_info_path).expanduser()
        self.temp_path = Path(self.config.temp_path).expanduser()
        self.log_path = Path(self.config.log_file).expanduser()
        self.pid_path = Path(self.config.pid_file).expanduser()

        self.executable = (
            self.config.executable or find_php() or "PHP executable not found"
        )

        self.base_url = f"http://localhost:{self.config.port}"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.php_info_url = f"{self.base_url}/dashboard/phpinfo.php"
        self.phpmyadmin_url = f"{self.base_url}/dashboard/phpmyadmin"

    def compose(self) -> ComposeResult:
        with Vertical(id="php-settings"):
            yield Label("PHP Server", classes="section-title")

            yield Static(
                f"Host: {self.config.host}",
                classes="config-value",
            )

            yield Button(
                f"Open server: {self.base_url}",
                id="php-open-server",
                variant="primary",
                classes="config-button",
            )

            yield Static(
                f"Port: {self.config.port}",
                classes="config-value",
            )

            yield Label("PHP Executable", classes="section-title")
            yield Button(
                f"Open: {self.executable}",
                id="php-executable",
                classes="config-button",
            )

            yield Label("Directories", classes="section-title")

            yield Button(
                f"Document Root: {self.document_root}",
                id="php-root",
                classes="config-button",
            )

            yield Button(
                f"Dashboard: {self.dashboard_path}",
                id="php-dashboard-path",
                classes="config-button",
            )

            yield Button(
                f"Temporary Directory: {self.temp_path}",
                id="php-temp",
                classes="config-button",
            )

            yield Label("Configuration Files", classes="section-title")

            yield Button(
                f"Edit php.ini: {self.ini_path}",
                id="php-ini",
                variant="success",
                classes="config-button",
            )

            yield Button(
                f"Router: {self.router_path}",
                id="php-router",
                classes="config-button",
            )

            yield Label("Logs and Process", classes="section-title")

            yield Button(
                f"Log File: {self.log_path}",
                id="php-log",
                classes="config-button",
            )

            yield Button(
                f"PID File: {self.pid_path}",
                id="php-pid",
                classes="config-button",
            )

            yield Label("Quick Links", classes="section-title")

            with Horizontal(classes="php-links"):
                yield Button(
                    "phpinfo",
                    id="php-info-url",
                    variant="primary",
                )

                yield Button(
                    "Dashboard",
                    id="php-dashboard-url",
                    variant="primary",
                )

                yield Button(
                    "phpMyAdmin",
                    id="phpmyadmin-url",
                    variant="primary",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "php-ini":
            self.app.push_screen(
                IniEditorScreen(self.ini_path),
                callback=self.on_ini_editor_closed,
            )
            return

        urls = {
            "php-open-server": self.base_url,
            "php-info-url": self.php_info_url,
            "php-dashboard-url": self.dashboard_url,
            "phpmyadmin-url": self.phpmyadmin_url,
        }

        if button_id in urls:
            self.app.open_url(urls[button_id])
            return

        paths = {
            "php-executable": Path(self.executable),
            "php-root": self.document_root,
            "php-dashboard-path": self.dashboard_path,
            "php-temp": self.temp_path,
            "php-router": self.router_path,
            "php-log": self.log_path,
            "php-pid": self.pid_path,
        }

        path = paths.get(button_id)

        if path is not None:
            self.open_path(path)

    def open_path(self, path: Path) -> None:
        path = path.expanduser()

        if not path.exists():
            path = path.parent

        if not path.exists():
            self.notify(
                f"Path does not exist: {path}",
                title="Cannot open path",
                severity="warning",
            )
            return

        webbrowser.open(path.resolve().as_uri())

    def on_ini_editor_closed(self, saved: bool | None) -> None:
        if saved:
            self.notify(
                "PHP configuration updated. Restart PHP to apply changes.",
                title="Configuration saved",
                severity="information",
            )

            log_event = getattr(self.app, "log_event", None)

            if callable(log_event):
                log_event("php", "php.ini configuration updated")
