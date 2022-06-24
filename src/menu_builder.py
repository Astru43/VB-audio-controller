from typing import Callable, Union
from vmwrapper import VoicemeeterWrapper
from pystray import Menu, MenuItem


def menu_builder(vm: VoicemeeterWrapper, stop: Callable[[None], None]):
    def map_helper(channel: Union[vm.Bus, vm.Strip]):
        return MenuItem(
            channel.name.capitalize(),
            action=lambda: action_helper(channel),
            checked=lambda _: status(channel),
            radio=True
        )

    def status(item) -> bool:
        return item == vm.channel

    def action_helper(channel: Union[vm.Bus, vm.Strip]):
        print(channel)
        vm.set_channel(channel)

    menu = Menu(
        MenuItem(
            'Stop',
            stop,
            default=True,
        ),
        Menu.SEPARATOR,
        MenuItem(
            'Busses',
            Menu(lambda: (map_helper(bus) for bus in vm.Bus))
        ),
        MenuItem(
            'Strips',
            Menu(lambda: (map_helper(strip) for strip in vm.Strip))
        )
    )

    return menu
