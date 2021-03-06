#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roles in this namespace are meant to provide virtual environments and run commands inside a `virtualenv <http://www.virtualenv.org/>`_, for Debian distributions.
'''

from contextlib import contextmanager
import os

from provy.core import Role


class VirtualenvRole(Role):
    '''
    This role provides `virtualenv <http://www.virtualenv.org/>`_ management.
    It also provides `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_ provisioning, although it's not internally used in this role.

    When using the object as a context manager (that is, using a `with` block) it will make sure that the virtual environment is created and that the commands
    that run inside it run within this same virtual environment (which affects, for example, the `python` and `pip` commands).

    If the virtual environment already exists, it just bypasses the creation procedure.

    :param env_name: Name of the virtual environment to be created and to keep activated when running commands inside the context manager.
    :type env_name: :class:`str`
    :param system_site_packages: If :data:`True`, will include system-wide site-packages in the virtual environment. Defaults to :data:`False`.
    :type system_site_packages: :class:`bool`
    :ivar base_directory: (:class:`str`) Directory where the virtual environment subdirectory will be put at.
        For example, if you set it as "/home/johndoe/my_envs", and use venv("some_env"), it will create a virtual environment at "/home/johndoe/my_envs/some_env".
        Defaults to $HOME/.virtualenvs (or :attr:`venv.user` `/.virtualenvs`, if the user is explicitly set - see below -).
    :ivar user: (:class:`str`) The user with which the virtual environment should be created. Defaults to the context user.

    Example:
    ::

        from provy.core import Role
        from provy.more.debian import VirtualenvRole

        class MySampleRole(Role):
            def provision(self):

                # this example uses the defaults provided
                with self.using(PipRole) as pip, self.using(VirtualenvRole) as venv, venv('fancylib'):
                    pip.ensure_package_installed('django')

                # this is when you want to set a different base virtualenv directory and user, and include the system-wide site-packages.
                with self.using(PipRole) as pip, self.using(VirtualenvRole) as venv:
                    venv.base_directory = '/home/johndoe/Envs'
                    venv.user = 'johndoe'
                    with venv('fancylib2', system_site_packages=True):
                        pip.ensure_package_installed('tornado')
    '''

    def __init__(self, prov, context):
        super(VirtualenvRole, self).__init__(prov, context)
        self.user = context['user']
        self.base_directory = None

    def get_base_directory(self):
        '''
        Gets the base directory that will be used to create the virtual environment.

        By default, it returns a subdir under the current venv user home and ".virtualenvs".
        If you wish to change the directory where it gets created, just set :attr:`role.base_directory <base_directory>`

        Example:
        ::

            from provy.core import Role
            from provy.more.debian import VirtualenvRole

            class MySampleRole(Role):
                def provision(self):
                    with self.using(VirtualenvRole) as venv:
                        venv.user = 'johndoe'
                        venv.get_base_directory() # "/home/johndoe/.virtualenvs"
                        venv.base_directory = '/home/johndoe/Envs'
                        venv.get_base_directory() # "/home/johndoe/Envs"
        '''
        return self.base_directory or os.path.join(self.__get_user_dir(), '.virtualenvs')

    def __get_user_dir(self):
        if self.user == 'root':
            return '/root'
        else:
            return '/home/%s' % self.user

    def env_dir(self, env_name):
        '''
        Gets the virtual environment directory for a given environment name.

        Please note that this doesn't check if the env actually exists.

        :param env_name: Name of the virtual environment to be used to build a directory string.
        :type env_name: :class:`str`
        :return: The directory to be used.
        :rtype: :class:`str`

        Example:
        ::

            from provy.core import Role
            from provy.more.debian import VirtualenvRole

            class MySampleRole(Role):
                def provision(self):
                    with self.using(VirtualenvRole) as venv, venv('fancylib'):
                        venv.env_dir('fancylib')
        '''
        return os.path.join(self.get_base_directory(), env_name)

    @contextmanager
    def __call__(self, env_name, system_site_packages=False):
        from fabric.api import prefix

        if not self.env_exists(env_name):
            self.create_env(env_name, system_site_packages=system_site_packages)

        with prefix('source %s/bin/activate' % self.env_dir(env_name)):
            yield

    def provision(self):
        '''
        Installs virtualenv and virtualenvwrapper, and their dependencies.
        This method should be called upon if overriden in base classes, or virtualenv won't work properly in the remote server.

        Example:
        ::

            from provy.core import Role
            from provy.more.debian import VirtualenvRole

            class MySampleRole(Role):
                def provision(self):
                    self.provision_role(VirtualenvRole) # does not need to be called if using with block.
        '''

        from provy.more.debian import PipRole

        with self.using(PipRole) as pip:
            pip.ensure_package_installed('virtualenv')
            pip.ensure_package_installed('virtualenvwrapper')

    def create_env(self, env_name, system_site_packages=False):
        '''
        Creates a virtual environment.

        :param env_name: Name of the virtual environment to be created.
        :type env_name: :class:`str`
        :param system_site_packages: If :data:`True`, will include system-wide site-packages in the virtual environment. Defaults to :data:`False`.
        :type system_site_packages: :class:`bool`

        Examples:
        ::

            from provy.core import Role
            from provy.more.debian import VirtualenvRole

            class MySampleRole(Role):
                def provision(self):
                    with self.using(VirtualenvRole) as venv:
                        env_dir = venv.create_env('fancylib') # will return the directory where the virtual environment was created
        '''
        env_dir = self.env_dir(env_name)
        site_packages_arg = '--system-site-packages ' if system_site_packages else ''
        self.execute('virtualenv %s%s' % (site_packages_arg, env_dir), user=self.user)
        return env_dir

    def env_exists(self, env_name):
        '''
        Checks if a virtual environment exists.

        :param env_name: Name of the virtual environment to be checked.
        :type env_name: :class:`str`
        :return: Whether the virtual environment exists.
        :rtype: :class:`bool`

        Example:
        ::

            from provy.core import Role
            from provy.more.debian import VirtualenvRole

            class MySampleRole(Role):
                def provision(self):
                    with self.using(VirtualenvRole) as venv:
                        venv.env_exists('fancylib') # True or False
        '''
        return self.remote_exists_dir(self.env_dir(env_name))
