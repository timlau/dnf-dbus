%global dnf_org dk.rasmil.DnfDbus
%global dnf_version 4.2.6

Name:           dnfdbus
Version:        1.0.0
Release:        1%{?dist}
Summary:        DBus daemon for dnf package actions

License:        GPLv3+
URL:            https://github.com/timlau/dnf-dbus
Source0:        %{url}/releases/download/%{name}-%{version}/%{name}-%{version}.tar.xz

BuildArch:      noarch
BuildRequires:  python3-devel >= 3.9
BuildRequires:  make
BuildRequires:  systemd

Requires:       python3-gobject
Requires:       python3-dnf >= %{dnf_version}
Requires:       polkit
Requires:       python3-%{name} = %{version}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Dbus daemon for performing package actions with the dnf package manager


%package selinux
Summary:        SELinux integration for dnfdbus

Requires:       %{name} = %{version}-%{release}

Requires(post):     policycoreutils-python-utils
Requires(postun):   policycoreutils-python-utils

%description selinux
Metapackage customizing the SELinux policy to ensure dnfdbus works with
SELinux enabled in enforcing mode.


%package -n python3-%{name}
Summary:        %{name} python3 modules

BuildRequires:  python3-devel
Requires:       python3-dasbus

%{?python_provide:%python_provide python3-%{name}}

%description -n python3-%{name}
%{name} python3 modules


%prep
%autosetup

%build
%py3_build


%install
rm -rf $RPM_BUILD_ROOT
%py3_install
make install DESTDIR=%{buildroot} DATADIR=%{_datadir} SYSCONFDIR=%{_sysconfdir}

%files
%doc README.md
%license LICENSE
%{_datadir}/dbus-1/system-services/%{dnf_org}*
%{_datadir}/%{name}/
%{_unitdir}/%{name}.service
%{_datadir}/polkit-1/actions/%{dnf_org}*
%{_sysconfdir}/dbus-1/system.d/%{dnf_org}*

%files selinux
# empty metapackage

%files -n  python3-%{name}
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info/


%post
%systemd_post %{name}.service

%postun
%systemd_postun %{name}.service

%preun
%systemd_preun %{name}.service

%post selinux
# apply the right selinux file context
# http://fedoraproject.org/wiki/PackagingDrafts/SELinux#File_contexts
semanage fcontext -a -t rpm_exec_t '%{_datadir}/%{name}/%{name}' 2>/dev/null || :
restorecon -R %{_datadir}/%{name}/%{name} || :

%postun selinux
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t rpm_exec_t '%{_datadir}/%{name}/%{name}' 2>/dev/null || :
fi


%changelog
* Tue May 25 2021 Tim Lauridsen <timlau@fedoraproject.org> 1.0.0-1
- Intial Package