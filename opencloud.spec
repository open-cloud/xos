Summary: OpenCloud core services
Name: opencloud
Version: 1.0.28
Release: 2
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
requires: python-httplib2
requires: GeoIP
requires: wget

%description
%{summary}

%prep
%setup -q

%build
# Empty section.

%pre
pip-python install django==1.7
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
pip-python install django-bitfield
pip-python install django-ipware
pip-python install django-encrypted-fields
pip-python install python-keyczar
pip-python install python-keystoneclient
pip-python install python-novaclient
pip-python install python-neutronclient 
pip-python install python-glanceclient


easy_install django_evolution
easy_install python_gflags
easy_install google_api_python_client

if [ ! -f /usr/lib/python2.7/site-packages/suit/static/suit/js/jquery-1.9.1.min.js ]; then
    wget -P /usr/lib/python2.7/site-packages/suit/static/suit/js http://code.jquery.com/jquery-1.9.1.min.js
fi

if [ ! -f /usr/share/GeoIP/GeoLiteCity.dat ]; then
   rm -f /usr/share/GeoIP/GeoLiteCity.*
   wget -P /usr/share/GeoIP http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
   gzip -d /usr/share/GeoIP/GeoLiteCity*.gz
fi

if [ "$1" == 2 ] ; then
    if [[ -e /opt/planetstack/scripts/opencloud ]]; then
        echo "UPGRADE - saving current state"
        /opt/planetstack/scripts/opencloud dumpdata
    fi
fi

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
install -d %{buildroot}/opt/planetstack
install -d %{buildroot}/etc/init.d

# in builddir


# don't copy symbolic links (they are handled in %post)
rsync -rptgoD ./planetstack %{buildroot}/opt/.  
cp observer-initscript %{buildroot}/etc/init.d/plstackobserver

find %{buildroot}/opt/planetstack -type f -print | sed "s@^$RPM_BUILD_ROOT@@g" > %{_tmppath}/tmp-filelist
echo /etc/init.d/plstackobserver >> %{_tmppath}/tmp-filelist

# remove config files from the file list (see %config below)
cat > %{_tmppath}/config-files << "EOF"
/opt/planetstack/plstackapi_config
/opt/planetstack/deployment_auth.py
EOF

sort %{_tmppath}/tmp-filelist > %{_tmppath}/tmp-filelist.sorted
sort %{_tmppath}/config-files > %{_tmppath}/config-files.sorted
comm -13 %{_tmppath}/config-files.sorted %{_tmppath}/tmp-filelist.sorted > %{_tmppath}/tmp-filelist

cp %{_tmppath}/tmp-filelist /tmp/tmp-filelist


%clean
rm -rf %{buildroot}

%files -f %{_tmppath}/tmp-filelist
%defattr(-,root,root,-)
%config /opt/planetstack/plstackapi_config
%config /opt/planetstack/deployment_auth.py
%config /opt/planetstack/model-deps

%post
ln -s ec2_observer /opt/planetstack/observer
ln -s config-opencloud.py /opt/planetstack/syndicate_observer/syndicatelib_config/config.py

if [ ! -e /opt/planetstack/public_keys ]; then
    cd /opt/planetstack
    scripts/opencloud genkeys
fi

if [ "$1" == 1 ] ; then
    echo "NEW INSTALL - initializing database"
    /opt/planetstack/scripts/opencloud initdb
else
    # scripts/opencloud will choose evolve or migrate depending on django version
    echo "UPGRADE - doing evolution/migration"
    /opt/planetstack/scripts/opencloud evolvedb
fi

# Clone ansible with latest openstack modules
git clone --recursive git://github.com/ansible/ansible.git /opt/ansible
mkdir -p /etc/ansible
echo > /etc/ansible/hosts << "EOF"
[localhost]
127.0.0.1
EOF


# start the server
/opt/planetstack/scripts/opencloud runserver

%preun
if [ "$1" = 0 ] ; then
    echo "UNINSTALL - destroying planetstack"
    rm -rf /opt/planetstack
fi

%changelog
* Sat Feb 22 2014  Siobhan Tully  1.0.0
- First Build

