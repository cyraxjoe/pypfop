import os

import pypfop

SKELDIR = os.path.join(pypfop.BASEDIR, 'skeletons')


def skeleton_dir(template_type):
    """Return the absolute path to the skeleton directory
    for the respective template type.
    """
    return os.path.join(SKELDIR, template_type)


class Template(object):

    def render(self, params):
        raise NotImplementedError()


class Factory(object):
    name = ''

    def __call__(self, template):
        raise NotImplementedError()

    @property
    def skel_dir(self):
        return skeleton_dir(self.name)
