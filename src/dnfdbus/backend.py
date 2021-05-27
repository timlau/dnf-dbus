"""
dnfdbus.dnf module
"""
import sys
import json
from typing import Dict
import dnf

class DnfRepository:
    """
    Wrapper for the dnf.repo.Repo class
    """

    def __init__(self, repo) -> None:
        self.repo = repo

    @property
    def id(self):
        return self.repo.id

    @property
    def name(self):
        return self.repo.name
    
    @property
    def enabled(self):
        return self.repo.enabled

    @property    
    def dump(self) -> Dict:
        return  {'id': self.id, 'name': self.name, 'enabled': self.enabled}
        

class DnfPkg:
    """ Wrapper for dnf po"""
    
    def __init__(self, pkg) -> None:
        self.pkg = pkg

    def __str__(self):
        return str(self.pkg)

    def __repr__(self):
        return(f'DnfPkg({str(self.pkg)})')

    @property
    def name(self):
        return self.pkg.name

    @property
    def version(self):
        return self.pkg.version

    @property
    def release(self):
        return self.pkg.release

    @property
    def arch(self):
        return self.pkg.arch

    @property
    def epoch(self):
        return self.pkg.epoch

    @property    
    def dump(self) -> str:
        return str(self.pkg)



class DnfPackages:

    def __init__(self, backend ) -> None:
        self.backend = backend
        self.base = backend.base
        
    @property
    def installed(self):
        ''' Get list of installed packages'''
        self.backend.setup()
        q = self.base.sack.query()
        q = q.installed()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available(self):
        ''' Get list of lastest available packages'''
        self.backend.setup()
        q = self.base.sack.query().available().latest()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available_all(self):
        ''' Get list of all available packages'''
        self.backend.setup()
        q = self.base.sack.query()
        q = q.available()
        return [DnfPkg(pkg) for pkg in q]

    def by_key(self, key):
        """ find packages the match a key (Ex. '*qt6*') """
        self.backend.setup()
        subject = dnf.subject.Subject(key)
        q = subject.get_best_query(self.base.sack)
        return [DnfPkg(pkg) for pkg in q]

class DnfBackend:

    def __init__(self, base) -> None:
        self.base = base
        self.is_setup = False
        self._packages = None

    @property
    def packages(self):
        ''' Get tha package object'''
        if not self._packages:
            self._packages = DnfPackages(self)
        return self._packages

    def setup(self):
        ''' Setup Dnf load repository info & fill the sack '''
        if not self.is_setup:
            _ = self.base.read_all_repos()
            #_ = self.base.fill_sack()
            _ = self.base.fill_sack_from_repos_in_cache()
            self.is_setup = True


    def get_repositories(self) -> list:
        ''' Get list of repositories'''
        self.setup()
        return [DnfRepository(self.base.repos[repo]) for repo in self.base.repos]


if __name__ == "__main__":
    b = DnfBackend(dnf.Base())
    pkgs = b.packages
    res = pkgs.by_key("*qt6*")
    for pkg in res:
        print(f'    "{str(pkg)}",')
    