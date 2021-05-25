"""
dnfdbus.dnf module
"""
import sys
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




class DnfPackages:

    def __init__(self, backend ) -> None:
        self.backend = backend
        self.base = backend.base
        
    @property
    def installed(self):
        self.backend.setup()
        q = self.base.sack.query()
        q = q.installed()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available(self):
        self.backend.setup()
        q = self.base.sack.query()
        q = q.available()
        q = q.latest()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available_all(self):
        self.backend.setup()
        q = self.base.sack.query()
        q = q.available()
        return [DnfPkg(pkg) for pkg in q]

class DnfBackend:

    def __init__(self, base) -> None:
        self.base = base
        self.is_setup = False
        self._packages = None

    @property
    def packages(self):
        if not self._packages:
            self._packages = DnfPackages(self)
        return self._packages

    def setup(self):
        if not self.is_setup:
            _ = self.base.read_all_repos()
            #_ = self.base.fill_sack()
            _ = self.base.fill_sack_from_repos_in_cache()
            self.is_setup = True


    def get_repositories(self):
        self.setup()
        return [DnfRepository(self.base.repos[repo]) for repo in self.base.repos]


if __name__ == "__main__":
    b = DnfBackend(dnf.Base())
    pkgs = b.packages
    inst = pkgs.available
    cnt = 0
    print("TEST_PKGS = [")
    for pkg in inst:
        print(f'    "{str(pkg)}",')
        cnt += 1
        if cnt == 10:
            break
    print("]")

    sys.exit(0)
    repos = b.get_repositories()
    print(repos)
    for repo in repos:
        print(repo.id, repo.name, repo.enabled)
    