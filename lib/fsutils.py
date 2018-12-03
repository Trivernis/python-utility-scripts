import os
import shutil


def dir_exist_guarantee(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def get_extension(fname: str):
    return fname.split('.')[-1]


class FileInfo:
    """ A simple wrapper around the os path functions that returns basic file info
     and let's you peform basic file tasks."""
    def __init__(self, fname: str):
        self._init_info(fname)

    def _init_info(self, fname):
        """ Set's all the required variables for performing file tasks and to
         access when working with the file object. """
        # stringvars
        self._path = os.path.normpath(fname.replace('\\', '/')).encode('utf-8')
        if not os.path.isfile(self._path):
            raise Exception("Not a File")
        self._extless, self.extension = os.path.splitext(self._path)
        self.dirname, self.basename = os.path.split(self._path)
        self.fullname = os.path.join(self.dirname, self.basename)
        # boolvars
        self.exist = os.path.exists(self.fullname)
        self.ismount = self.islink = False
        if self.exist:
            self.ismount = os.path.ismount(self.fullname)
            self.islink = os.path.islink(self.fullname)

    def delete(self):
        """ Deletes the file if it exists.
         Does nothing, if it does not exist."""
        if self.exist:
            os.remove(self.fullname)

    def create(self):
        """ Creates the file if it doesn't exist.
         Does nothing, if it does."""
        if not self.exist:
            with open(self.fullname, 'w') as f:
                f.write('');

    def reset(self):
        """ Opens the file and writes nothing into it. """
        with open(self.fullname, 'w') as f:
            f.write('')

    def open(self, mode: str):
        """ Returns the file opened with the open method. """
        self.create()
        return open(self.fullname, mode)

    def copy(self, dest: str):
        if self.exist:
            shutil.copyfile(self.fullname, dest)
            return FileInfo(dest)

    def move(self, dest: str):
        if self.exist:
            shutil.move(self.fullname, dest)
            self._init_info(dest)
        else:
            self._init_info(dest)


class DirInfo:
    """ A simple wrapper around the os path functions that returns basic directory info
     and let's you peform basic directory tasks."""

    def __init__(self, dirname: str):
        self._init_info(dirname)

    def _init_info(self, dirname: str):
        """ Set's all the required variables for performing file tasks and to
         access when working with the file object. """
        # stringvars
        self._path = os.path.normpath(dirname.replace('\\', '/')).encode('utf-8')
        if not os.path.isdir(self._path):
            raise Exception("Not a Directory")
        self.parent_dir, self.basename = os.path.split(self._path)
        self.fullname = os.path.join(self.parent_dir, self.basename)
        # boolvars
        self.exist = os.path.exists(self.fullname)
        self.ismount = self.islink = False
        if self.exist:
            self.ismount = os.path.ismount(self.fullname)
            self.islink = os.path.islink(self.fullname)

    def get_content(self) -> list:
        """ Returns the content of the directory without subdirectory contents. """
        return os.listdir(self.fullname)

    def get_full_content(self) -> list:
        """ Returns the content of the direcdtory tree. """
        content = []
        for dirname, dirnames, filenames in os.walk(self.fullname):
            # print path to all subdirectories first.
            for subdirname in dirnames:
                content.append(os.path.join(dirname, subdirname).decode('utf-8'))

            # print path to all filenames.
            for filename in filenames:
                content.append(os.path.join(dirname, filename).decode('utf-8'))
        return content

    def delete(self):
        shutil.rmtree(self.fullname)

    def delete_empty(self):
        """ Deletes the directory if it is empty. Raises an Exception if it is not. """
        if len(self.get_content()):
            raise Exception('Directory not empty')
        else:
            self.delete()

    def create(self):
        if not self.exist:
            os.mkdir(self.fullname)
            self._init_info(self.fullname)
