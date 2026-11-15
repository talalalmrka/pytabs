from textual.widgets import TabPane, Static


class SettingsTab(TabPane):
    def __init__(self):
        super().__init__("Settings", id="settings")

    def compose(self):
        yield Static("Application Settings")
        yield Static("Configure your application here.")
