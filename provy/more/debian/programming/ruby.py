#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roles in this namespace are meant to provide Ruby utility methods for Debian distributions.
'''

from fabric.api import settings

from provy.core import Role
from provy.more.debian import AptitudeRole

class RubyRole(Role):
    '''
    This role provides Ruby utilities for Debian distributions.

    <em>Sample usage</em>
    <pre class="sh_python">
    from provy.core import Role
    from provy.more.debian import NodeJsRole

    class MySampleRole(Role):
        def provision(self):
            self.provision_role(RubyRole)
    </pre>
    '''

    version = "1.9.2"
    patch = 290
    url = "http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-%s-p%d.tar.gz"

    def __symlink_from_local(self):
        commands = "erb gem irb rake rdoc ri ruby testrb"

        for command in commands.split():
            self.remove_file('/usr/bin/%s' % command, sudo=True)
            self.remote_symlink('/usr/local/bin/%s' % command, '/usr/bin/%s' % command, sudo=True)

    def provision(self):
        '''
        Installs Ruby and its dependencies. This method should be called upon if overriden in base classes, or Ruby won't work properly in the remote server.
        <em>Sample usage</em>
        <pre class="sh_python">
        from provy.core import Role
        from provy.more.debian import RubyRole

        class MySampleRole(Role):
            def provision(self):
                self.provision_role(RubyRole) # no need to call this if using with block.

        </pre>
        '''
        with self.using(AptitudeRole) as role:
            for package in 'build-essential zlib1g zlib1g-dev libreadline5 libreadline5-dev libssl-dev libyaml-dev'.split():
                role.ensure_package_installed(package)

            with settings(warn_only=True):
                result = self.execute('gem --version | egrep 1.9.2', stdout=False)

            if not result or 'command not found' in result.lower():
                self.log('ruby 1.9.2 not found! Installing...')
                ruby_url = self.url % (self.version, self.patch)
                self.execute('cd /tmp && wget %s && tar xzf ruby-1.9.2-p0.tar.gz && cd ruby-1.9.2-p0 && ./configure && make && make install' % ruby_url, sudo=True, stdout=False)
                self.remove_file('/tmp/ruby-1.9.2-p0.tar.gz', sudo=True)

                self.__symlink_from_local()
                self.log('ruby 1.9.2 installed!')

