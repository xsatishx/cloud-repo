import importlib
import os
import sys


def dif(a, b):
    return list(set(a) - set(b))


def module_contents(name):
    
    usuals = ['__builtins__', '__doc__', '__file__', '__name__', '__package__']

    module = importlib.import_module(name)

    return module, dif(dir(module), usuals)


def intersection(c1, c2):
    return [x for x in c1 if x in c2]


def split(path, result=None):
    """
    Split a path into components in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return split(head, [tail] + result)


def patch():

    # getting rid of the /tukey
    local_dir = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]) + '/'

    my_dir = local_dir + 'tukey'
    their_dir = local_dir + 'openstack_dashboard'
    target_dirs = ['api','dashboards', 'usage']

    target_dirs = ['/'.join([my_dir, target]) for target in target_dirs]

    modules = []

    for target_dir in target_dirs:
        for dirpath, dirnames, filenames in os.walk(target_dir):
            # Ignore dirnames that start with '.'
            for i, dirname in enumerate(dirnames):
                if dirname.startswith('.'):
                    del dirnames[i]

            if filenames:
                modules += ['.'.join([dirpath[len(my_dir) + 1:], f[:-3]]).replace('/','.') 
                    for f in filenames if f.endswith(('.py',))
                    and f != '__init__.py']

    for module in modules:

        my_dir = my_dir.split('/')[-1]
        their_dir = their_dir.split('/')[-1]

        my_module_path = '.'.join([my_dir, module])
        their_module_path = '.'.join([their_dir,module])

        my_module, mine = module_contents(my_module_path)
        their_module, theirs = module_contents(their_module_path)


        patchables = intersection(theirs, mine)

        for to_patch in patchables:

            obj_to_patch = getattr(sys.modules[their_module_path], to_patch)

            patch_obj = getattr(sys.modules[my_module_path], to_patch)

            if hasattr(obj_to_patch, '__module__') and hasattr(patch_obj, '__module__'):

                
                setattr(their_module, to_patch, getattr(my_module, to_patch))

