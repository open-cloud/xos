# Converted with pg2mysql-1.9
# Converted on Fri, 16 Oct 2015 05:12:46 -0400
# Lightbox Technologies Inc. http://www.lightbox.ca

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone="+00:00";

CREATE TABLE auth_group (
    id int(11) NOT NULL,
    name varchar(80) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_group_permissions (
    id int(11) NOT NULL,
    group_id int(11) NOT NULL,
    permission_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_permission (
    id int(11) NOT NULL,
    name varchar(50) NOT NULL,
    content_type_id int(11) NOT NULL,
    codename varchar(100) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_account (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_charge (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    kind varchar(30) NOT NULL,
    state varchar(30) NOT NULL,
    date timestamp NOT NULL,
    amount double precision NOT NULL,
    `coreHours` double precision NOT NULL,
    account_id int(11) NOT NULL,
    invoice_id int(11),
    object_id int(11) NOT NULL,
    slice_id int(11)
) ENGINE=MyISAM;

CREATE TABLE core_controller (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL,
    backend_type varchar(200) NOT NULL,
    version varchar(200) NOT NULL,
    auth_url varchar(200),
    admin_user varchar(200),
    admin_password varchar(200),
    admin_tenant varchar(200),
    domain varchar(200),
    deployment_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllercredential (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    key_id text NOT NULL,
    enc_value text NOT NULL,
    controller_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllerdashboardview (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    enabled bool NOT NULL,
    url text NOT NULL,
    controller_id int(11) NOT NULL,
    `dashboardView_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllerimages (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    glance_image_id varchar(200),
    controller_id int(11) NOT NULL,
    image_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllernetwork (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    net_id text,
    router_id text,
    subnet_id text,
    subnet varchar(32) NOT NULL,
    controller_id int(11) NOT NULL,
    network_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllerrole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllersite (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    tenant_id varchar(200),
    controller_id int(11),
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllersiteprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id varchar(200),
    controller_id int(11) NOT NULL,
    site_privilege_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllerslice (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    tenant_id varchar(200),
    controller_id int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controllersliceprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id varchar(200),
    controller_id int(11) NOT NULL,
    slice_privilege_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_controlleruser (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    kuser_id varchar(200),
    controller_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_dashboardview (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL,
    url text NOT NULL,
    enabled bool NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_dashboardview_deployments (
    id int(11) NOT NULL,
    dashboardview_id int(11) NOT NULL,
    deployment_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_deployment (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL,
    `accessControl` text NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_deploymentprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    deployment_id int(11) NOT NULL,
    role_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_deploymentrole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_flavor (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    description text,
    flavor varchar(32) NOT NULL,
    `order` int(11) NOT NULL,
    `default` bool NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_flavor_deployments (
    id int(11) NOT NULL,
    flavor_id int(11) NOT NULL,
    deployment_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_image (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name text NOT NULL,
    disk_format text NOT NULL,
    container_format text NOT NULL,
    path text
) ENGINE=MyISAM;

CREATE TABLE core_imagedeployments (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    deployment_id int(11) NOT NULL,
    image_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_instance (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    instance_id varchar(200),
    instance_uuid varchar(200),
    name varchar(200) NOT NULL,
    instance_name varchar(200),
    ip varchar(43),
    numberCores int(11) NOT NULL,
    userData text,
    creator_id int(11),
    deployment_id int(11) NOT NULL,
    flavor_id int(11) NOT NULL,
    image_id int(11) NOT NULL,
    node_id int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_invoice (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    date timestamp NOT NULL,
    account_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_network (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    subnet varchar(32) NOT NULL,
    ports text,
    labels text,
    guaranteed_bandwidth int(11) NOT NULL,
    permit_all_slices bool NOT NULL,
    topology_parameters text,
    controller_url text,
    controller_parameters text,
    network_id text,
    router_id text,
    subnet_id text,
    autoconnect bool NOT NULL,
    owner_id int(11) NOT NULL,
    template_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_network_permitted_slices (
    id int(11) NOT NULL,
    network_id int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_networkparameter (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    value text NOT NULL,
    object_id int(11) NOT NULL,
    content_type_id int(11) NOT NULL,
    parameter_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_networkparametertype (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    description text NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_networkslice (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    network_id int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_networktemplate (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    description text,
    guaranteed_bandwidth int(11) NOT NULL,
    visibility varchar(30) NOT NULL,
    translation varchar(30) NOT NULL,
    shared_network_name varchar(30),
    shared_network_id text,
    topology_kind varchar(30) NOT NULL,
    controller_kind varchar(30)
) ENGINE=MyISAM;

CREATE TABLE core_node (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL,
    site_id int(11),
    site_deployment_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_payment (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    amount double precision NOT NULL,
    date timestamp NOT NULL,
    account_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_port (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    ip varchar(43),
    port_id text,
    mac text,
    instance_id int(11),
    network_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_program (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(30) NOT NULL,
    description text,
    kind varchar(30) NOT NULL,
    command varchar(30),
    contents text,
    output text,
    messages text,
    `status` text,
    owner_id int(11)
) ENGINE=MyISAM;

CREATE TABLE core_project (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_reservation (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    `startTime` timestamp NOT NULL,
    duration int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_reservedresource (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    quantity int(11) NOT NULL,
    instance_id int(11) NOT NULL,
    `reservationSet_id` int(11) NOT NULL,
    resource_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_role (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_type varchar(80) NOT NULL,
    role varchar(80),
    description varchar(120) NOT NULL,
    content_type_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_router (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    owner_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_router_networks (
    id int(11) NOT NULL,
    router_id int(11) NOT NULL,
    network_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE `core_router_permittedNetworks` (
    id int(11) NOT NULL,
    router_id int(11) NOT NULL,
    network_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_service (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    description text,
    enabled bool NOT NULL,
    kind varchar(30) NOT NULL,
    name varchar(30) NOT NULL,
    `versionNumber` varchar(30) NOT NULL,
    published bool NOT NULL,
    view_url text,
    icon_url text,
    public_key text,
    service_specific_id varchar(30),
    service_specific_attribute text
) ENGINE=MyISAM;

CREATE TABLE core_serviceattribute (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    value text NOT NULL,
    service_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_serviceclass (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    description varchar(255) NOT NULL,
    commitment int(11) NOT NULL,
    `membershipFee` int(11) NOT NULL,
    `membershipFeeMonths` int(11) NOT NULL,
    `upgradeRequiresApproval` bool NOT NULL
) ENGINE=MyISAM;

CREATE TABLE `core_serviceclass_upgradeFrom` (
    id int(11) NOT NULL,
    from_serviceclass_id int(11) NOT NULL,
    to_serviceclass_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_serviceprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id int(11) NOT NULL,
    service_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_serviceresource (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(32) NOT NULL,
    `maxUnitsDeployment` int(11) NOT NULL,
    `maxUnitsNode` int(11) NOT NULL,
    `maxDuration` int(11) NOT NULL,
    `bucketInRate` int(11) NOT NULL,
    `bucketMaxSize` int(11) NOT NULL,
    cost int(11) NOT NULL,
    `calendarReservable` bool NOT NULL,
    `serviceClass_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_servicerole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_site (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(200) NOT NULL,
    site_url text,
    enabled bool NOT NULL,
    hosts_nodes bool NOT NULL,
    hosts_users bool NOT NULL,
    location varchar(42) NOT NULL,
    longitude double precision,
    latitude double precision,
    login_base varchar(50) NOT NULL,
    is_public bool NOT NULL,
    abbreviated_name varchar(80) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_sitecredential (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    key_id text NOT NULL,
    enc_value text NOT NULL,
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_sitedeployment (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    availability_zone varchar(200),
    controller_id int(11),
    deployment_id int(11) NOT NULL,
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_siteprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id int(11) NOT NULL,
    site_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_siterole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_slice (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(80) NOT NULL,
    enabled bool NOT NULL,
    omf_friendly bool NOT NULL,
    description text NOT NULL,
    slice_url text NOT NULL,
    max_instances int(11) NOT NULL,
    network text,
    mount_data_sets text,
    creator_id int(11),
    default_flavor_id int(11),
    default_image_id int(11),
    service_id int(11),
    `serviceClass_id` int(11),
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_slicecredential (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    key_id text NOT NULL,
    enc_value text NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_sliceprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id int(11) NOT NULL,
    slice_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_slicerole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_slicetag (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(30) NOT NULL,
    value text NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_tag (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    value text NOT NULL,
    object_id int(11) NOT NULL,
    content_type_id int(11) NOT NULL,
    service_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_tenant (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    kind varchar(30) NOT NULL,
    service_specific_id varchar(30),
    service_specific_attribute text,
    connect_method varchar(30) NOT NULL,
    provider_service_id int(11) NOT NULL,
    subscriber_root_id int(11),
    subscriber_service_id int(11),
    subscriber_tenant_id int(11),
    subscriber_user_id int(11)
) ENGINE=MyISAM;

CREATE TABLE core_tenantroot (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    kind varchar(30) NOT NULL,
    name varchar(255),
    service_specific_attribute text,
    service_specific_id varchar(30)
) ENGINE=MyISAM;

CREATE TABLE core_tenantrootprivilege (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role_id int(11) NOT NULL,
    tenant_root_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_tenantrootrole (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    role varchar(30) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_usableobject (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name text NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_user (
    id int(11) NOT NULL,
    password varchar(128) NOT NULL,
    last_login timestamp NOT NULL,
    email varchar(255) NOT NULL,
    username varchar(255) NOT NULL,
    firstname varchar(200) NOT NULL,
    lastname varchar(200) NOT NULL,
    phone varchar(100),
    user_url varchar(200),
    public_key text,
    is_active bool NOT NULL,
    is_admin bool NOT NULL,
    is_staff bool NOT NULL,
    is_readonly bool NOT NULL,
    is_registering bool NOT NULL,
    is_appuser bool NOT NULL,
    login_page varchar(200),
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    timezone varchar(100) NOT NULL,
    site_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_usercredential (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(128) NOT NULL,
    key_id text NOT NULL,
    enc_value text NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE core_userdashboardview (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    `order` int(11) NOT NULL,
    `dashboardView_id` int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_admin_log (
    id int(11) NOT NULL,
    action_time timestamp NOT NULL,
    object_id text,
    object_repr varchar(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id int(11),
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_content_type (
    id int(11) NOT NULL,
    name varchar(100) NOT NULL,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_migrations (
    id int(11) NOT NULL,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied timestamp NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_session (
    session_key varchar(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_accessmap (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(64) NOT NULL,
    description text,
    map varchar(100) NOT NULL,
    `contentProvider_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_cdnprefix (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    cdn_prefix_id int(11),
    prefix varchar(200) NOT NULL,
    description text,
    enabled bool NOT NULL,
    `contentProvider_id` int(11) NOT NULL,
    `defaultOriginServer_id` int(11)
) ENGINE=MyISAM;

CREATE TABLE hpc_contentprovider (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    content_provider_id int(11),
    name varchar(254) NOT NULL,
    enabled bool NOT NULL,
    description text,
    `serviceProvider_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_contentprovider_users (
    id int(11) NOT NULL,
    contentprovider_id int(11) NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_hpchealthcheck (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    kind varchar(30) NOT NULL,
    resource_name text NOT NULL,
    result_contains text,
    result_min_size int(11),
    result_max_size int(11),
    `hpcService_id` int(11)
) ENGINE=MyISAM;

CREATE TABLE hpc_hpcservice (
    service_ptr_id int(11) NOT NULL,
    cmi_hostname varchar(254),
    hpc_port80 bool NOT NULL,
    watcher_hpc_network varchar(254),
    watcher_dnsdemux_network varchar(254),
    watcher_dnsredir_network varchar(254)
) ENGINE=MyISAM;

CREATE TABLE hpc_originserver (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    origin_server_id int(11),
    url text NOT NULL,
    authenticated bool NOT NULL,
    enabled bool NOT NULL,
    protocol varchar(12) NOT NULL,
    redirects bool NOT NULL,
    description text,
    `contentProvider_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_serviceprovider (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    service_provider_id int(11),
    name varchar(254) NOT NULL,
    description text,
    enabled bool NOT NULL,
    `hpcService_id` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hpc_sitemap (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(64) NOT NULL,
    description text,
    map varchar(100) NOT NULL,
    map_id int(11),
    `cdnPrefix_id` int(11),
    `contentProvider_id` int(11),
    `hpcService_id` int(11),
    `serviceProvider_id` int(11)
) ENGINE=MyISAM;

CREATE TABLE requestrouter_requestrouterservice (
    service_ptr_id int(11) NOT NULL,
    `behindNat` bool NOT NULL,
    `defaultTTL` int(11) NOT NULL,
    `defaultAction` varchar(30) NOT NULL,
    `lastResortAction` varchar(30) NOT NULL,
    `maxAnswers` int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE requestrouter_servicemap (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(50) NOT NULL,
    prefix text NOT NULL,
    `siteMap` varchar(100) NOT NULL,
    `accessMap` varchar(100) NOT NULL,
    owner_id int(11) NOT NULL,
    slice_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_slicesecret (
    id int(11) NOT NULL,
    secret text NOT NULL,
    slice_id_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_syndicateprincipal (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    principal_id text NOT NULL,
    public_key_pem text NOT NULL,
    sealed_private_key text NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_syndicateservice (
    service_ptr_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_volume (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    name varchar(64) NOT NULL,
    description text,
    blocksize int(11) NOT NULL,
    private bool NOT NULL,
    archive bool NOT NULL,
    cap_read_data bool NOT NULL,
    cap_write_data bool NOT NULL,
    cap_host_data bool NOT NULL,
    owner_id_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_volumeaccessright (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    cap_read_data bool NOT NULL,
    cap_write_data bool NOT NULL,
    cap_host_data bool NOT NULL,
    owner_id_id int(11) NOT NULL,
    volume_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE syndicate_storage_volumeslice (
    id int(11) NOT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,
    enacted timestamp,
    policed timestamp,
    backend_register varchar(140),
    backend_status text NOT NULL,
    deleted bool NOT NULL,
    write_protect bool NOT NULL,
    lazy_blocked bool NOT NULL,
    no_sync bool NOT NULL,
    cap_read_data bool NOT NULL,
    cap_write_data bool NOT NULL,
    cap_host_data bool NOT NULL,
    `UG_portnum` int(11) NOT NULL,
    `RG_portnum` int(11) NOT NULL,
    credentials_blob text,
    slice_id_id int(11) NOT NULL,
    volume_id_id int(11) NOT NULL
) ENGINE=MyISAM;

ALTER TABLE auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
ALTER TABLE auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
ALTER TABLE auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
ALTER TABLE core_account
    ADD CONSTRAINT core_account_pkey PRIMARY KEY (id);
ALTER TABLE core_charge
    ADD CONSTRAINT core_charge_pkey PRIMARY KEY (id);
ALTER TABLE core_controller
    ADD CONSTRAINT core_controller_pkey PRIMARY KEY (id);
ALTER TABLE core_controllercredential
    ADD CONSTRAINT core_controllercredential_pkey PRIMARY KEY (id);
ALTER TABLE core_controllerdashboardview
    ADD CONSTRAINT core_controllerdashboardview_pkey PRIMARY KEY (id);
ALTER TABLE core_controllerimages
    ADD CONSTRAINT core_controllerimages_pkey PRIMARY KEY (id);
ALTER TABLE core_controllernetwork
    ADD CONSTRAINT core_controllernetwork_pkey PRIMARY KEY (id);
ALTER TABLE core_controllerrole
    ADD CONSTRAINT core_controllerrole_pkey PRIMARY KEY (id);
ALTER TABLE core_controllersite
    ADD CONSTRAINT core_controllersite_pkey PRIMARY KEY (id);
ALTER TABLE core_controllersiteprivilege
    ADD CONSTRAINT core_controllersiteprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_controllerslice
    ADD CONSTRAINT core_controllerslice_pkey PRIMARY KEY (id);
ALTER TABLE core_controllersliceprivilege
    ADD CONSTRAINT core_controllersliceprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_controlleruser
    ADD CONSTRAINT core_controlleruser_pkey PRIMARY KEY (id);
ALTER TABLE core_dashboardview_deployments
    ADD CONSTRAINT core_dashboardview_deployments_pkey PRIMARY KEY (id);
ALTER TABLE core_dashboardview
    ADD CONSTRAINT core_dashboardview_pkey PRIMARY KEY (id);
ALTER TABLE core_deployment
    ADD CONSTRAINT core_deployment_pkey PRIMARY KEY (id);
ALTER TABLE core_deploymentprivilege
    ADD CONSTRAINT core_deploymentprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_deploymentrole
    ADD CONSTRAINT core_deploymentrole_pkey PRIMARY KEY (id);
ALTER TABLE core_flavor_deployments
    ADD CONSTRAINT core_flavor_deployments_pkey PRIMARY KEY (id);
ALTER TABLE core_flavor
    ADD CONSTRAINT core_flavor_pkey PRIMARY KEY (id);
ALTER TABLE core_image
    ADD CONSTRAINT core_image_pkey PRIMARY KEY (id);
ALTER TABLE core_imagedeployments
    ADD CONSTRAINT core_imagedeployments_pkey PRIMARY KEY (id);
ALTER TABLE core_instance
    ADD CONSTRAINT core_instance_pkey PRIMARY KEY (id);
ALTER TABLE core_invoice
    ADD CONSTRAINT core_invoice_pkey PRIMARY KEY (id);
ALTER TABLE core_network_permitted_slices
    ADD CONSTRAINT core_network_permitted_slices_pkey PRIMARY KEY (id);
ALTER TABLE core_network
    ADD CONSTRAINT core_network_pkey PRIMARY KEY (id);
ALTER TABLE core_networkparameter
    ADD CONSTRAINT core_networkparameter_pkey PRIMARY KEY (id);
ALTER TABLE core_networkparametertype
    ADD CONSTRAINT core_networkparametertype_pkey PRIMARY KEY (id);
ALTER TABLE core_networkslice
    ADD CONSTRAINT core_networkslice_pkey PRIMARY KEY (id);
ALTER TABLE core_networktemplate
    ADD CONSTRAINT core_networktemplate_pkey PRIMARY KEY (id);
ALTER TABLE core_node
    ADD CONSTRAINT core_node_pkey PRIMARY KEY (id);
ALTER TABLE core_payment
    ADD CONSTRAINT core_payment_pkey PRIMARY KEY (id);
ALTER TABLE core_port
    ADD CONSTRAINT core_port_pkey PRIMARY KEY (id);
ALTER TABLE core_program
    ADD CONSTRAINT core_program_pkey PRIMARY KEY (id);
ALTER TABLE core_project
    ADD CONSTRAINT core_project_pkey PRIMARY KEY (id);
ALTER TABLE core_reservation
    ADD CONSTRAINT core_reservation_pkey PRIMARY KEY (id);
ALTER TABLE core_reservedresource
    ADD CONSTRAINT core_reservedresource_pkey PRIMARY KEY (id);
ALTER TABLE core_role
    ADD CONSTRAINT core_role_pkey PRIMARY KEY (id);
ALTER TABLE core_router_networks
    ADD CONSTRAINT core_router_networks_pkey PRIMARY KEY (id);
ALTER TABLE `core_router_permittedNetworks`
    ADD CONSTRAINT core_router_permittedNetworks_pkey PRIMARY KEY (id);
ALTER TABLE core_router
    ADD CONSTRAINT core_router_pkey PRIMARY KEY (id);
ALTER TABLE core_service
    ADD CONSTRAINT core_service_pkey PRIMARY KEY (id);
ALTER TABLE core_serviceattribute
    ADD CONSTRAINT core_serviceattribute_pkey PRIMARY KEY (id);
ALTER TABLE core_serviceclass
    ADD CONSTRAINT core_serviceclass_pkey PRIMARY KEY (id);
ALTER TABLE `core_serviceclass_upgradeFrom`
    ADD CONSTRAINT core_serviceclass_upgradeFrom_pkey PRIMARY KEY (id);
ALTER TABLE core_serviceprivilege
    ADD CONSTRAINT core_serviceprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_serviceresource
    ADD CONSTRAINT core_serviceresource_pkey PRIMARY KEY (id);
ALTER TABLE core_servicerole
    ADD CONSTRAINT core_servicerole_pkey PRIMARY KEY (id);
ALTER TABLE core_site
    ADD CONSTRAINT core_site_pkey PRIMARY KEY (id);
ALTER TABLE core_sitecredential
    ADD CONSTRAINT core_sitecredential_pkey PRIMARY KEY (id);
ALTER TABLE core_sitedeployment
    ADD CONSTRAINT core_sitedeployment_pkey PRIMARY KEY (id);
ALTER TABLE core_siteprivilege
    ADD CONSTRAINT core_siteprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_siterole
    ADD CONSTRAINT core_siterole_pkey PRIMARY KEY (id);
ALTER TABLE core_slice
    ADD CONSTRAINT core_slice_pkey PRIMARY KEY (id);
ALTER TABLE core_slicecredential
    ADD CONSTRAINT core_slicecredential_pkey PRIMARY KEY (id);
ALTER TABLE core_sliceprivilege
    ADD CONSTRAINT core_sliceprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_slicerole
    ADD CONSTRAINT core_slicerole_pkey PRIMARY KEY (id);
ALTER TABLE core_slicetag
    ADD CONSTRAINT core_slicetag_pkey PRIMARY KEY (id);
ALTER TABLE core_tag
    ADD CONSTRAINT core_tag_pkey PRIMARY KEY (id);
ALTER TABLE core_tenant
    ADD CONSTRAINT core_tenant_pkey PRIMARY KEY (id);
ALTER TABLE core_tenantroot
    ADD CONSTRAINT core_tenantroot_pkey PRIMARY KEY (id);
ALTER TABLE core_tenantrootprivilege
    ADD CONSTRAINT core_tenantrootprivilege_pkey PRIMARY KEY (id);
ALTER TABLE core_tenantrootrole
    ADD CONSTRAINT core_tenantrootrole_pkey PRIMARY KEY (id);
ALTER TABLE core_usableobject
    ADD CONSTRAINT core_usableobject_pkey PRIMARY KEY (id);
ALTER TABLE core_user
    ADD CONSTRAINT core_user_pkey PRIMARY KEY (id);
ALTER TABLE core_usercredential
    ADD CONSTRAINT core_usercredential_pkey PRIMARY KEY (id);
ALTER TABLE core_userdashboardview
    ADD CONSTRAINT core_userdashboardview_pkey PRIMARY KEY (id);
ALTER TABLE django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
ALTER TABLE django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
ALTER TABLE django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
ALTER TABLE django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
ALTER TABLE hpc_accessmap
    ADD CONSTRAINT hpc_accessmap_pkey PRIMARY KEY (id);
ALTER TABLE hpc_cdnprefix
    ADD CONSTRAINT hpc_cdnprefix_pkey PRIMARY KEY (id);
ALTER TABLE hpc_contentprovider
    ADD CONSTRAINT hpc_contentprovider_pkey PRIMARY KEY (id);
ALTER TABLE hpc_contentprovider_users
    ADD CONSTRAINT hpc_contentprovider_users_pkey PRIMARY KEY (id);
ALTER TABLE hpc_hpchealthcheck
    ADD CONSTRAINT hpc_hpchealthcheck_pkey PRIMARY KEY (id);
ALTER TABLE hpc_hpcservice
    ADD CONSTRAINT hpc_hpcservice_pkey PRIMARY KEY (service_ptr_id);
ALTER TABLE hpc_originserver
    ADD CONSTRAINT hpc_originserver_pkey PRIMARY KEY (id);
ALTER TABLE hpc_serviceprovider
    ADD CONSTRAINT hpc_serviceprovider_pkey PRIMARY KEY (id);
ALTER TABLE hpc_sitemap
    ADD CONSTRAINT hpc_sitemap_pkey PRIMARY KEY (id);
ALTER TABLE requestrouter_requestrouterservice
    ADD CONSTRAINT requestrouter_requestrouterservice_pkey PRIMARY KEY (service_ptr_id);
ALTER TABLE requestrouter_servicemap
    ADD CONSTRAINT requestrouter_servicemap_pkey PRIMARY KEY (id);
ALTER TABLE syndicate_storage_slicesecret
    ADD CONSTRAINT syndicate_storage_slicesecret_pkey PRIMARY KEY (id);
ALTER TABLE syndicate_storage_syndicateprincipal
    ADD CONSTRAINT syndicate_storage_syndicateprincipal_pkey PRIMARY KEY (id);
ALTER TABLE syndicate_storage_syndicateservice
    ADD CONSTRAINT syndicate_storage_syndicateservice_pkey PRIMARY KEY (service_ptr_id);
ALTER TABLE syndicate_storage_volume
    ADD CONSTRAINT syndicate_storage_volume_pkey PRIMARY KEY (id);
ALTER TABLE syndicate_storage_volumeaccessright
    ADD CONSTRAINT syndicate_storage_volumeaccessright_pkey PRIMARY KEY (id);
ALTER TABLE syndicate_storage_volumeslice
    ADD CONSTRAINT syndicate_storage_volumeslice_pkey PRIMARY KEY (id);
ALTER TABLE `auth_group_permissions` ADD INDEX ( group_id ) ;
ALTER TABLE `auth_group_permissions` ADD INDEX ( permission_id ) ;
ALTER TABLE `auth_permission` ADD INDEX ( content_type_id ) ;
ALTER TABLE `core_account` ADD INDEX ( site_id ) ;
ALTER TABLE `core_charge` ADD INDEX ( account_id ) ;
ALTER TABLE `core_charge` ADD INDEX ( object_id ) ;
ALTER TABLE `core_charge` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_charge` ADD INDEX ( invoice_id ) ;
ALTER TABLE `core_controller` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_controllercredential` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllercredential` ADD INDEX ( name ) ;
ALTER TABLE `core_controllerdashboardview` ADD INDEX ( dashboardView_id ) ;
ALTER TABLE `core_controllerdashboardview` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllerimages` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllerimages` ADD INDEX ( image_id ) ;
ALTER TABLE `core_controllernetwork` ADD INDEX ( network_id ) ;
ALTER TABLE `core_controllernetwork` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllersite` ADD INDEX ( tenant_id ) ;
ALTER TABLE `core_controllersite` ADD INDEX ( site_id ) ;
ALTER TABLE `core_controllersite` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllersiteprivilege` ADD INDEX ( site_privilege_id ) ;
ALTER TABLE `core_controllersiteprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_controllersiteprivilege` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllerslice` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controllerslice` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_controllersliceprivilege` ADD INDEX ( slice_privilege_id ) ;
ALTER TABLE `core_controllersliceprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_controllersliceprivilege` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controlleruser` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_controlleruser` ADD INDEX ( user_id ) ;
ALTER TABLE `core_dashboardview_deployments` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_dashboardview_deployments` ADD INDEX ( dashboardview_id ) ;
ALTER TABLE `core_deploymentprivilege` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_deploymentprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_deploymentprivilege` ADD INDEX ( user_id ) ;
ALTER TABLE `core_flavor_deployments` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_flavor_deployments` ADD INDEX ( flavor_id ) ;
ALTER TABLE `core_imagedeployments` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_imagedeployments` ADD INDEX ( image_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( creator_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( node_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( flavor_id ) ;
ALTER TABLE `core_instance` ADD INDEX ( image_id ) ;
ALTER TABLE `core_invoice` ADD INDEX ( account_id ) ;
ALTER TABLE `core_network` ADD INDEX ( owner_id ) ;
ALTER TABLE `core_network` ADD INDEX ( template_id ) ;
ALTER TABLE `core_network_permitted_slices` ADD INDEX ( network_id ) ;
ALTER TABLE `core_network_permitted_slices` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_networkparameter` ADD INDEX ( content_type_id ) ;
ALTER TABLE `core_networkparameter` ADD INDEX ( parameter_id ) ;
ALTER TABLE `core_networkparametertype` ADD INDEX ( name ) ;
ALTER TABLE `core_networkslice` ADD INDEX ( network_id ) ;
ALTER TABLE `core_networkslice` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_node` ADD INDEX ( site_deployment_id ) ;
ALTER TABLE `core_node` ADD INDEX ( site_id ) ;
ALTER TABLE `core_payment` ADD INDEX ( account_id ) ;
ALTER TABLE `core_port` ADD INDEX ( network_id ) ;
ALTER TABLE `core_port` ADD INDEX ( instance_id ) ;
ALTER TABLE `core_program` ADD INDEX ( owner_id ) ;
ALTER TABLE `core_reservation` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_reservedresource` ADD INDEX ( instance_id ) ;
ALTER TABLE `core_reservedresource` ADD INDEX ( reservationSet_id ) ;
ALTER TABLE `core_reservedresource` ADD INDEX ( resource_id ) ;
ALTER TABLE `core_role` ADD INDEX ( content_type_id ) ;
ALTER TABLE `core_router` ADD INDEX ( owner_id ) ;
ALTER TABLE `core_router_networks` ADD INDEX ( network_id ) ;
ALTER TABLE `core_router_networks` ADD INDEX ( router_id ) ;
ALTER TABLE `core_router_permittedNetworks` ADD INDEX ( network_id ) ;
ALTER TABLE `core_router_permittedNetworks` ADD INDEX ( router_id ) ;
ALTER TABLE `core_serviceattribute` ADD INDEX ( name ) ;
ALTER TABLE `core_serviceattribute` ADD INDEX ( service_id ) ;
ALTER TABLE `core_serviceclass_upgradeFrom` ADD INDEX ( to_serviceclass_id ) ;
ALTER TABLE `core_serviceclass_upgradeFrom` ADD INDEX ( from_serviceclass_id ) ;
ALTER TABLE `core_serviceprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_serviceprivilege` ADD INDEX ( service_id ) ;
ALTER TABLE `core_serviceprivilege` ADD INDEX ( user_id ) ;
ALTER TABLE `core_serviceresource` ADD INDEX ( serviceClass_id ) ;
ALTER TABLE `core_sitecredential` ADD INDEX ( site_id ) ;
ALTER TABLE `core_sitecredential` ADD INDEX ( name ) ;
ALTER TABLE `core_sitedeployment` ADD INDEX ( deployment_id ) ;
ALTER TABLE `core_sitedeployment` ADD INDEX ( site_id ) ;
ALTER TABLE `core_sitedeployment` ADD INDEX ( controller_id ) ;
ALTER TABLE `core_siteprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_siteprivilege` ADD INDEX ( site_id ) ;
ALTER TABLE `core_siteprivilege` ADD INDEX ( user_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( creator_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( default_flavor_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( site_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( default_image_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( serviceClass_id ) ;
ALTER TABLE `core_slice` ADD INDEX ( service_id ) ;
ALTER TABLE `core_slicecredential` ADD INDEX ( name ) ;
ALTER TABLE `core_slicecredential` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_sliceprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_sliceprivilege` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_sliceprivilege` ADD INDEX ( user_id ) ;
ALTER TABLE `core_slicetag` ADD INDEX ( slice_id ) ;
ALTER TABLE `core_tag` ADD INDEX ( content_type_id ) ;
ALTER TABLE `core_tag` ADD INDEX ( name ) ;
ALTER TABLE `core_tag` ADD INDEX ( service_id ) ;
ALTER TABLE `core_tenant` ADD INDEX ( subscriber_tenant_id ) ;
ALTER TABLE `core_tenant` ADD INDEX ( subscriber_service_id ) ;
ALTER TABLE `core_tenant` ADD INDEX ( provider_service_id ) ;
ALTER TABLE `core_tenant` ADD INDEX ( subscriber_user_id ) ;
ALTER TABLE `core_tenant` ADD INDEX ( subscriber_root_id ) ;
ALTER TABLE `core_tenantrootprivilege` ADD INDEX ( role_id ) ;
ALTER TABLE `core_tenantrootprivilege` ADD INDEX ( tenant_root_id ) ;
ALTER TABLE `core_tenantrootprivilege` ADD INDEX ( user_id ) ;
ALTER TABLE `core_user` ADD INDEX ( site_id ) ;
ALTER TABLE `core_usercredential` ADD INDEX ( name ) ;
ALTER TABLE `core_usercredential` ADD INDEX ( user_id ) ;
ALTER TABLE `core_userdashboardview` ADD INDEX ( dashboardView_id ) ;
ALTER TABLE `core_userdashboardview` ADD INDEX ( user_id ) ;
ALTER TABLE `django_admin_log` ADD INDEX ( content_type_id ) ;
ALTER TABLE `django_admin_log` ADD INDEX ( user_id ) ;
ALTER TABLE `django_session` ADD INDEX ( expire_date ) ;
ALTER TABLE `hpc_accessmap` ADD INDEX ( contentProvider_id ) ;
ALTER TABLE `hpc_cdnprefix` ADD INDEX ( defaultOriginServer_id ) ;
ALTER TABLE `hpc_cdnprefix` ADD INDEX ( contentProvider_id ) ;
ALTER TABLE `hpc_contentprovider` ADD INDEX ( serviceProvider_id ) ;
ALTER TABLE `hpc_contentprovider_users` ADD INDEX ( contentprovider_id ) ;
ALTER TABLE `hpc_contentprovider_users` ADD INDEX ( user_id ) ;
ALTER TABLE `hpc_hpchealthcheck` ADD INDEX ( hpcService_id ) ;
ALTER TABLE `hpc_originserver` ADD INDEX ( contentProvider_id ) ;
ALTER TABLE `hpc_serviceprovider` ADD INDEX ( hpcService_id ) ;
ALTER TABLE `hpc_sitemap` ADD INDEX ( cdnPrefix_id ) ;
ALTER TABLE `hpc_sitemap` ADD INDEX ( hpcService_id ) ;
ALTER TABLE `hpc_sitemap` ADD INDEX ( contentProvider_id ) ;
ALTER TABLE `hpc_sitemap` ADD INDEX ( serviceProvider_id ) ;
ALTER TABLE `requestrouter_servicemap` ADD INDEX ( owner_id ) ;
ALTER TABLE `requestrouter_servicemap` ADD INDEX ( slice_id ) ;
ALTER TABLE `syndicate_storage_slicesecret` ADD INDEX ( slice_id_id ) ;
ALTER TABLE `syndicate_storage_volume` ADD INDEX ( owner_id_id ) ;
ALTER TABLE `syndicate_storage_volumeaccessright` ADD INDEX ( owner_id_id ) ;
ALTER TABLE `syndicate_storage_volumeaccessright` ADD INDEX ( volume_id ) ;
ALTER TABLE `syndicate_storage_volumeslice` ADD INDEX ( volume_id_id ) ;
ALTER TABLE `syndicate_storage_volumeslice` ADD INDEX ( slice_id_id ) ;
