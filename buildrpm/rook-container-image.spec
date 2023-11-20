{{{$version := printf "%s.%s.%s" .major .minor .patch}}}
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif
%{!?registry_url: %global registry_url container-registry.oracle.com/olcne}
%{!?registry: %global registry container-registry.oracle.com/olcne}
%global _name   	rook
%global _buildhost	build-ol%{?oraclelinux}-%{?_arch}.oracle.com
%ifarch %{arm} arm64 aarch64
%global arch aarch64
%else
%global arch x86_64
%endif


Name:           %{_name}-container-image
Version:        {{{$version}}}
Release:        1%{?dist}
Summary:        Rook container image
License:        Apache-2.0
Group:          System/Management
Url:            https://github.com/rook/rook
Source:         %{name}-%{version}.tar.bz2

BuildRequires: python36
BuildRequires: podman

%description
Rook container image

%prep
%setup -q -n %{name}-%{version}

%build
# NOTE: Make sure ceph image built before rook
%global ceph_tag %{registry_url}/ceph:v%{ceph_version}

%global rook_rpm %{_name}-%{version}-%{release}.%{arch}
%global rook_tag %{registry}/ceph:v%{version}
dnf clean all && \
  yumdownloader --destdir=${PWD}/rpms %{rook_rpm}
podman build \
    --build-arg BASE_IMAGE=%{ceph_tag} \
    %{build_args} \
    -t %{rook_tag} -f ./olm/builds/Dockerfile.rook .
podman save -o %{_name}.tar %{rook_tag}

%install
%__install -D -m 644 %{_name}.tar %{buildroot}/usr/local/share/olcne/%{_name}.tar

%files
%license LICENSE
/usr/local/share/olcne/%{_name}.tar

%changelog
* {{{.changelog_timestamp}}} - {{{ $version }}}-1
- Added Oracle specific files for {{{ $version }}}-1
