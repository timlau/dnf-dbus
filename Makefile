PKGNAME = dnfdbus
APPNAME = $(PKGNAME)
DATADIR := /usr/share
SYSCONFDIR := /etc
PKGDIR = $(DATADIR)/$(PKGNAME)
SYSTEMDSYSTEMUNITDIR := /usr/lib/systemd/system
ORG_NAME = dk.rasmil.DnfDbus
ORG_RO_NAME = org.baseurl.DnfSession
SUBDIRS = python
VERSION=$(shell awk '/Version:/ { print $$2 }' ${PKGNAME}.spec)
TESTLIBS=src/:test:/
GITDATE=git$(shell date +%Y%m%d)
VER_REGEX=\(^Version:\s*[0-9]*\.[0-9]*\.\)\(.*\)
BUMPED_MINOR=${shell VN=`cat ${APPNAME}.spec | grep Version| sed  's/${VER_REGEX}/\2/'`; echo $$(($$VN + 1))}
NEW_VER=${shell cat ${APPNAME}.spec | grep Version| sed  's/\(^Version:\s*\)\([0-9]*\.[0-9]*\.\)\(.*\)/\2${BUMPED_MINOR}/'}
NEW_REL=0.1.${GITDATE}
DIST=${shell rpm --eval "%{dist}"}
GIT_MASTER=master
CURDIR = ${shell pwd}
BUILDDIR= $(CURDIR)/build

show-vars:
	@echo $(VERSION)
	@echo ${GITDATE}
	@echo ${BUMPED_MINOR}
	@echo ${NEW_VER}-${NEW_REL}	

install:
	mkdir -p $(DESTDIR)$(DATADIR)/dbus-1/system-services
	mkdir -p $(DESTDIR)$(DATADIR)/dbus-1/services
	mkdir -p $(DESTDIR)$(SYSCONFDIR)/dbus-1/system.d
	mkdir -p $(DESTDIR)$(DATADIR)/polkit-1/actions
	mkdir -p $(DESTDIR)$(PKGDIR)
	mkdir -p $(DESTDIR)/usr/lib/systemd/system
	install -m644 dbus/$(ORG_NAME).service $(DESTDIR)$(DATADIR)/dbus-1/system-services/.				
	install -m644 dbus/dnfdbus.service $(DESTDIR)$(SYSTEMDSYSTEMUNITDIR)/.				
	install -m644 dbus/$(ORG_NAME).conf $(DESTDIR)$(SYSCONFDIR)/dbus-1/system.d/.				
	install -m644 policykit1/$(ORG_NAME).policy $(DESTDIR)$(DATADIR)/polkit-1/actions/.				
	install -m755 daemon/dnfdbus.py $(DESTDIR)/$(PKGDIR)/dnfdbus

selinux:
	@$(MAKE) install
	semanage fcontext -a -t rpm_exec_t $(DESTDIR)/$(PKGDIR)/dnfdbus
	restorecon $(DESTDIR)/$(PKGDIR_DNF)/dnfdbus
	
run-tests:
	@PYTHONPATH=$(TESTLIBS) python3 -m unittest -v test/*.py

build-setup:
	@rm -rf build/  &>/dev/null ||:
	@mkdir -p build/SOURCES ||:
	@mkdir -p build/SRPMS ||:
	@mkdir -p build/RPMS ||:
	@mkdir -p build/BUILD ||:
	@mkdir -p build/BUILDROOT ||:

test-cleanup:	
	@rm -rf ${APPNAME}-${VERSION}.test.tar.gz
	@echo "Cleanup the git release-test local branch"
	@git checkout -f
	@git checkout ${GIT_MASTER}
	@git branch -D release-test

test-release:
	$(MAKE) build-setup
	@git checkout -b release-test
	# +1 Minor version and add 0.1-gitYYYYMMDD release
	@cat ${APPNAME}.spec | sed  -e 's/${VER_REGEX}/\1${BUMPED_MINOR}/' -e 's/\(^Release:\s*\)\([0-9]*\)\(.*\)./\10.1.${GITDATE}%{?dist}/' > ${APPNAME}-test.spec ; mv ${APPNAME}-test.spec ${APPNAME}.spec
	@git commit -a -m "bumped ${APPNAME} version ${NEW_VER}-${NEW_REL}"
	# Make archive
	@rm -rf ${APPNAME}-${NEW_VER}.tar.gz
	@git archive --format=tar --prefix=$(PKGNAME)-$(NEW_VER)/ HEAD | xz >build/SOURCES/${PKGNAME}-$(NEW_VER).tar.xz
	# Build RPMS 
	@-rpmbuild --define '_topdir $(BUILDDIR)' -ba ${PKGNAME}.spec
	@$(MAKE) test-cleanup


PNONY: run-tests selinux install build-setup test-release test-cleanup show-vars


