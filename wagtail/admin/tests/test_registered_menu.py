import unittest
from unittest.mock import patch, MagicMock
from wagtail import hooks
from wagtail.admin.menu import MenuItem


class MyClass:
    def __init__(self, initial_menu_items=None, register_hook_name=None):
        self.initial_menu_items = initial_menu_items
        self.register_hook_name = register_hook_name

    def registered_menu_items(self):
        if self.initial_menu_items:
            items = self.initial_menu_items.copy()
        else:
            items = []

        if self.register_hook_name:
            for fn in hooks.get_hooks(self.register_hook_name):
                items.append(fn())

        return items


class TestRegisteredMenuItems(unittest.TestCase):
    def setUp(self):
        self.obj = MyClass()

    def compare_menu_items(self, item1, item2):
        self.assertEqual(item1.label, item2.label)
        self.assertEqual(item1.url, item2.url)

    def test_no_initial_items_no_hooks(self):
        self.obj.initial_menu_items = []
        self.obj.register_hook_name = None
        with patch('wagtail.hooks.get_hooks', return_value=[]):
            items = self.obj.registered_menu_items()
            self.assertEqual(items, [])

    def test_with_initial_items_no_hooks(self):
        self.obj.initial_menu_items = [MenuItem('item1', '/item1'), MenuItem('item2', '/item2')]
        self.obj.register_hook_name = None
        with patch('wagtail.hooks.get_hooks', return_value=[]):
            items = self.obj.registered_menu_items()
            self.assertEqual(len(items), 2)
            self.compare_menu_items(items[0], MenuItem('item1', '/item1'))
            self.compare_menu_items(items[1], MenuItem('item2', '/item2'))

    def test_no_initial_items_with_hooks(self):
        self.obj.initial_menu_items = []
        self.obj.register_hook_name = 'some_hook'
        with patch('wagtail.hooks.get_hooks', return_value=[lambda: MenuItem('hook_item1', '/hook1'), lambda: MenuItem('hook_item2', '/hook2')]):
            items = self.obj.registered_menu_items()
            self.assertEqual(len(items), 2)
            self.compare_menu_items(items[0], MenuItem('hook_item1', '/hook1'))
            self.compare_menu_items(items[1], MenuItem('hook_item2', '/hook2'))

    def test_with_initial_items_with_hooks(self):
        self.obj.initial_menu_items = [MenuItem('item1', '/item1'), MenuItem('item2', '/item2')]
        self.obj.register_hook_name = 'some_hook'
        with patch('wagtail.hooks.get_hooks', return_value=[lambda: MenuItem('hook_item1', '/hook1'), lambda: MenuItem('hook_item2', '/hook2')]):
            items = self.obj.registered_menu_items()
            self.assertEqual(len(items), 4)
            self.compare_menu_items(items[0], MenuItem('item1', '/item1'))
            self.compare_menu_items(items[1], MenuItem('item2', '/item2'))
            self.compare_menu_items(items[2], MenuItem('hook_item1', '/hook1'))
            self.compare_menu_items(items[3], MenuItem('hook_item2', '/hook2'))

if __name__ == "__main__":
    unittest.main()
