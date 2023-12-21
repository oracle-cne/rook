{{{$version := printf "%s.%s.%s" .major .minor .patch}}}
%global _buildhost          build-ol%{?oraclelinux}-%{?_arch}.oracle.com
%global debug_package   %{nil}

%global app_name rook
%global app_version {{{$version}}}
%global oracle_release_version 1

%global yqv3_version 3.3.0
%global yqv4_version 4.14.2
%global operatorsdk_version 0.17.1
%global helm_version 3.6.2
%global controllergen_version 0.11.3
%global kubectl_version 1.14
%ifarch %{arm} arm64 aarch64
%global arch arm64
%else
%global arch amd64
%endif

Name:    %{app_name}
Version: %{app_version}
Release: %{oracle_release_version}%{?dist}
Summary: Rook cloud native storage operator
License: Apache License 2.0
URL:     https://github.com/rook/rook
Source0: %{name}-%{version}.tar.bz2

Requires:       s5cmd

BuildRequires:  golang >= 1.20.12
BuildRequires:  helm = %{helm_version}
BuildRequires:  yq = %{yqv3_version}
BuildRequires:  yq4 = %{yqv4_version}
BuildRequires:  operator-sdk = %{operatorsdk_version}
BuildRequires:  kube-controller-tools = %{controllergen_version}
BuildRequires:  kubectl >= %{kubectl_version}

%description

%prep
%setup -q

%build

# The Rook build pulls in some third party build tools and installs
# them locally.  Take the versions installed as build dependencies
# and copy them to the local installation paths so that the Rook
# build will consume them.  Historically, Rook has been sensitive
# to the versions of these tools.  If builds start failing without
# a clear reason, these build dependencies are a good spot to
# start looking
mkdir -p .cache/tools/linux_%{arch}/
cp `which operator-sdk` .cache/tools/linux_%{arch}/operator-sdk-v%{operatorsdk_version}
cp `which yq` .cache/tools/linux_%{arch}/yq-%{yqv3_version}
cp `which yq4` .cache/tools/linux_%{arch}/yq-v%{yqv4_version}
cp `which controller-gen` .cache/tools/linux_%{arch}/controller-gen-v%{controllergen_version}
cp `which helm` .cache/tools/linux_%{arch}/helm-v%{helm_version}

# Build everything
mkdir -p `pwd`/_output/templates
make VERSION={{{$version}}} BUILD_CONTAINER_IMAGE=false TEMP=`pwd`/_output/templates build

%install
# Refer to images/ceph/Dockerfile to see how/why files
# are chosen for this package
install -m 755 -d %{buildroot}/usr/local/bin
install -m 755 -d %{buildroot}/etc
install -m 755 -d %{buildroot}/etc/ceph-csv-templates
install -m 755 -d %{buildroot}/etc/rook-external
install -m 755 _output/bin/linux_%{arch}/rook %{buildroot}/usr/local/bin/rook
install -m 755 images/ceph/set-ceph-debug-level %{buildroot}/usr/local/bin/set-ceph-debug-level
install -m 755 images/ceph/toolbox.sh %{buildroot}/usr/local/bin/toolbox.sh

cp -r deploy/examples/monitoring %{buildroot}/etc/ceph-monitoring
cp -r deploy/examples/create-external-cluster-resources.* %{buildroot}/etc/rook-external
install -m 755 -d %{buildroot}/etc/rook-external/test-data
install tests/ceph-status-out %{buildroot}/etc/rook-external/test-data/ceph-status-out
#cp -r _output/templates/* %{buildroot}/etc/ceph-csv-templates

%files
%license LICENSE THIRD_PARTY_LICENSES.txt

/usr/local/bin/rook
/usr/local/bin/set-ceph-debug-level
/usr/local/bin/toolbox.sh
/etc

%changelog
* {{{.changelog_timestamp}}} - {{{ $version }}}-1
- Added Oracle specific files for {{{ $version }}}-1
