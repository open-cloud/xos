FROM       xosproject/xos-synchronizer-openstack

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    openvpn

# for OpenVPN
RUN mkdir -p /opt/openvpn
RUN chmod 777 /opt/openvpn
RUN git clone https://github.com/OpenVPN/easy-rsa.git /opt/openvpn
RUN git -C /opt/openvpn pull origin master
RUN echo 'set_var EASYRSA	"/opt/openvpn/easyrsa3"' | tee /opt/openvpn/vars
RUN echo 'set_var EASYRSA_BATCH	"true"' | tee -a /opt/openvpn/vars
