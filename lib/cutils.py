
class ProgressBar:
    def __init__(self, total=100, prefix='', suffix='', length=50, fill='█'):
        self.prefix = prefix
        self.suffix = suffix
        self.fill = fill
        self.length = length
        self.total = total
        self.progress = 0

    def tick(self):
        self.progress += 1
        self._print_progress()

    def setprogress(self, progress):
        self.progress = progress
        self._print_progress()

    def _print_progress(self):
        iteration = self.progress
        total = self.total
        prefix = self.prefix
        suffix = self.suffix

        percent = ("{0:." + str(1) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(self.length * iteration // total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()
