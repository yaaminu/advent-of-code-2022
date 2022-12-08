#!/usr/bin/env python3
import collections
import sys


class FileSystemObject:
    @property
    def size(self):
        raise NotImplementedError()

    @property
    def abs_path(self):
        raise NotImplementedError()

    @property
    def parent_dir(self):
        raise NotImplementedError()

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def level(self):
        raise NotImplementedError()

    def on_added_to_parent_dir(self, parent_dir):
        raise NotImplementedError()


class File(FileSystemObject):

    def __init__(self, name, size):
        self._parent_dir = None
        self._name = name
        self._size = size
        self._level = 0

    @property
    def size(self):
        return self._size

    @property
    def name(self):
        return self._name

    @property
    def abs_path(self):
        return self.parent_dir.abs_path + self.name

    @property
    def level(self):
        return self._level

    def on_added_to_parent_dir(self, parent_dir):
        self._parent_dir = parent_dir
        self._level = parent_dir.level + 1

    @property
    def parent_dir(self):
        return self._parent_dir


class Directory(FileSystemObject):
    def __init__(self, name):
        self._parent_dir = None
        self._name = name
        self._children = []
        self._size = 0
        self._level = 0

    @property
    def name(self):
        return self._name

    @property
    def abs_path(self):
        return self.parent_dir.abs_path + self.name + "/" if self.parent_dir else "/"

    @property
    def level(self):
        return self._level

    def add_child(self, child):
        old_size = self._size

        existing_index = -1
        for index, c in enumerate(self._children):
            if c.name == child.name:
                existing_index = index
                break
        if existing_index != -1:
            if isinstance(self._children[existing_index], Directory) and isinstance(child, File):
                raise ValueError()
            elif isinstance(self._children[existing_index], File) and isinstance(child, Directory):
                raise ValueError()
            self._size = self.size + child.size - self._children[existing_index].size
            self._children[existing_index] = child
        else:
            self._size += child.size
            self._children.append(child)
        child.on_added_to_parent_dir(self)
        if self.parent_dir:
            self.parent_dir.on_child_size_changed(self, old_child_size=old_size)

    def on_added_to_parent_dir(self, parent_dir):
        self._parent_dir = parent_dir
        self._level = parent_dir.level + 1

    def on_child_size_changed(self, child, old_child_size):
        old_size = self._size
        self._size += child.size - old_child_size
        if self.parent_dir:
            self.parent_dir.on_child_size_changed(self, old_child_size=old_size)

    @property
    def size(self):
        return self._size

    @property
    def parent_dir(self):
        return self._parent_dir

    @property
    def children(self):
        return [c for c in self._children]  # ideally should return a deep copy but no time :-(

    def find(self, path):
        if path.startswith("/"):
            return self._find_absolute(path)
        return self._find_absolute(self.abs_path + path)

    def _find_absolute(self, abs_path):
        if self.abs_path == abs_path:
            return self
        # avoid unnecessary lookup
        if self.level > len(abs_path.split("/")[1:-1]):
            return None
        for child in self._children:
            found = None
            if isinstance(child, Directory):
                found = child.find(abs_path)
            elif child.abs_path == abs_path:
                found = child
            if found is not None:
                return found
        return None


class FileSystem:
    def __init__(self):
        self.root = Directory(name="")

    @property
    def total_size(self):
        return self.root.size

    def find(self, abs_path):
        return self.root.find(abs_path)


class FileSystemState:
    def __init__(self, fs):
        self.fs = fs
        self._cwd = self.fs.root
        self._listing = False

    def cd(self, path):
        """
        changes current dir to {path} creating it if it doesn't exist
        """
        if path == self.cwd.abs_path or path == self.cwd.name:
            return
        if path == "..":
            if self._cwd == self.fs.root:
                return
            self._cwd = self._cwd.parent_dir
        else:
            new_dir = Directory(name=path.strip("/"))
            self._cwd.add_child(new_dir)
            self._cwd = new_dir

    def new_dir(self, dir_name):
        self._cwd.add_child(Directory(dir_name))

    def new_file(self, file_name, file_size):
        self._cwd.add_child(File(name=file_name, size=file_size))

    @property
    def cwd(self):
        return self._cwd


class CliOutputProcessor:

    def __init__(self, fs_state_machine):
        self._fs_state = fs_state_machine

    def process_command(self, cmd):
        if cmd.startswith("$ cd "):
            dirname = cmd.split(" ", maxsplit=2)[2]
            self._fs_state.cd(dirname)
        elif cmd.startswith("$ ls"):
            # listing dir #NOP
            pass
        elif cmd.startswith("dir "):
            dirname = cmd.split(" ", maxsplit=1)[1]
            self._fs_state.new_dir(dirname)
        else:
            size, filename = cmd.split(" ", maxsplit=1)
            self._fs_state.new_file(file_name=filename, file_size=int(size))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: fs_full.py {input-file}")
        exit(1)
    input_file = sys.argv[1]
    fs = FileSystem()
    fs_state = FileSystemState(fs)
    cli_output_processor = CliOutputProcessor(fs_state)
    dir_to_delete = {}

    for command in open(input_file, "r"):
        cli_output_processor.process_command(command.strip("\n"))


    def sum_dirs_with_max_100_000():
        dirs_with_max_100_000 = []

        q = collections.deque()
        q.appendleft(fs.root)
        while len(q) > 0:
            curr_entry = q.pop()
            if isinstance(curr_entry, Directory) and curr_entry.size <= 100_000:
                dirs_with_max_100_000.append(curr_entry)
            if isinstance(curr_entry, Directory):
                q.extendleft(curr_entry.children)

        print(f"sum of all dirs below 100_000: {sum([d.size for d in dirs_with_max_100_000], 0)}")


    def has_enough_space_for_update():
        min_deletable_entry = None

        q = collections.deque()
        q.appendleft(fs.root)
        free_space = 70000000 - fs.total_size
        space_to_free = max(30000000 - free_space, 0)
        while len(q) > 0:
            cur_entry = q.pop()
            if not cur_entry:
                continue
            if cur_entry.size >= space_to_free and (
                    min_deletable_entry is None or cur_entry.size < min_deletable_entry.size):
                min_deletable_entry = cur_entry
            # only add if we have a chance of finding something better down below!
            if cur_entry.size > space_to_free and isinstance(cur_entry, Directory):
                q.extendleft(cur_entry.children)

        print(f"min_size_to_delete: {min_deletable_entry.size}")


    sum_dirs_with_max_100_000()

    has_enough_space_for_update()
