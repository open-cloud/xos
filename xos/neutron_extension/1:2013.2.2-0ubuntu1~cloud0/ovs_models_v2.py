# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Nicira Networks, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
# @author: Aaron Rosen, Nicira Networks, Inc.
# @author: Bob Kukura, Red Hat, Inc.


from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, PickleType
from sqlalchemy.schema import UniqueConstraint

from neutron.db.models_v2 import model_base


class VlanAllocation(model_base.BASEV2):
    """Represents allocation state of vlan_id on physical network."""
    __tablename__ = 'ovs_vlan_allocations'

    physical_network = Column(String(64), nullable=False, primary_key=True)
    vlan_id = Column(Integer, nullable=False, primary_key=True,
                     autoincrement=False)
    allocated = Column(Boolean, nullable=False)

    def __init__(self, physical_network, vlan_id):
        self.physical_network = physical_network
        self.vlan_id = vlan_id
        self.allocated = False

    def __repr__(self):
        return "<VlanAllocation(%s,%d,%s)>" % (self.physical_network,
                                               self.vlan_id, self.allocated)


class TunnelAllocation(model_base.BASEV2):
    """Represents allocation state of tunnel_id."""
    __tablename__ = 'ovs_tunnel_allocations'

    tunnel_id = Column(Integer, nullable=False, primary_key=True,
                       autoincrement=False)
    allocated = Column(Boolean, nullable=False)

    def __init__(self, tunnel_id):
        self.tunnel_id = tunnel_id
        self.allocated = False

    def __repr__(self):
        return "<TunnelAllocation(%d,%s)>" % (self.tunnel_id, self.allocated)


class NetworkBinding(model_base.BASEV2):
    """Represents binding of virtual network to physical realization."""
    __tablename__ = 'ovs_network_bindings'

    network_id = Column(String(36),
                        ForeignKey('networks.id', ondelete="CASCADE"),
                        primary_key=True)
    # 'gre', 'vlan', 'flat', 'local'
    network_type = Column(String(32), nullable=False)
    physical_network = Column(String(64))
    segmentation_id = Column(Integer)  # tunnel_id or vlan_id

    def __init__(self, network_id, network_type, physical_network,
                 segmentation_id):
        self.network_id = network_id
        self.network_type = network_type
        self.physical_network = physical_network
        self.segmentation_id = segmentation_id

    def __repr__(self):
        return "<NetworkBinding(%s,%s,%s,%d)>" % (self.network_id,
                                                  self.network_type,
                                                  self.physical_network,
                                                  self.segmentation_id)

class PortForwarding(model_base.BASEV2):
    """Ports to be forwarded through NAT """
    __tablename__ = 'ovs_port_forwarding'

    port_id = Column(String(36),
                     ForeignKey('ports.id', ondelete="CASCADE"),
                     primary_key=True)
    forward_ports = Column(PickleType)

    def __init__(self, port_id, forward_ports):
        self.port_id = port_id
        self.forward_ports = forward_ports

    def __repr__(self):
        return "<PortForwarding(%s,%s)>" % (self.port_id, self.forward_ports)

class TunnelEndpoint(model_base.BASEV2):
    """Represents tunnel endpoint in RPC mode."""
    __tablename__ = 'ovs_tunnel_endpoints'
    __table_args__ = (
        UniqueConstraint('id', name='uniq_ovs_tunnel_endpoints0id'),
    )

    ip_address = Column(String(64), primary_key=True)
    id = Column(Integer, nullable=False)

    def __init__(self, ip_address, id):
        self.ip_address = ip_address
        self.id = id

    def __repr__(self):
        return "<TunnelEndpoint(%s,%s)>" % (self.ip_address, self.id)

