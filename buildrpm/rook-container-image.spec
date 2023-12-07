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
%global custom_arch arm64
%else
%global arch x86_64
%global custom_arch amd64
%endif
%global ceph_version "17.2.5"


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
%global ceph_tag container-registry.oracle.com/olcne/ceph:v%{ceph_version}
if [[ $( podman pull %{ceph_tag} ) && \
      $( podman inspect -t image -f "{{.Architecture}}"  %{ceph_tag} ) = %{custom_arch} ]];then
     echo "Using ceph image from ocr"
elif [[ $( podman pull %{registry_url}/ceph:v%{ceph_version} ) && \
        $( podman inspect -t image -f "{{.Architecture}}"  %{registry_url}/ceph:v%{ceph_version} ) = %{custom_arch} ]];then
    podman rmi -f %{ceph_tag}
    podman tag %{registry_url}/ceph:v%{ceph_version} %{ceph_tag}
else
     echo "Ceph:v%{ceph_version} doesn't exist"
     exit 1
fi

%global rook_rpm %{_name}-%{version}-%{release}.%{arch}
%global rook_tag %{registry}/ceph:v%{version}
dnf clean all && \
  yumdownloader --destdir=${PWD}/rpms %{rook_rpm} && \
  yumdownloader --destdir=${PWD}/rpms s5cmd
podman build \
    --build-arg BASE_IMAGE=%{ceph_tag} \
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
