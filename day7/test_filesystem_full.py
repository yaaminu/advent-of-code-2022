import unittest
from unittest import TestCase
from filesystem_full import Directory, File, FileSystem, FileSystemState, CliOutputProcessor


class DirectoryTestCase(TestCase):
    def test_should_correctly_return_abs_path_for_root(self):
        root = Directory(name="")
        self.assertEqual(root.abs_path, "/")

    def test_should_correctly_set_parent_dir(self):
        root = Directory(name="")
        child1 = Directory("child1")
        root.add_child(child1)
        self.assertEqual(child1.parent_dir, root)

    def test_should_correctly_return_abs_path_for_child_file(self):
        root = Directory(name="")
        child_level1 = Directory("child1")
        root.add_child(child_level1)
        self.assertEqual(child_level1.abs_path, "/child1/")

        child_level2 = Directory("child2")
        child_level1.add_child(child_level2)
        self.assertEqual(child_level2.abs_path, "/child1/child2/")

    def test_should_return_correct_name(self):
        root = Directory(name="")
        self.assertEqual(root.name, "")
        child_level1 = Directory("child1")
        root.add_child(child_level1)
        self.assertEqual(child_level1.name, "child1")

        child_level2 = Directory("child2")
        child_level1.add_child(child_level2)
        self.assertEqual(child_level2.name, "child2")

    def test_should_correctly_update_size(self):
        root = Directory(name="")
        self.assertEqual(root.size, 0)

        child_level1 = Directory("child1")
        child_level1.add_child(File(size=5, name="foo.txt"))

        self.assertEqual(child_level1.size, 5)
        root.add_child(child_level1)
        self.assertEqual(root.size, 5)

        child_level2 = Directory("child2")
        child_level2.add_child(File(size=20, name="bar.txt"))
        child_level1.add_child(child_level2)
        self.assertEqual(child_level1.size, 25)
        self.assertEqual(root.size, 25)

        root.add_child(File(size=300, name="foo.txt"))
        self.assertEqual(root.size, 325)

    def test_should_correctly_replace_existing_child_on_name_collisions(self):
        root = Directory(name="")
        child_level1 = Directory("child1")
        root.add_child(child_level1)
        root.add_child(Directory(child_level1.name))
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].abs_path, "/child1/")

        root.add_child(File(size=5, name="foo.txt"))
        root.add_child(File(size=5, name="foo.txt"))
        self.assertEqual(len(root.children), 2)
        self.assertEqual({c.abs_path for c in root.children}, {"/child1/", "/foo.txt"})
        self.assertEqual(root.size, 5)

        child_level1.add_child(File(size=3, name="bar.txt"))
        child_level1.add_child(File(size=3, name="bar.txt"))
        self.assertEqual(len(child_level1.children), 1)
        self.assertEqual(child_level1.children[0].abs_path, "/child1/bar.txt")
        self.assertEqual(root.size, 8)

    def test_should_raise_value_error_when_dir_name_collides_with_file_name(self):
        root = Directory(name="")
        d1 = Directory("child1")
        root.add_child(d1)
        self.assertRaises(ValueError, lambda: root.add_child(File(name=d1.name, size=3)))

    def test_should_properly_set_child_parent_dir(self):
        root = Directory(name="")
        child = Directory(name="child")
        root.add_child(child)
        self.assertEqual(child.parent_dir, root)

    def test_should_correctly_find_self(self):
        root = Directory(name="")
        self.assertEqual(root.find("/"), root)

        child = Directory("c1")
        root.add_child(child)
        self.assertEqual(child.find("/c1/"), child)

        child2 = Directory("c2")
        child.add_child(child2)
        child2.find("/c1/c2/")

    def test_should_find_direct_child(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)
        self.assertEqual(root.find("/c1/"), child)

        child2 = Directory("c2")
        child.add_child(child2)
        self.assertEqual(child.find("/c1/c2/"), child2)

        child3 = File(size=3, name="foo.txt")
        child2.add_child(child3)
        self.assertEqual(child2.find("/c1/c2/foo.txt"), child3)

    def test_should_find_child_2_levels_deep(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)

        child2 = Directory("c2")
        child.add_child(child2)

        self.assertEqual(root.find("/c1/c2/"), child2)

        child3 = File(size=3, name="foo.txt")
        child2.add_child(child3)
        self.assertEqual(child.find("/c1/c2/foo.txt"), child3)

        child4 = Directory("c4")
        child2.add_child(child4)
        self.assertEqual(child.find("/c1/c2/c4/"), child4)

    def test_should_find_child_3_levels_deep(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)

        child2 = Directory("c2")
        child.add_child(child2)

        child3 = File(size=3, name="foo.txt")
        child2.add_child(child3)
        self.assertEqual(root.find("/c1/c2/foo.txt"), child3)

    def test_should_return_none_if_not_found(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)
        self.assertIsNone(root.find("/booz"))
        self.assertEqual(root.find("/c1/"), child)
        self.assertIsNone(root.find("/c1/fooz/"))

        c2 = Directory("c2")
        child.add_child(c2)
        self.assertEqual(root.find("/c1/c2/"), c2)
        self.assertIsNone(root.find("/c1/c2/fooo.txt"))

    def test_find_relative_should_correctly_find_level_1(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)
        self.assertEqual(root.find("c1/"), child)

        file = File(size=8, name="foo.txt")
        child.add_child(file)
        self.assertEqual(child.find("foo.txt"), file)

    def test_find_relative_should_correctly_find_level_2(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)

        child2 = Directory("c2")
        child.add_child(child2)
        self.assertEqual(root.find("c1/c2/"), child2)

        file = File(size=8, name="foo.txt")
        child.add_child(file)
        self.assertEqual(root.find("c1/foo.txt"), file)

    def test_find_relative_should_correctly_find_level_3(self):
        root = Directory(name="")
        child = Directory("c1")
        root.add_child(child)

        child2 = Directory("c2")
        child.add_child(child2)

        child3 = Directory("c3")
        child2.add_child(child3)
        self.assertEqual(root.find("c1/c2/c3/"), child3)

        file = File(size=8, name="bar.txt")
        child2.add_child(file)
        self.assertEqual(root.find("c1/c2/bar.txt"), file)


class FileSystemStateTestCase(TestCase):
    def setUp(self):
        self.fs = FileSystem()
        self.fs_state = FileSystemState(self.fs)
        self.cli_output_processor = CliOutputProcessor(self.fs_state)

    def test_should_handle_switching_to_root_dir(self):
        self.cli_output_processor.process_command("$ cd /")
        self.assertEqual(self.fs_state.cwd.abs_path, "/")

    def test_should_handle_switching_to_dir_one_level_down_creating_dirs_on_the_fly(self):
        self.cli_output_processor.process_command("$ cd /bar")
        self.assertEqual(self.fs_state.cwd.abs_path, "/bar/")
        self.assertEqual(len(self.fs.root.children), 1)
        self.assertEqual(self.fs.root.children[0].abs_path, "/bar/")

        self.cli_output_processor.process_command("$ cd foo")
        self.assertEqual(self.fs_state.cwd.abs_path, "/bar/foo/")

    def test_should_handle_switching_up_to_parent_dir(self):
        self.cli_output_processor.process_command("$ cd bar")
        self.assertEqual(self.fs_state.cwd.abs_path, "/bar/")

    def test_should_do_nothing_when_switching_to_parent_while_at_root(self):
        self.cli_output_processor.process_command("$ cd ..")
        self.assertEqual(self.fs_state.cwd.abs_path, "/")

    def test_should_be_able_to_handle_dirs_with_spaces(self):
        self.cli_output_processor.process_command("$ cd test folder")
        self.assertEqual(self.fs_state.cwd.abs_path, "/test folder/")


if __name__ == "__main__":
    unittest.main()
