from textual.widgets import Static


class Divider(Static):
    def __init__(
        self,
        *,
        orientation: str = "horizontal",
        color: str | None = None,
        thickness: int = 1,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        if orientation not in ("horizontal", "vertical"):
            raise ValueError("Orientation must be 'horizontal' or 'vertical'.")

        super().__init__(
            id=id,
            classes=f"{classes or ''} {orientation}".strip(),
        )

        if thickness < 1:
            raise ValueError("Thickness must be at least 1.")

        if orientation == "horizontal":
            self.styles.height = thickness
        else:
            self.styles.width = thickness

        if color is not None:
            self.styles.background = color
