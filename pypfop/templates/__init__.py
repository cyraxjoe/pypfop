import os


BASEDIR = os.path.abspath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__),
        '..'
    )
)
SKELDIR = os.path.join(BASEDIR, 'skeletons')


def skeleton_dir(template_type):
    """Return the absolute path to the skeleton directory
    for the respective template type.
    """
    return os.path.join(SKELDIR, template_type)


class Template:

    def render(self, params):
        raise NotImplementedError()


class Factory:
    name = ''

    def __call__(self, template):
        raise NotImplementedError()

    @property
    def skel_dir(self):
        return skeleton_dir(self.name)
