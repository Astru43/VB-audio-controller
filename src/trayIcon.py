from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


class TrayIcon(Icon):
    def __init__(self, name, icon=None, title=None, menu=None, **kwargs):
        icon = self._create_image(64, 64, 'black', 'white', icon)
        super().__init__(name, icon, title, menu, **kwargs)

    def _create_image(self, width, height, color1, color2, icon):
        try:
            image = Image.open(icon)
        except:
            image = Image.new('RGB', (width, height), color1)
            dc = ImageDraw.Draw(image)
            dc.rectangle(
                (width // 2, 0, width, height // 2),
                fill=color2
            )
            dc.rectangle(
                (0, height // 2, width // 2, height),
                fill=color2
            )

        return image
