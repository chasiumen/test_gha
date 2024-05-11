%define installbase /etc/
%define owner_user prometheus
%define owner_group prometheus
%define project %{_builddir}/%{name}-%{version}

Name: %{name}
Version: %{version}
Release: 1
Summary: Prometheus event monitoring and alerting server
Group: prometheus
License: GPLv3
URL: https://github.com/prometheus/prometheus
BuildArch: %{_arch}
AutoReqProv: no

%description
Prometheus, a Cloud Native Computing Foundation project, is a systems and 
service monitoring system. It collects metrics from configured targets 
at given intervals, evaluates rule expressions, displays the results, 
and can trigger alerts when specified conditions are observed.


%prep
exit 0

%pre
if ! grep -q %{name} /etc/passwd; then
    groupadd -r %{name}
    useradd -r -M -N --shell /sbin/nologin -d %{installbase}/%{name} -g %{name} -c "Prometheus monitoring server" %{name}
    echo "Added service user: prometheus"
fi


%build
mkdir -p %{project}/{/etc/prometheus/,/var/lib/prometheus,/usr/local/bin/,%{installbase}/%{name}}
curl -s -L --output %{_sourcedir}/prometheus-latest.linux-amd64.tar.gz "https://github.com/prometheus/prometheus/releases/download/v%{version}/prometheus-%{version}.linux-amd64.tar.gz"
cd %{_sourcedir}/
tar zxvf %{_sourcedir}/prometheus-latest.linux-amd64.tar.gz
ls -altr ./
cd %{_sourcedir}/prometheus-%{version}.linux-amd64/
cp ./prometheus         %{project}/usr/local/bin/
cp ./promtool           %{project}/usr/local/bin/
cp ./prometheus.yml     %{project}/etc/prometheus/prometheus-default.yml
cp -r console*          %{project}/etc/prometheus/


%clean
exit 0

%install
cp -a %{project}/* %{buildroot}
exit 0

%files
%defattr(-,%{owner_user},%{owner_group})
%{installbase}/%{name}
/etc/prometheus/*
/usr/local/bin/*
/var/lib/prometheus
/etc/prometheus/prometheus-default.yml

%post
if [ ! -f /etc/systemd/system/prometheus.service ]; then
    echo "Creating unit file..."
    # Unit file
    /bin/cat > /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus Time Series Collection and Processing Server
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --storage.tsdb.retention.time=365d \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9999 \

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
echo "Installed on %{installbase}%{name}"

%postun
/bin/rm -rf %{installbase}/%{name}
/bin/rm -f /etc/systemd/system/prometheus.service
systemctl daemon-reload
echo "To completly delete: userdel -r prometheus"
