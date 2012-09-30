from provy.core.roles import Role
from provy.more.debian import AptitudeRole


class ApacheRole(Role):
    def provision(self):
        with self.using(AptitudeRole) as aptitude:
            aptitude.ensure_package_installed('apache2')

    def ensure_mod(self, mod):
        with self.using(AptitudeRole) as aptitude:
            aptitude.ensure_package_installed('libapache2-mod-%s' % mod)

        self.execute('a2enmod %s' % mod, sudo=True)