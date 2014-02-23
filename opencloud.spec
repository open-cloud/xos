Summary: OpenCloud core services
Name: opencloud
Version: 1.0
Release: 1
License: GPL+
Group: Development/Tools
Source0: %{_tmppath}/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
requires: postgresql
requires: postgresql-server
requires: python-psycopg2
requires: graphviz
requires: graphviz-devel
requires: graphviz-python
requires: libxslt-devel
requires: python-pip
requires: tar
requires: gcc

%description
%{summary}

%prep
%setup -q

%build
# Empty section.

%pre
pip-python install django==1.5
pip-python install djangorestframework
pip-python install markdown  # Markdown support for the browseable API.
pip-python install pyyaml    # YAML content-type support.
pip-python install django-filter  # Filtering support
pip-python install lxml  # XML manipulation library
pip-python install netaddr # IP Addr library
pip-python install pytz
pip-python install django-timezones
pip-python install requests
pip-python install django-crispy-forms
pip-python install django-geoposition
pip-python install django-extensions
pip-python install django-suit
pip-python install django-evolution

easy_install django_evolution

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
install -d %{buildroot}/opt/planetstack

# in builddir
cp -rp /opt/plstackapi/planetstack %{buildroot}/opt/.

find %{buildroot}/opt/planetstack -type f -print | sed "s@^$RPM_BUILD_ROOT@@g"  > %{_tmppath}/tmp-filelist

%clean
rm -rf %{buildroot}

%files -f %{_tmppath}/tmp-filelist
%defattr(-,root,root,-)

%post
/opt/planetstack/scripts/opencloud initdb

%preun
rm -rf /opt/planetstack

%changelog
* Sat Feb 22 2014  Siobhan Tully  1.0.0
- First Build

