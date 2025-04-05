from abc import ABC, abstractmethod
from copy import deepcopy
from io import StringIO


class Printable(ABC):
    """Base abstract class for printable objects."""

    @abstractmethod
    def print_me(self, os, prefix="", is_last=False):
        """Base printing method for the tree structure display.
        Implement properly to display hierarchical structure."""
        pass

    def clone(self):
        """Create a deep copy of this object."""
        return deepcopy(self)

    @staticmethod
    def tree_connector(is_last):
        return "\\-" if is_last else "+-"

    @staticmethod
    def is_last(index, items):
        return index == len(items) - 1

    @staticmethod
    def sub_prefix(prefix, is_last):
        return prefix + ("  " if is_last else "| ")

    def __str__(self):
        os = StringIO()
        self.print_me(os)
        return os.getvalue().rstrip()


class BasicCollection(Printable):
    """Base class for collections of items."""


class Component(Printable):
    """Base class for computer components."""


class Address(Printable):
    """Class representing a network address."""

    def __init__(self, addr):
        self.address = addr

    def print_me(self, os, prefix="", is_last=True):
        os.write(f"{prefix}{Printable.tree_connector(is_last)}{self.address}\n")


class Computer(BasicCollection):
    """Class representing a computer with addresses and components."""

    def __init__(self, name):
        self.name = name
        self.addresses = []
        self.components = []

    def add_address(self, addr):
        self.addresses.append(Address(addr))
        return self

    def add_component(self, comp):
        self.components.append(comp)
        return self

    def print_me(self, os, prefix="", is_last=True):
        os.write(f"{prefix}{Printable.tree_connector(is_last)}Host: {self.name}\n")

        sub_prefix = Printable.sub_prefix(prefix, is_last)

        for i, addr in enumerate(self.addresses):
            addr.print_me(
                os,
                sub_prefix,
                is_last=(
                    Printable.is_last(i, self.addresses) and len(self.components) == 0
                ),
            )

        for i, comp in enumerate(self.components):
            comp.print_me(
                os, sub_prefix, is_last=(Printable.is_last(i, self.components))
            )


class Network(Printable):
    """Class representing a network of computers."""

    def __init__(self, name):
        self.name = name
        self.computers = []

    def add_computer(self, comp):
        self.computers.append(comp)
        return self

    def find_computer(self, name):
        for comp in self.computers:
            if comp.name == name:
                return comp
        return None

    def print_me(self, os, prefix="", is_last=True):
        os.write(f"Network: {self.name}\n")
        for i, comp in enumerate(self.computers):
            comp.print_me(os, "", Printable.is_last(i, self.computers))


class Disk(Component):
    """Disk component class with partitions."""

    # Определение типов дисков
    SSD = 0
    MAGNETIC = 1

    def __init__(self, storage_type, size):
        self.storage_type = storage_type
        self.size = size
        self.partitions = []

    def add_partition(self, size, name):
        self.partitions.append((size, name))
        return self

    def print_me(self, os, prefix="", is_last=True):
        disk_type = "SSD" if self.storage_type == Disk.SSD else "HDD"

        os.write(
            f"{prefix}{Printable.tree_connector(is_last)}{disk_type}, {self.size} GiB\n"
        )

        part_prefix = Printable.sub_prefix(prefix, is_last)

        for i, (size, name) in enumerate(self.partitions):
            last = Printable.is_last(i, self.partitions)

            os.write(
                f"{part_prefix}{Printable.tree_connector(last)}[{i}]: {size} GiB, {name}\n"
            )


class CPU(Component):
    """CPU component class."""

    def __init__(self, cores, mhz):
        self.cores = cores
        self.mhz = mhz

    def print_me(self, os, prefix="", is_last=True):
        os.write(
            f"{prefix}{Printable.tree_connector(is_last)}CPU, {self.cores} cores @ {self.mhz}MHz\n"
        )


class Memory(Component):
    """Memory component class."""

    def __init__(self, size):
        self.size = size

    def print_me(self, os, prefix="", is_last=True):
        os.write(
            f"{prefix}{Printable.tree_connector(is_last)}Memory, {self.size} MiB\n"
        )


# Пример использования (может быть неполным или содержать ошибки)
def main():
    # Создание тестовой сети
    n = Network("MISIS network")

    # Добавляем первый сервер с одним CPU и памятью
    n.add_computer(
        Computer("server1.misis.ru")
        .add_address("192.168.1.1")
        .add_component(CPU(4, 2500))
        .add_component(Memory(16000))
    )

    # Добавляем второй сервер с CPU и HDD с разделами
    n.add_computer(
        Computer("server2.misis.ru")
        .add_address("10.0.0.1")
        .add_component(CPU(8, 3200))
        .add_component(
            Disk(Disk.MAGNETIC, 2000)
            .add_partition(500, "system")
            .add_partition(1500, "data")
        )
    )

    # Выводим сеть для проверки форматирования
    print("=== Созданная сеть ===")
    print(n)

    # Тест ожидаемого вывода
    expected_output = """Network: MISIS network
+-Host: server1.misis.ru
| +-192.168.1.1
| +-CPU, 4 cores @ 2500MHz
| \-Memory, 16000 MiB
\-Host: server2.misis.ru
  +-10.0.0.1
  +-CPU, 8 cores @ 3200MHz
  \-HDD, 2000 GiB
    +-[0]: 500 GiB, system
    \-[1]: 1500 GiB, data"""

    assert str(n) == expected_output, "Формат вывода не соответствует ожидаемому"
    print("✓ Тест формата вывода пройден")

    # Тестируем глубокое копирование
    print("\n=== Тестирование глубокого копирования ===")
    x = n.clone()

    # Тестируем поиск компьютера
    print("Поиск компьютера server2.misis.ru:")
    c = x.find_computer("server2.misis.ru")
    print(c)

    # Модифицируем найденный компьютер в копии
    print("\nДобавляем SSD к найденному компьютеру в копии:")
    c.add_component(Disk(Disk.SSD, 500).add_partition(500, "fast_storage"))

    # Проверяем, что оригинал не изменился
    print("\n=== Модифицированная копия ===")
    print(x)
    print("\n=== Исходная сеть (должна остаться неизменной) ===")
    print(n)

    # Проверяем ассерты для тестирования системы
    print("\n=== Выполнение тестов ===")

    # Тест поиска
    assert x.find_computer("server1.misis.ru") is not None, "Компьютер не найден"
    print("✓ Тест поиска пройден")

    # Тест независимости копий
    original_server2 = n.find_computer("server2.misis.ru")
    modified_server2 = x.find_computer("server2.misis.ru")

    original_components = sum(1 for _ in original_server2.components)
    modified_components = sum(1 for _ in modified_server2.components)

    assert original_components == 2, (
        f"Неверное количество компонентов в оригинале: {original_components}"
    )
    assert modified_components == 3, (
        f"Неверное количество компонентов в копии: {modified_components}"
    )
    print("✓ Тест независимости копий пройден")

    # Проверка типов дисков
    disk_tests = [(Disk(Disk.SSD, 256), "SSD"), (Disk(Disk.MAGNETIC, 1000), "HDD")]

    for disk, expected_type in disk_tests:
        assert expected_type in str(disk), f"Неверный тип диска в выводе: {str(disk)}"
    print("✓ Тест типов дисков пройден")

    print("\nВсе тесты пройдены!")


if __name__ == "__main__":
    main()
