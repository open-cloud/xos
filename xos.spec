Summary: OpenCloud core services
Name: xos
Version: 1.2.0
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
pip-python install djangorestframework==2.4.4
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
pip-python install python-ceilometerclient
pip-python install django_rest_swagger


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
    if [[ -e /opt/xos/scripts/opencloud ]]; then
        echo "UPGRADE - saving current state"
        /opt/xos/scripts/opencloud dumpdata
    fi
fi

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
install -d %{buildroot}/opt/xos
install -d %{buildroot}/etc/init.d

# in builddir

rm -rf %{buildroot}/opt/xos
# don't copy symbolic links (they are handled in %post)
rsync -rptgoD ./planetstack %{buildroot}/opt/.  
# XXX temporary - rename /opt/planetstack to /opt/xos
mv %{buildroot}/opt/planetstack %{buildroot}/opt/xos
cp observer-initscript %{buildroot}/etc/init.d/plstackobserver

find %{buildroot}/opt/xos -type f -print | sed "s@^$RPM_BUILD_ROOT@@g" > %{_tmppath}/tmp-filelist
echo /etc/init.d/plstackobserver >> %{_tmppath}/tmp-filelist

# remove config files from the file list (see %config below)
cat > %{_tmppath}/config-files << "EOF"
/opt/xos/xos_config
/opt/xos/deployment_auth.py
EOF

sort %{_tmppath}/tmp-filelist > %{_tmppath}/tmp-filelist.sorted
sort %{_tmppath}/config-files > %{_tmppath}/config-files.sorted
comm -13 %{_tmppath}/config-files.sorted %{_tmppath}/tmp-filelist.sorted > %{_tmppath}/tmp-filelist

cp %{_tmppath}/tmp-filelist /tmp/tmp-filelist


%clean
rm -rf %{buildroot}

%files -f %{_tmppath}/tmp-filelist
%defattr(-,root,root,-)
%config /opt/xos/xos_config
%config /opt/xos/deployment_auth.py
%config /opt/xos/model-deps

%post
ln -s openstack_observer /opt/xos/observer
#ln -s config-opencloud.py /opt/xos/syndicate_observer/syndicatelib_config/config.py

if [ ! -e /opt/xos/public_keys ]; then
    cd /opt/xos
    scripts/opencloud genkeys
fi

if [ "$1" == 1 ] ; then
    echo "NEW INSTALL - initializing database"
    /opt/xos/scripts/opencloud initdb
else
    # scripts/opencloud will choose evolve or migrate depending on django version
    echo "UPGRADE - doing evolution/migration"
    /opt/xos/scripts/opencloud evolvedb
fi

# Clone ansible with latest openstack modules
git clone --recursive git://github.com/ansible/ansible.git /opt/ansible
mkdir -p /etc/ansible
echo > /etc/ansible/hosts << "EOF"
[localhost]
127.0.0.1
EOF


# start the server
/opt/xos/scripts/opencloud runserver

%preun
if [ "$1" = 0 ] ; then
    echo "UNINSTALL - destroying xos"
    rm -rf /opt/xos
fi

%changelog
* Sat Feb 22 2014  Siobhan Tully  1.0.0
- First Build

