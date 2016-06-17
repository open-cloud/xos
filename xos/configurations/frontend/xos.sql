--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: core_account; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_account (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE public.core_account OWNER TO postgres;

--
-- Name: core_account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_account_id_seq OWNER TO postgres;

--
-- Name: core_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_account_id_seq OWNED BY core_account.id;


--
-- Name: core_addresspool; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_addresspool (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    addresses text,
    inuse text
);


ALTER TABLE public.core_addresspool OWNER TO postgres;

--
-- Name: core_addresspool_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_addresspool_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_addresspool_id_seq OWNER TO postgres;

--
-- Name: core_addresspool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_addresspool_id_seq OWNED BY core_addresspool.id;


--
-- Name: core_charge; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_charge (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    kind character varying(30) NOT NULL,
    state character varying(30) NOT NULL,
    date timestamp with time zone NOT NULL,
    amount double precision NOT NULL,
    "coreHours" double precision NOT NULL,
    account_id integer NOT NULL,
    invoice_id integer,
    object_id integer NOT NULL,
    slice_id integer
);


ALTER TABLE public.core_charge OWNER TO postgres;

--
-- Name: core_charge_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_charge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_charge_id_seq OWNER TO postgres;

--
-- Name: core_charge_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_charge_id_seq OWNED BY core_charge.id;


--
-- Name: core_controller; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controller (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL,
    backend_type character varying(200) NOT NULL,
    version character varying(200) NOT NULL,
    auth_url character varying(200),
    admin_user character varying(200),
    admin_password character varying(200),
    admin_tenant character varying(200),
    domain character varying(200),
    rabbit_host character varying(200),
    rabbit_user character varying(200),
    rabbit_password character varying(200),
    deployment_id integer NOT NULL
);


ALTER TABLE public.core_controller OWNER TO postgres;

--
-- Name: core_controller_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controller_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controller_id_seq OWNER TO postgres;

--
-- Name: core_controller_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controller_id_seq OWNED BY core_controller.id;


--
-- Name: core_controllercredential; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllercredential (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    key_id character varying(1024) NOT NULL,
    enc_value text NOT NULL,
    controller_id integer NOT NULL
);


ALTER TABLE public.core_controllercredential OWNER TO postgres;

--
-- Name: core_controllercredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllercredential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllercredential_id_seq OWNER TO postgres;

--
-- Name: core_controllercredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllercredential_id_seq OWNED BY core_controllercredential.id;


--
-- Name: core_controllerdashboardview; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllerdashboardview (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    enabled boolean NOT NULL,
    url character varying(1024) NOT NULL,
    controller_id integer NOT NULL,
    "dashboardView_id" integer NOT NULL
);


ALTER TABLE public.core_controllerdashboardview OWNER TO postgres;

--
-- Name: core_controllerdashboardview_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllerdashboardview_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllerdashboardview_id_seq OWNER TO postgres;

--
-- Name: core_controllerdashboardview_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllerdashboardview_id_seq OWNED BY core_controllerdashboardview.id;


--
-- Name: core_controllerimages; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllerimages (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    glance_image_id character varying(200),
    controller_id integer NOT NULL,
    image_id integer NOT NULL
);


ALTER TABLE public.core_controllerimages OWNER TO postgres;

--
-- Name: core_controllerimages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllerimages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllerimages_id_seq OWNER TO postgres;

--
-- Name: core_controllerimages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllerimages_id_seq OWNED BY core_controllerimages.id;


--
-- Name: core_controllernetwork; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllernetwork (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    net_id character varying(256),
    router_id character varying(256),
    subnet_id character varying(256),
    subnet character varying(32) NOT NULL,
    controller_id integer NOT NULL,
    network_id integer NOT NULL
);


ALTER TABLE public.core_controllernetwork OWNER TO postgres;

--
-- Name: core_controllernetwork_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllernetwork_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllernetwork_id_seq OWNER TO postgres;

--
-- Name: core_controllernetwork_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllernetwork_id_seq OWNED BY core_controllernetwork.id;


--
-- Name: core_controllerrole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllerrole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_controllerrole OWNER TO postgres;

--
-- Name: core_controllerrole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllerrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllerrole_id_seq OWNER TO postgres;

--
-- Name: core_controllerrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllerrole_id_seq OWNED BY core_controllerrole.id;


--
-- Name: core_controllersite; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllersite (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    tenant_id character varying(200),
    controller_id integer,
    site_id integer NOT NULL
);


ALTER TABLE public.core_controllersite OWNER TO postgres;

--
-- Name: core_controllersite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllersite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllersite_id_seq OWNER TO postgres;

--
-- Name: core_controllersite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllersite_id_seq OWNED BY core_controllersite.id;


--
-- Name: core_controllersiteprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllersiteprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id character varying(200),
    controller_id integer NOT NULL,
    site_privilege_id integer NOT NULL
);


ALTER TABLE public.core_controllersiteprivilege OWNER TO postgres;

--
-- Name: core_controllersiteprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllersiteprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllersiteprivilege_id_seq OWNER TO postgres;

--
-- Name: core_controllersiteprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllersiteprivilege_id_seq OWNED BY core_controllersiteprivilege.id;


--
-- Name: core_controllerslice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllerslice (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    tenant_id character varying(200),
    controller_id integer NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_controllerslice OWNER TO postgres;

--
-- Name: core_controllerslice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllerslice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllerslice_id_seq OWNER TO postgres;

--
-- Name: core_controllerslice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllerslice_id_seq OWNED BY core_controllerslice.id;


--
-- Name: core_controllersliceprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controllersliceprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id character varying(200),
    controller_id integer NOT NULL,
    slice_privilege_id integer NOT NULL
);


ALTER TABLE public.core_controllersliceprivilege OWNER TO postgres;

--
-- Name: core_controllersliceprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controllersliceprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controllersliceprivilege_id_seq OWNER TO postgres;

--
-- Name: core_controllersliceprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controllersliceprivilege_id_seq OWNED BY core_controllersliceprivilege.id;


--
-- Name: core_controlleruser; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_controlleruser (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    kuser_id character varying(200),
    controller_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_controlleruser OWNER TO postgres;

--
-- Name: core_controlleruser_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_controlleruser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_controlleruser_id_seq OWNER TO postgres;

--
-- Name: core_controlleruser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_controlleruser_id_seq OWNED BY core_controlleruser.id;


--
-- Name: core_dashboardview; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_dashboardview (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL,
    url character varying(1024) NOT NULL,
    enabled boolean NOT NULL
);


ALTER TABLE public.core_dashboardview OWNER TO postgres;

--
-- Name: core_dashboardview_deployments; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_dashboardview_deployments (
    id integer NOT NULL,
    dashboardview_id integer NOT NULL,
    deployment_id integer NOT NULL
);


ALTER TABLE public.core_dashboardview_deployments OWNER TO postgres;

--
-- Name: core_dashboardview_deployments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_dashboardview_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_dashboardview_deployments_id_seq OWNER TO postgres;

--
-- Name: core_dashboardview_deployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_dashboardview_deployments_id_seq OWNED BY core_dashboardview_deployments.id;


--
-- Name: core_dashboardview_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_dashboardview_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_dashboardview_id_seq OWNER TO postgres;

--
-- Name: core_dashboardview_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_dashboardview_id_seq OWNED BY core_dashboardview.id;


--
-- Name: core_deployment; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_deployment (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL,
    "accessControl" text NOT NULL
);


ALTER TABLE public.core_deployment OWNER TO postgres;

--
-- Name: core_deployment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_deployment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_deployment_id_seq OWNER TO postgres;

--
-- Name: core_deployment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_deployment_id_seq OWNED BY core_deployment.id;


--
-- Name: core_deploymentprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_deploymentprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    deployment_id integer NOT NULL,
    role_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_deploymentprivilege OWNER TO postgres;

--
-- Name: core_deploymentprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_deploymentprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_deploymentprivilege_id_seq OWNER TO postgres;

--
-- Name: core_deploymentprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_deploymentprivilege_id_seq OWNED BY core_deploymentprivilege.id;


--
-- Name: core_deploymentrole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_deploymentrole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_deploymentrole OWNER TO postgres;

--
-- Name: core_deploymentrole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_deploymentrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_deploymentrole_id_seq OWNER TO postgres;

--
-- Name: core_deploymentrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_deploymentrole_id_seq OWNED BY core_deploymentrole.id;


--
-- Name: core_diag; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_diag (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.core_diag OWNER TO postgres;

--
-- Name: core_diag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_diag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_diag_id_seq OWNER TO postgres;

--
-- Name: core_diag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_diag_id_seq OWNED BY core_diag.id;


--
-- Name: core_flavor; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_flavor (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    description character varying(1024),
    flavor character varying(32) NOT NULL,
    "order" integer NOT NULL,
    "default" boolean NOT NULL
);


ALTER TABLE public.core_flavor OWNER TO postgres;

--
-- Name: core_flavor_deployments; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_flavor_deployments (
    id integer NOT NULL,
    flavor_id integer NOT NULL,
    deployment_id integer NOT NULL
);


ALTER TABLE public.core_flavor_deployments OWNER TO postgres;

--
-- Name: core_flavor_deployments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_flavor_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_flavor_deployments_id_seq OWNER TO postgres;

--
-- Name: core_flavor_deployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_flavor_deployments_id_seq OWNED BY core_flavor_deployments.id;


--
-- Name: core_flavor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_flavor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_flavor_id_seq OWNER TO postgres;

--
-- Name: core_flavor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_flavor_id_seq OWNED BY core_flavor.id;


--
-- Name: core_image; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_image (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(256) NOT NULL,
    kind character varying(30) NOT NULL,
    disk_format character varying(256) NOT NULL,
    container_format character varying(256) NOT NULL,
    path character varying(256),
    tag character varying(256)
);


ALTER TABLE public.core_image OWNER TO postgres;

--
-- Name: core_image_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_image_id_seq OWNER TO postgres;

--
-- Name: core_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_image_id_seq OWNED BY core_image.id;


--
-- Name: core_imagedeployments; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_imagedeployments (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    deployment_id integer NOT NULL,
    image_id integer NOT NULL
);


ALTER TABLE public.core_imagedeployments OWNER TO postgres;

--
-- Name: core_imagedeployments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_imagedeployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_imagedeployments_id_seq OWNER TO postgres;

--
-- Name: core_imagedeployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_imagedeployments_id_seq OWNED BY core_imagedeployments.id;


--
-- Name: core_instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_instance (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    instance_id character varying(200),
    instance_uuid character varying(200),
    name character varying(200) NOT NULL,
    instance_name character varying(200),
    ip inet,
    "numberCores" integer NOT NULL,
    "userData" text,
    isolation character varying(30) NOT NULL,
    volumes text,
    creator_id integer,
    deployment_id integer NOT NULL,
    flavor_id integer NOT NULL,
    image_id integer NOT NULL,
    node_id integer NOT NULL,
    parent_id integer,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_instance OWNER TO postgres;

--
-- Name: core_instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_instance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_instance_id_seq OWNER TO postgres;

--
-- Name: core_instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_instance_id_seq OWNED BY core_instance.id;


--
-- Name: core_invoice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_invoice (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    date timestamp with time zone NOT NULL,
    account_id integer NOT NULL
);


ALTER TABLE public.core_invoice OWNER TO postgres;

--
-- Name: core_invoice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_invoice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_invoice_id_seq OWNER TO postgres;

--
-- Name: core_invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_invoice_id_seq OWNED BY core_invoice.id;


--
-- Name: core_network; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_network (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    subnet character varying(32) NOT NULL,
    ports character varying(1024),
    labels character varying(1024),
    guaranteed_bandwidth integer NOT NULL,
    permit_all_slices boolean NOT NULL,
    topology_parameters text,
    controller_url character varying(1024),
    controller_parameters text,
    network_id character varying(256),
    router_id character varying(256),
    subnet_id character varying(256),
    autoconnect boolean NOT NULL,
    owner_id integer NOT NULL,
    template_id integer NOT NULL
);


ALTER TABLE public.core_network OWNER TO postgres;

--
-- Name: core_network_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_network_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_network_id_seq OWNER TO postgres;

--
-- Name: core_network_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_network_id_seq OWNED BY core_network.id;


--
-- Name: core_network_permitted_slices; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_network_permitted_slices (
    id integer NOT NULL,
    network_id integer NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_network_permitted_slices OWNER TO postgres;

--
-- Name: core_network_permitted_slices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_network_permitted_slices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_network_permitted_slices_id_seq OWNER TO postgres;

--
-- Name: core_network_permitted_slices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_network_permitted_slices_id_seq OWNED BY core_network_permitted_slices.id;


--
-- Name: core_networkparameter; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_networkparameter (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    value character varying(1024) NOT NULL,
    object_id integer NOT NULL,
    content_type_id integer NOT NULL,
    parameter_id integer NOT NULL,
    CONSTRAINT core_networkparameter_object_id_check CHECK ((object_id >= 0))
);


ALTER TABLE public.core_networkparameter OWNER TO postgres;

--
-- Name: core_networkparameter_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_networkparameter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_networkparameter_id_seq OWNER TO postgres;

--
-- Name: core_networkparameter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_networkparameter_id_seq OWNED BY core_networkparameter.id;


--
-- Name: core_networkparametertype; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_networkparametertype (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    description character varying(1024) NOT NULL
);


ALTER TABLE public.core_networkparametertype OWNER TO postgres;

--
-- Name: core_networkparametertype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_networkparametertype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_networkparametertype_id_seq OWNER TO postgres;

--
-- Name: core_networkparametertype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_networkparametertype_id_seq OWNED BY core_networkparametertype.id;


--
-- Name: core_networkslice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_networkslice (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    network_id integer NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_networkslice OWNER TO postgres;

--
-- Name: core_networkslice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_networkslice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_networkslice_id_seq OWNER TO postgres;

--
-- Name: core_networkslice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_networkslice_id_seq OWNED BY core_networkslice.id;


--
-- Name: core_networktemplate; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_networktemplate (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    description character varying(1024),
    guaranteed_bandwidth integer NOT NULL,
    visibility character varying(30) NOT NULL,
    translation character varying(30) NOT NULL,
    access character varying(30),
    shared_network_name character varying(30),
    shared_network_id character varying(256),
    topology_kind character varying(30) NOT NULL,
    controller_kind character varying(30)
);


ALTER TABLE public.core_networktemplate OWNER TO postgres;

--
-- Name: core_networktemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_networktemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_networktemplate_id_seq OWNER TO postgres;

--
-- Name: core_networktemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_networktemplate_id_seq OWNED BY core_networktemplate.id;


--
-- Name: core_node; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_node (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL,
    site_id integer,
    site_deployment_id integer NOT NULL
);


ALTER TABLE public.core_node OWNER TO postgres;

--
-- Name: core_node_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_node_id_seq OWNER TO postgres;

--
-- Name: core_node_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_node_id_seq OWNED BY core_node.id;


--
-- Name: core_nodelabel; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_nodelabel (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.core_nodelabel OWNER TO postgres;

--
-- Name: core_nodelabel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_nodelabel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_nodelabel_id_seq OWNER TO postgres;

--
-- Name: core_nodelabel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_nodelabel_id_seq OWNED BY core_nodelabel.id;


--
-- Name: core_nodelabel_node; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_nodelabel_node (
    id integer NOT NULL,
    nodelabel_id integer NOT NULL,
    node_id integer NOT NULL
);


ALTER TABLE public.core_nodelabel_node OWNER TO postgres;

--
-- Name: core_nodelabel_node_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_nodelabel_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_nodelabel_node_id_seq OWNER TO postgres;

--
-- Name: core_nodelabel_node_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_nodelabel_node_id_seq OWNED BY core_nodelabel_node.id;


--
-- Name: core_payment; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_payment (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    amount double precision NOT NULL,
    date timestamp with time zone NOT NULL,
    account_id integer NOT NULL
);


ALTER TABLE public.core_payment OWNER TO postgres;

--
-- Name: core_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_payment_id_seq OWNER TO postgres;

--
-- Name: core_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_payment_id_seq OWNED BY core_payment.id;


--
-- Name: core_port; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_port (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    ip inet,
    port_id character varying(256),
    mac character varying(256),
    xos_created boolean NOT NULL,
    instance_id integer,
    network_id integer NOT NULL
);


ALTER TABLE public.core_port OWNER TO postgres;

--
-- Name: core_port_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_port_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_port_id_seq OWNER TO postgres;

--
-- Name: core_port_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_port_id_seq OWNED BY core_port.id;


--
-- Name: core_program; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_program (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(30) NOT NULL,
    description text,
    kind character varying(30) NOT NULL,
    command character varying(30),
    contents text,
    output text,
    messages text,
    status text,
    owner_id integer
);


ALTER TABLE public.core_program OWNER TO postgres;

--
-- Name: core_program_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_program_id_seq OWNER TO postgres;

--
-- Name: core_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_program_id_seq OWNED BY core_program.id;


--
-- Name: core_project; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_project (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.core_project OWNER TO postgres;

--
-- Name: core_project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_project_id_seq OWNER TO postgres;

--
-- Name: core_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_project_id_seq OWNED BY core_project.id;


--
-- Name: core_reservation; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_reservation (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    "startTime" timestamp with time zone NOT NULL,
    duration integer NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_reservation OWNER TO postgres;

--
-- Name: core_reservation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_reservation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_reservation_id_seq OWNER TO postgres;

--
-- Name: core_reservation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_reservation_id_seq OWNED BY core_reservation.id;


--
-- Name: core_reservedresource; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_reservedresource (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    quantity integer NOT NULL,
    instance_id integer NOT NULL,
    "reservationSet_id" integer NOT NULL,
    resource_id integer NOT NULL
);


ALTER TABLE public.core_reservedresource OWNER TO postgres;

--
-- Name: core_reservedresource_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_reservedresource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_reservedresource_id_seq OWNER TO postgres;

--
-- Name: core_reservedresource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_reservedresource_id_seq OWNED BY core_reservedresource.id;


--
-- Name: core_role; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_role (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_type character varying(80) NOT NULL,
    role character varying(80),
    description character varying(120) NOT NULL,
    content_type_id integer NOT NULL
);


ALTER TABLE public.core_role OWNER TO postgres;

--
-- Name: core_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_role_id_seq OWNER TO postgres;

--
-- Name: core_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_role_id_seq OWNED BY core_role.id;


--
-- Name: core_router; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_router (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    owner_id integer NOT NULL
);


ALTER TABLE public.core_router OWNER TO postgres;

--
-- Name: core_router_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_router_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_router_id_seq OWNER TO postgres;

--
-- Name: core_router_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_router_id_seq OWNED BY core_router.id;


--
-- Name: core_router_networks; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_router_networks (
    id integer NOT NULL,
    router_id integer NOT NULL,
    network_id integer NOT NULL
);


ALTER TABLE public.core_router_networks OWNER TO postgres;

--
-- Name: core_router_networks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_router_networks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_router_networks_id_seq OWNER TO postgres;

--
-- Name: core_router_networks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_router_networks_id_seq OWNED BY core_router_networks.id;


--
-- Name: core_router_permittedNetworks; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "core_router_permittedNetworks" (
    id integer NOT NULL,
    router_id integer NOT NULL,
    network_id integer NOT NULL
);


ALTER TABLE public."core_router_permittedNetworks" OWNER TO postgres;

--
-- Name: core_router_permittedNetworks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "core_router_permittedNetworks_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."core_router_permittedNetworks_id_seq" OWNER TO postgres;

--
-- Name: core_router_permittedNetworks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "core_router_permittedNetworks_id_seq" OWNED BY "core_router_permittedNetworks".id;


--
-- Name: core_service; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_service (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    description text,
    enabled boolean NOT NULL,
    kind character varying(30) NOT NULL,
    name character varying(30) NOT NULL,
    "versionNumber" character varying(30) NOT NULL,
    published boolean NOT NULL,
    view_url character varying(1024),
    icon_url character varying(1024),
    public_key text,
    private_key_fn character varying(1024),
    service_specific_id character varying(30),
    service_specific_attribute text
);


ALTER TABLE public.core_service OWNER TO postgres;

--
-- Name: core_service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_service_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_service_id_seq OWNER TO postgres;

--
-- Name: core_service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_service_id_seq OWNED BY core_service.id;


--
-- Name: core_serviceattribute; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_serviceattribute (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    value character varying(1024) NOT NULL,
    service_id integer NOT NULL
);


ALTER TABLE public.core_serviceattribute OWNER TO postgres;

--
-- Name: core_serviceattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_serviceattribute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_serviceattribute_id_seq OWNER TO postgres;

--
-- Name: core_serviceattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_serviceattribute_id_seq OWNED BY core_serviceattribute.id;


--
-- Name: core_serviceclass; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_serviceclass (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    description character varying(255) NOT NULL,
    commitment integer NOT NULL,
    "membershipFee" integer NOT NULL,
    "membershipFeeMonths" integer NOT NULL,
    "upgradeRequiresApproval" boolean NOT NULL
);


ALTER TABLE public.core_serviceclass OWNER TO postgres;

--
-- Name: core_serviceclass_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_serviceclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_serviceclass_id_seq OWNER TO postgres;

--
-- Name: core_serviceclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_serviceclass_id_seq OWNED BY core_serviceclass.id;


--
-- Name: core_serviceclass_upgradeFrom; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "core_serviceclass_upgradeFrom" (
    id integer NOT NULL,
    from_serviceclass_id integer NOT NULL,
    to_serviceclass_id integer NOT NULL
);


ALTER TABLE public."core_serviceclass_upgradeFrom" OWNER TO postgres;

--
-- Name: core_serviceclass_upgradeFrom_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "core_serviceclass_upgradeFrom_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."core_serviceclass_upgradeFrom_id_seq" OWNER TO postgres;

--
-- Name: core_serviceclass_upgradeFrom_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "core_serviceclass_upgradeFrom_id_seq" OWNED BY "core_serviceclass_upgradeFrom".id;


--
-- Name: core_serviceprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_serviceprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id integer NOT NULL,
    service_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_serviceprivilege OWNER TO postgres;

--
-- Name: core_serviceprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_serviceprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_serviceprivilege_id_seq OWNER TO postgres;

--
-- Name: core_serviceprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_serviceprivilege_id_seq OWNED BY core_serviceprivilege.id;


--
-- Name: core_serviceresource; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_serviceresource (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(32) NOT NULL,
    "maxUnitsDeployment" integer NOT NULL,
    "maxUnitsNode" integer NOT NULL,
    "maxDuration" integer NOT NULL,
    "bucketInRate" integer NOT NULL,
    "bucketMaxSize" integer NOT NULL,
    cost integer NOT NULL,
    "calendarReservable" boolean NOT NULL,
    "serviceClass_id" integer NOT NULL
);


ALTER TABLE public.core_serviceresource OWNER TO postgres;

--
-- Name: core_serviceresource_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_serviceresource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_serviceresource_id_seq OWNER TO postgres;

--
-- Name: core_serviceresource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_serviceresource_id_seq OWNED BY core_serviceresource.id;


--
-- Name: core_servicerole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_servicerole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_servicerole OWNER TO postgres;

--
-- Name: core_servicerole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_servicerole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_servicerole_id_seq OWNER TO postgres;

--
-- Name: core_servicerole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_servicerole_id_seq OWNED BY core_servicerole.id;


--
-- Name: core_site; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_site (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(200) NOT NULL,
    site_url character varying(512),
    enabled boolean NOT NULL,
    hosts_nodes boolean NOT NULL,
    hosts_users boolean NOT NULL,
    location character varying(42) NOT NULL,
    longitude double precision,
    latitude double precision,
    login_base character varying(50) NOT NULL,
    is_public boolean NOT NULL,
    abbreviated_name character varying(80) NOT NULL
);


ALTER TABLE public.core_site OWNER TO postgres;

--
-- Name: core_site_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_site_id_seq OWNER TO postgres;

--
-- Name: core_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_site_id_seq OWNED BY core_site.id;


--
-- Name: core_sitecredential; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_sitecredential (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    key_id character varying(1024) NOT NULL,
    enc_value text NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE public.core_sitecredential OWNER TO postgres;

--
-- Name: core_sitecredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_sitecredential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_sitecredential_id_seq OWNER TO postgres;

--
-- Name: core_sitecredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_sitecredential_id_seq OWNED BY core_sitecredential.id;


--
-- Name: core_sitedeployment; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_sitedeployment (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    availability_zone character varying(200),
    controller_id integer,
    deployment_id integer NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE public.core_sitedeployment OWNER TO postgres;

--
-- Name: core_sitedeployment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_sitedeployment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_sitedeployment_id_seq OWNER TO postgres;

--
-- Name: core_sitedeployment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_sitedeployment_id_seq OWNED BY core_sitedeployment.id;


--
-- Name: core_siteprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_siteprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id integer NOT NULL,
    site_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_siteprivilege OWNER TO postgres;

--
-- Name: core_siteprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_siteprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_siteprivilege_id_seq OWNER TO postgres;

--
-- Name: core_siteprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_siteprivilege_id_seq OWNED BY core_siteprivilege.id;


--
-- Name: core_siterole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_siterole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_siterole OWNER TO postgres;

--
-- Name: core_siterole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_siterole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_siterole_id_seq OWNER TO postgres;

--
-- Name: core_siterole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_siterole_id_seq OWNED BY core_siterole.id;


--
-- Name: core_slice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_slice (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(80) NOT NULL,
    enabled boolean NOT NULL,
    omf_friendly boolean NOT NULL,
    description text NOT NULL,
    slice_url character varying(512) NOT NULL,
    max_instances integer NOT NULL,
    network character varying(256),
    exposed_ports character varying(256),
    mount_data_sets character varying(256),
    default_isolation character varying(30) NOT NULL,
    creator_id integer,
    default_flavor_id integer,
    default_image_id integer,
    service_id integer,
    "serviceClass_id" integer,
    site_id integer NOT NULL
);


ALTER TABLE public.core_slice OWNER TO postgres;

--
-- Name: core_slice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_slice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_slice_id_seq OWNER TO postgres;

--
-- Name: core_slice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_slice_id_seq OWNED BY core_slice.id;


--
-- Name: core_slicecredential; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_slicecredential (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    key_id character varying(1024) NOT NULL,
    enc_value text NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_slicecredential OWNER TO postgres;

--
-- Name: core_slicecredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_slicecredential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_slicecredential_id_seq OWNER TO postgres;

--
-- Name: core_slicecredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_slicecredential_id_seq OWNED BY core_slicecredential.id;


--
-- Name: core_sliceprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_sliceprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id integer NOT NULL,
    slice_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_sliceprivilege OWNER TO postgres;

--
-- Name: core_sliceprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_sliceprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_sliceprivilege_id_seq OWNER TO postgres;

--
-- Name: core_sliceprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_sliceprivilege_id_seq OWNED BY core_sliceprivilege.id;


--
-- Name: core_slicerole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_slicerole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_slicerole OWNER TO postgres;

--
-- Name: core_slicerole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_slicerole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_slicerole_id_seq OWNER TO postgres;

--
-- Name: core_slicerole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_slicerole_id_seq OWNED BY core_slicerole.id;


--
-- Name: core_slicetag; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_slicetag (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(30) NOT NULL,
    value character varying(1024) NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.core_slicetag OWNER TO postgres;

--
-- Name: core_slicetag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_slicetag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_slicetag_id_seq OWNER TO postgres;

--
-- Name: core_slicetag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_slicetag_id_seq OWNED BY core_slicetag.id;


--
-- Name: core_tag; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tag (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    value character varying(1024) NOT NULL,
    object_id integer NOT NULL,
    content_type_id integer NOT NULL,
    service_id integer NOT NULL,
    CONSTRAINT core_tag_object_id_check CHECK ((object_id >= 0))
);


ALTER TABLE public.core_tag OWNER TO postgres;

--
-- Name: core_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tag_id_seq OWNER TO postgres;

--
-- Name: core_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tag_id_seq OWNED BY core_tag.id;


--
-- Name: core_tenant; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tenant (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    kind character varying(30) NOT NULL,
    service_specific_id character varying(30),
    service_specific_attribute text,
    connect_method character varying(30) NOT NULL,
    provider_service_id integer NOT NULL,
    subscriber_root_id integer,
    subscriber_service_id integer,
    subscriber_tenant_id integer,
    subscriber_user_id integer
);


ALTER TABLE public.core_tenant OWNER TO postgres;

--
-- Name: core_tenant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tenant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tenant_id_seq OWNER TO postgres;

--
-- Name: core_tenant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tenant_id_seq OWNED BY core_tenant.id;


--
-- Name: core_tenantattribute; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tenantattribute (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    value text NOT NULL,
    tenant_id integer NOT NULL
);


ALTER TABLE public.core_tenantattribute OWNER TO postgres;

--
-- Name: core_tenantattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tenantattribute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tenantattribute_id_seq OWNER TO postgres;

--
-- Name: core_tenantattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tenantattribute_id_seq OWNED BY core_tenantattribute.id;


--
-- Name: core_tenantroot; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tenantroot (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    kind character varying(30) NOT NULL,
    name character varying(255),
    service_specific_attribute text,
    service_specific_id character varying(30)
);


ALTER TABLE public.core_tenantroot OWNER TO postgres;

--
-- Name: core_tenantroot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tenantroot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tenantroot_id_seq OWNER TO postgres;

--
-- Name: core_tenantroot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tenantroot_id_seq OWNED BY core_tenantroot.id;


--
-- Name: core_tenantrootprivilege; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tenantrootprivilege (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role_id integer NOT NULL,
    tenant_root_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_tenantrootprivilege OWNER TO postgres;

--
-- Name: core_tenantrootprivilege_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tenantrootprivilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tenantrootprivilege_id_seq OWNER TO postgres;

--
-- Name: core_tenantrootprivilege_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tenantrootprivilege_id_seq OWNED BY core_tenantrootprivilege.id;


--
-- Name: core_tenantrootrole; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_tenantrootrole (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    role character varying(30) NOT NULL
);


ALTER TABLE public.core_tenantrootrole OWNER TO postgres;

--
-- Name: core_tenantrootrole_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_tenantrootrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_tenantrootrole_id_seq OWNER TO postgres;

--
-- Name: core_tenantrootrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_tenantrootrole_id_seq OWNED BY core_tenantrootrole.id;


--
-- Name: core_usableobject; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_usableobject (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(1024) NOT NULL
);


ALTER TABLE public.core_usableobject OWNER TO postgres;

--
-- Name: core_usableobject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_usableobject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_usableobject_id_seq OWNER TO postgres;

--
-- Name: core_usableobject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_usableobject_id_seq OWNED BY core_usableobject.id;


--
-- Name: core_user; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(255) NOT NULL,
    firstname character varying(200) NOT NULL,
    lastname character varying(200) NOT NULL,
    phone character varying(100),
    user_url character varying(200),
    public_key text,
    is_active boolean NOT NULL,
    is_admin boolean NOT NULL,
    is_staff boolean NOT NULL,
    is_readonly boolean NOT NULL,
    is_registering boolean NOT NULL,
    is_appuser boolean NOT NULL,
    login_page character varying(200),
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    timezone character varying(100) NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE public.core_user OWNER TO postgres;

--
-- Name: core_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_user_id_seq OWNER TO postgres;

--
-- Name: core_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_user_id_seq OWNED BY core_user.id;


--
-- Name: core_usercredential; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_usercredential (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(128) NOT NULL,
    key_id character varying(1024) NOT NULL,
    enc_value text NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_usercredential OWNER TO postgres;

--
-- Name: core_usercredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_usercredential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_usercredential_id_seq OWNER TO postgres;

--
-- Name: core_usercredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_usercredential_id_seq OWNED BY core_usercredential.id;


--
-- Name: core_userdashboardview; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE core_userdashboardview (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    "order" integer NOT NULL,
    "dashboardView_id" integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_userdashboardview OWNER TO postgres;

--
-- Name: core_userdashboardview_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE core_userdashboardview_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_userdashboardview_id_seq OWNER TO postgres;

--
-- Name: core_userdashboardview_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE core_userdashboardview_id_seq OWNED BY core_userdashboardview.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: hpc_accessmap; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_accessmap (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    map character varying(100) NOT NULL,
    "contentProvider_id" integer NOT NULL
);


ALTER TABLE public.hpc_accessmap OWNER TO postgres;

--
-- Name: hpc_accessmap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_accessmap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_accessmap_id_seq OWNER TO postgres;

--
-- Name: hpc_accessmap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_accessmap_id_seq OWNED BY hpc_accessmap.id;


--
-- Name: hpc_cdnprefix; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_cdnprefix (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    cdn_prefix_id integer,
    prefix character varying(200) NOT NULL,
    description text,
    enabled boolean NOT NULL,
    "contentProvider_id" integer NOT NULL,
    "defaultOriginServer_id" integer
);


ALTER TABLE public.hpc_cdnprefix OWNER TO postgres;

--
-- Name: hpc_cdnprefix_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_cdnprefix_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_cdnprefix_id_seq OWNER TO postgres;

--
-- Name: hpc_cdnprefix_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_cdnprefix_id_seq OWNED BY hpc_cdnprefix.id;


--
-- Name: hpc_contentprovider; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_contentprovider (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    content_provider_id integer,
    name character varying(254) NOT NULL,
    enabled boolean NOT NULL,
    description text,
    "serviceProvider_id" integer NOT NULL
);


ALTER TABLE public.hpc_contentprovider OWNER TO postgres;

--
-- Name: hpc_contentprovider_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_contentprovider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_contentprovider_id_seq OWNER TO postgres;

--
-- Name: hpc_contentprovider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_contentprovider_id_seq OWNED BY hpc_contentprovider.id;


--
-- Name: hpc_contentprovider_users; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_contentprovider_users (
    id integer NOT NULL,
    contentprovider_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.hpc_contentprovider_users OWNER TO postgres;

--
-- Name: hpc_contentprovider_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_contentprovider_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_contentprovider_users_id_seq OWNER TO postgres;

--
-- Name: hpc_contentprovider_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_contentprovider_users_id_seq OWNED BY hpc_contentprovider_users.id;


--
-- Name: hpc_hpchealthcheck; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_hpchealthcheck (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    kind character varying(30) NOT NULL,
    resource_name character varying(1024) NOT NULL,
    result_contains character varying(1024),
    result_min_size integer,
    result_max_size integer,
    "hpcService_id" integer
);


ALTER TABLE public.hpc_hpchealthcheck OWNER TO postgres;

--
-- Name: hpc_hpchealthcheck_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_hpchealthcheck_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_hpchealthcheck_id_seq OWNER TO postgres;

--
-- Name: hpc_hpchealthcheck_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_hpchealthcheck_id_seq OWNED BY hpc_hpchealthcheck.id;


--
-- Name: hpc_hpcservice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_hpcservice (
    service_ptr_id integer NOT NULL,
    cmi_hostname character varying(254),
    hpc_port80 boolean NOT NULL,
    watcher_hpc_network character varying(254),
    watcher_dnsdemux_network character varying(254),
    watcher_dnsredir_network character varying(254)
);


ALTER TABLE public.hpc_hpcservice OWNER TO postgres;

--
-- Name: hpc_originserver; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_originserver (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    origin_server_id integer,
    url character varying(1024) NOT NULL,
    authenticated boolean NOT NULL,
    enabled boolean NOT NULL,
    protocol character varying(12) NOT NULL,
    redirects boolean NOT NULL,
    description text,
    "contentProvider_id" integer NOT NULL
);


ALTER TABLE public.hpc_originserver OWNER TO postgres;

--
-- Name: hpc_originserver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_originserver_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_originserver_id_seq OWNER TO postgres;

--
-- Name: hpc_originserver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_originserver_id_seq OWNED BY hpc_originserver.id;


--
-- Name: hpc_serviceprovider; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_serviceprovider (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    service_provider_id integer,
    name character varying(254) NOT NULL,
    description text,
    enabled boolean NOT NULL,
    "hpcService_id" integer NOT NULL
);


ALTER TABLE public.hpc_serviceprovider OWNER TO postgres;

--
-- Name: hpc_serviceprovider_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_serviceprovider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_serviceprovider_id_seq OWNER TO postgres;

--
-- Name: hpc_serviceprovider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_serviceprovider_id_seq OWNED BY hpc_serviceprovider.id;


--
-- Name: hpc_sitemap; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hpc_sitemap (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    map character varying(100) NOT NULL,
    map_id integer,
    "cdnPrefix_id" integer,
    "contentProvider_id" integer,
    "hpcService_id" integer,
    "serviceProvider_id" integer
);


ALTER TABLE public.hpc_sitemap OWNER TO postgres;

--
-- Name: hpc_sitemap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hpc_sitemap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hpc_sitemap_id_seq OWNER TO postgres;

--
-- Name: hpc_sitemap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE hpc_sitemap_id_seq OWNED BY hpc_sitemap.id;


--
-- Name: requestrouter_requestrouterservice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE requestrouter_requestrouterservice (
    service_ptr_id integer NOT NULL,
    "behindNat" boolean NOT NULL,
    "defaultTTL" integer NOT NULL,
    "defaultAction" character varying(30) NOT NULL,
    "lastResortAction" character varying(30) NOT NULL,
    "maxAnswers" integer NOT NULL,
    CONSTRAINT "requestrouter_requestrouterservice_defaultTTL_check" CHECK (("defaultTTL" >= 0)),
    CONSTRAINT "requestrouter_requestrouterservice_maxAnswers_check" CHECK (("maxAnswers" >= 0))
);


ALTER TABLE public.requestrouter_requestrouterservice OWNER TO postgres;

--
-- Name: requestrouter_servicemap; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE requestrouter_servicemap (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(50) NOT NULL,
    prefix character varying(256) NOT NULL,
    "siteMap" character varying(100) NOT NULL,
    "accessMap" character varying(100) NOT NULL,
    owner_id integer NOT NULL,
    slice_id integer NOT NULL
);


ALTER TABLE public.requestrouter_servicemap OWNER TO postgres;

--
-- Name: requestrouter_servicemap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE requestrouter_servicemap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.requestrouter_servicemap_id_seq OWNER TO postgres;

--
-- Name: requestrouter_servicemap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE requestrouter_servicemap_id_seq OWNED BY requestrouter_servicemap.id;


--
-- Name: syndicate_storage_slicesecret; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_slicesecret (
    id integer NOT NULL,
    secret text NOT NULL,
    slice_id_id integer NOT NULL
);


ALTER TABLE public.syndicate_storage_slicesecret OWNER TO postgres;

--
-- Name: syndicate_storage_slicesecret_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE syndicate_storage_slicesecret_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syndicate_storage_slicesecret_id_seq OWNER TO postgres;

--
-- Name: syndicate_storage_slicesecret_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE syndicate_storage_slicesecret_id_seq OWNED BY syndicate_storage_slicesecret.id;


--
-- Name: syndicate_storage_syndicateprincipal; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_syndicateprincipal (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    principal_id text NOT NULL,
    public_key_pem text NOT NULL,
    sealed_private_key text NOT NULL
);


ALTER TABLE public.syndicate_storage_syndicateprincipal OWNER TO postgres;

--
-- Name: syndicate_storage_syndicateprincipal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE syndicate_storage_syndicateprincipal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syndicate_storage_syndicateprincipal_id_seq OWNER TO postgres;

--
-- Name: syndicate_storage_syndicateprincipal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE syndicate_storage_syndicateprincipal_id_seq OWNED BY syndicate_storage_syndicateprincipal.id;


--
-- Name: syndicate_storage_syndicateservice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_syndicateservice (
    service_ptr_id integer NOT NULL
);


ALTER TABLE public.syndicate_storage_syndicateservice OWNER TO postgres;

--
-- Name: syndicate_storage_volume; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_volume (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    blocksize integer NOT NULL,
    private boolean NOT NULL,
    archive boolean NOT NULL,
    cap_read_data boolean NOT NULL,
    cap_write_data boolean NOT NULL,
    cap_host_data boolean NOT NULL,
    owner_id_id integer NOT NULL,
    CONSTRAINT syndicate_storage_volume_blocksize_check CHECK ((blocksize >= 0))
);


ALTER TABLE public.syndicate_storage_volume OWNER TO postgres;

--
-- Name: syndicate_storage_volume_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE syndicate_storage_volume_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syndicate_storage_volume_id_seq OWNER TO postgres;

--
-- Name: syndicate_storage_volume_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE syndicate_storage_volume_id_seq OWNED BY syndicate_storage_volume.id;


--
-- Name: syndicate_storage_volumeaccessright; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_volumeaccessright (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    cap_read_data boolean NOT NULL,
    cap_write_data boolean NOT NULL,
    cap_host_data boolean NOT NULL,
    owner_id_id integer NOT NULL,
    volume_id integer NOT NULL
);


ALTER TABLE public.syndicate_storage_volumeaccessright OWNER TO postgres;

--
-- Name: syndicate_storage_volumeaccessright_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE syndicate_storage_volumeaccessright_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syndicate_storage_volumeaccessright_id_seq OWNER TO postgres;

--
-- Name: syndicate_storage_volumeaccessright_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE syndicate_storage_volumeaccessright_id_seq OWNED BY syndicate_storage_volumeaccessright.id;


--
-- Name: syndicate_storage_volumeslice; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE syndicate_storage_volumeslice (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    enacted timestamp with time zone,
    policed timestamp with time zone,
    backend_register character varying(140),
    backend_status character varying(1024) NOT NULL,
    deleted boolean NOT NULL,
    write_protect boolean NOT NULL,
    lazy_blocked boolean NOT NULL,
    no_sync boolean NOT NULL,
    cap_read_data boolean NOT NULL,
    cap_write_data boolean NOT NULL,
    cap_host_data boolean NOT NULL,
    "UG_portnum" integer NOT NULL,
    "RG_portnum" integer NOT NULL,
    credentials_blob text,
    slice_id_id integer NOT NULL,
    volume_id_id integer NOT NULL,
    CONSTRAINT "syndicate_storage_volumeslice_RG_portnum_check" CHECK (("RG_portnum" >= 0)),
    CONSTRAINT "syndicate_storage_volumeslice_UG_portnum_check" CHECK (("UG_portnum" >= 0))
);


ALTER TABLE public.syndicate_storage_volumeslice OWNER TO postgres;

--
-- Name: syndicate_storage_volumeslice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE syndicate_storage_volumeslice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syndicate_storage_volumeslice_id_seq OWNER TO postgres;

--
-- Name: syndicate_storage_volumeslice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE syndicate_storage_volumeslice_id_seq OWNED BY syndicate_storage_volumeslice.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_account ALTER COLUMN id SET DEFAULT nextval('core_account_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_addresspool ALTER COLUMN id SET DEFAULT nextval('core_addresspool_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_charge ALTER COLUMN id SET DEFAULT nextval('core_charge_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controller ALTER COLUMN id SET DEFAULT nextval('core_controller_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllercredential ALTER COLUMN id SET DEFAULT nextval('core_controllercredential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerdashboardview ALTER COLUMN id SET DEFAULT nextval('core_controllerdashboardview_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerimages ALTER COLUMN id SET DEFAULT nextval('core_controllerimages_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllernetwork ALTER COLUMN id SET DEFAULT nextval('core_controllernetwork_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerrole ALTER COLUMN id SET DEFAULT nextval('core_controllerrole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersite ALTER COLUMN id SET DEFAULT nextval('core_controllersite_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersiteprivilege ALTER COLUMN id SET DEFAULT nextval('core_controllersiteprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerslice ALTER COLUMN id SET DEFAULT nextval('core_controllerslice_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersliceprivilege ALTER COLUMN id SET DEFAULT nextval('core_controllersliceprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controlleruser ALTER COLUMN id SET DEFAULT nextval('core_controlleruser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_dashboardview ALTER COLUMN id SET DEFAULT nextval('core_dashboardview_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_dashboardview_deployments ALTER COLUMN id SET DEFAULT nextval('core_dashboardview_deployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deployment ALTER COLUMN id SET DEFAULT nextval('core_deployment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deploymentprivilege ALTER COLUMN id SET DEFAULT nextval('core_deploymentprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deploymentrole ALTER COLUMN id SET DEFAULT nextval('core_deploymentrole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_diag ALTER COLUMN id SET DEFAULT nextval('core_diag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_flavor ALTER COLUMN id SET DEFAULT nextval('core_flavor_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_flavor_deployments ALTER COLUMN id SET DEFAULT nextval('core_flavor_deployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_image ALTER COLUMN id SET DEFAULT nextval('core_image_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_imagedeployments ALTER COLUMN id SET DEFAULT nextval('core_imagedeployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance ALTER COLUMN id SET DEFAULT nextval('core_instance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_invoice ALTER COLUMN id SET DEFAULT nextval('core_invoice_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network ALTER COLUMN id SET DEFAULT nextval('core_network_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network_permitted_slices ALTER COLUMN id SET DEFAULT nextval('core_network_permitted_slices_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkparameter ALTER COLUMN id SET DEFAULT nextval('core_networkparameter_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkparametertype ALTER COLUMN id SET DEFAULT nextval('core_networkparametertype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkslice ALTER COLUMN id SET DEFAULT nextval('core_networkslice_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networktemplate ALTER COLUMN id SET DEFAULT nextval('core_networktemplate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_node ALTER COLUMN id SET DEFAULT nextval('core_node_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_nodelabel ALTER COLUMN id SET DEFAULT nextval('core_nodelabel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_nodelabel_node ALTER COLUMN id SET DEFAULT nextval('core_nodelabel_node_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_payment ALTER COLUMN id SET DEFAULT nextval('core_payment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_port ALTER COLUMN id SET DEFAULT nextval('core_port_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_program ALTER COLUMN id SET DEFAULT nextval('core_program_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_project ALTER COLUMN id SET DEFAULT nextval('core_project_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservation ALTER COLUMN id SET DEFAULT nextval('core_reservation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservedresource ALTER COLUMN id SET DEFAULT nextval('core_reservedresource_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_role ALTER COLUMN id SET DEFAULT nextval('core_role_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_router ALTER COLUMN id SET DEFAULT nextval('core_router_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_router_networks ALTER COLUMN id SET DEFAULT nextval('core_router_networks_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_router_permittedNetworks" ALTER COLUMN id SET DEFAULT nextval('"core_router_permittedNetworks_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_service ALTER COLUMN id SET DEFAULT nextval('core_service_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceattribute ALTER COLUMN id SET DEFAULT nextval('core_serviceattribute_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceclass ALTER COLUMN id SET DEFAULT nextval('core_serviceclass_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_serviceclass_upgradeFrom" ALTER COLUMN id SET DEFAULT nextval('"core_serviceclass_upgradeFrom_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceprivilege ALTER COLUMN id SET DEFAULT nextval('core_serviceprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceresource ALTER COLUMN id SET DEFAULT nextval('core_serviceresource_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_servicerole ALTER COLUMN id SET DEFAULT nextval('core_servicerole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_site ALTER COLUMN id SET DEFAULT nextval('core_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitecredential ALTER COLUMN id SET DEFAULT nextval('core_sitecredential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitedeployment ALTER COLUMN id SET DEFAULT nextval('core_sitedeployment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_siteprivilege ALTER COLUMN id SET DEFAULT nextval('core_siteprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_siterole ALTER COLUMN id SET DEFAULT nextval('core_siterole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice ALTER COLUMN id SET DEFAULT nextval('core_slice_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slicecredential ALTER COLUMN id SET DEFAULT nextval('core_slicecredential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sliceprivilege ALTER COLUMN id SET DEFAULT nextval('core_sliceprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slicerole ALTER COLUMN id SET DEFAULT nextval('core_slicerole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slicetag ALTER COLUMN id SET DEFAULT nextval('core_slicetag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tag ALTER COLUMN id SET DEFAULT nextval('core_tag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant ALTER COLUMN id SET DEFAULT nextval('core_tenant_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantattribute ALTER COLUMN id SET DEFAULT nextval('core_tenantattribute_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantroot ALTER COLUMN id SET DEFAULT nextval('core_tenantroot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantrootprivilege ALTER COLUMN id SET DEFAULT nextval('core_tenantrootprivilege_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantrootrole ALTER COLUMN id SET DEFAULT nextval('core_tenantrootrole_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_usableobject ALTER COLUMN id SET DEFAULT nextval('core_usableobject_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_user ALTER COLUMN id SET DEFAULT nextval('core_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_usercredential ALTER COLUMN id SET DEFAULT nextval('core_usercredential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_userdashboardview ALTER COLUMN id SET DEFAULT nextval('core_userdashboardview_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_accessmap ALTER COLUMN id SET DEFAULT nextval('hpc_accessmap_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_cdnprefix ALTER COLUMN id SET DEFAULT nextval('hpc_cdnprefix_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_contentprovider ALTER COLUMN id SET DEFAULT nextval('hpc_contentprovider_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_contentprovider_users ALTER COLUMN id SET DEFAULT nextval('hpc_contentprovider_users_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_hpchealthcheck ALTER COLUMN id SET DEFAULT nextval('hpc_hpchealthcheck_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_originserver ALTER COLUMN id SET DEFAULT nextval('hpc_originserver_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_serviceprovider ALTER COLUMN id SET DEFAULT nextval('hpc_serviceprovider_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_sitemap ALTER COLUMN id SET DEFAULT nextval('hpc_sitemap_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY requestrouter_servicemap ALTER COLUMN id SET DEFAULT nextval('requestrouter_servicemap_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_slicesecret ALTER COLUMN id SET DEFAULT nextval('syndicate_storage_slicesecret_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_syndicateprincipal ALTER COLUMN id SET DEFAULT nextval('syndicate_storage_syndicateprincipal_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volume ALTER COLUMN id SET DEFAULT nextval('syndicate_storage_volume_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeaccessright ALTER COLUMN id SET DEFAULT nextval('syndicate_storage_volumeaccessright_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeslice ALTER COLUMN id SET DEFAULT nextval('syndicate_storage_volumeslice_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add permission	1	add_permission
2	Can change permission	1	change_permission
3	Can delete permission	1	delete_permission
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add content type	3	add_contenttype
8	Can change content type	3	change_contenttype
9	Can delete content type	3	delete_contenttype
10	Can add session	4	add_session
11	Can change session	4	change_session
12	Can delete session	4	delete_session
13	Can add log entry	5	add_logentry
14	Can change log entry	5	change_logentry
15	Can delete log entry	5	delete_logentry
16	Can add project	6	add_project
17	Can change project	6	change_project
18	Can delete project	6	delete_project
19	Can add service	7	add_service
20	Can change service	7	change_service
21	Can delete service	7	delete_service
22	Can add service attribute	8	add_serviceattribute
23	Can change service attribute	8	change_serviceattribute
24	Can delete service attribute	8	delete_serviceattribute
25	Can add service role	9	add_servicerole
26	Can change service role	9	change_servicerole
27	Can delete service role	9	delete_servicerole
28	Can add service privilege	10	add_serviceprivilege
29	Can change service privilege	10	change_serviceprivilege
30	Can delete service privilege	10	delete_serviceprivilege
31	Can add tenant root	11	add_tenantroot
32	Can change tenant root	11	change_tenantroot
33	Can delete tenant root	11	delete_tenantroot
34	Can add tenant	12	add_tenant
35	Can change tenant	12	change_tenant
36	Can delete tenant	12	delete_tenant
37	Can add tenant with container	12	add_tenantwithcontainer
38	Can change tenant with container	12	change_tenantwithcontainer
39	Can delete tenant with container	12	delete_tenantwithcontainer
40	Can add coarse tenant	12	add_coarsetenant
41	Can change coarse tenant	12	change_coarsetenant
42	Can delete coarse tenant	12	delete_coarsetenant
43	Can add subscriber	11	add_subscriber
44	Can change subscriber	11	change_subscriber
45	Can delete subscriber	11	delete_subscriber
46	Can add provider	11	add_provider
47	Can change provider	11	change_provider
48	Can delete provider	11	delete_provider
49	Can add tenant attribute	13	add_tenantattribute
50	Can change tenant attribute	13	change_tenantattribute
51	Can delete tenant attribute	13	delete_tenantattribute
52	Can add tenant root role	14	add_tenantrootrole
53	Can change tenant root role	14	change_tenantrootrole
54	Can delete tenant root role	14	delete_tenantrootrole
55	Can add tenant root privilege	15	add_tenantrootprivilege
56	Can change tenant root privilege	15	change_tenantrootprivilege
57	Can delete tenant root privilege	15	delete_tenantrootprivilege
58	Can add tag	16	add_tag
59	Can change tag	16	change_tag
60	Can delete tag	16	delete_tag
61	Can add role	17	add_role
62	Can change role	17	change_role
63	Can delete role	17	delete_role
64	Can add site	18	add_site
65	Can change site	18	change_site
66	Can delete site	18	delete_site
67	Can add site role	19	add_siterole
68	Can change site role	19	change_siterole
69	Can delete site role	19	delete_siterole
70	Can add site privilege	20	add_siteprivilege
71	Can change site privilege	20	change_siteprivilege
72	Can delete site privilege	20	delete_siteprivilege
73	Can add deployment	21	add_deployment
74	Can change deployment	21	change_deployment
75	Can delete deployment	21	delete_deployment
76	Can add deployment role	22	add_deploymentrole
77	Can change deployment role	22	change_deploymentrole
78	Can delete deployment role	22	delete_deploymentrole
79	Can add deployment privilege	23	add_deploymentprivilege
80	Can change deployment privilege	23	change_deploymentprivilege
81	Can delete deployment privilege	23	delete_deploymentprivilege
82	Can add controller role	24	add_controllerrole
83	Can change controller role	24	change_controllerrole
84	Can delete controller role	24	delete_controllerrole
85	Can add controller	25	add_controller
86	Can change controller	25	change_controller
87	Can delete controller	25	delete_controller
88	Can add site deployment	26	add_sitedeployment
89	Can change site deployment	26	change_sitedeployment
90	Can delete site deployment	26	delete_sitedeployment
91	Can add controller site	27	add_controllersite
92	Can change controller site	27	change_controllersite
93	Can delete controller site	27	delete_controllersite
94	Can add diag	28	add_diag
95	Can change diag	28	change_diag
96	Can delete diag	28	delete_diag
97	Can add dashboard view	29	add_dashboardview
98	Can change dashboard view	29	change_dashboardview
99	Can delete dashboard view	29	delete_dashboardview
100	Can add controller dashboard view	30	add_controllerdashboardview
101	Can change controller dashboard view	30	change_controllerdashboardview
102	Can delete controller dashboard view	30	delete_controllerdashboardview
103	Can add user	31	add_user
104	Can change user	31	change_user
105	Can delete user	31	delete_user
106	Can add user dashboard view	32	add_userdashboardview
107	Can change user dashboard view	32	change_userdashboardview
108	Can delete user dashboard view	32	delete_userdashboardview
109	Can add service class	33	add_serviceclass
110	Can change service class	33	change_serviceclass
111	Can delete service class	33	delete_serviceclass
112	Can add flavor	34	add_flavor
113	Can change flavor	34	change_flavor
114	Can delete flavor	34	delete_flavor
115	Can add image	35	add_image
116	Can change image	35	change_image
117	Can delete image	35	delete_image
118	Can add image deployments	36	add_imagedeployments
119	Can change image deployments	36	change_imagedeployments
120	Can delete image deployments	36	delete_imagedeployments
121	Can add controller images	37	add_controllerimages
122	Can change controller images	37	change_controllerimages
123	Can delete controller images	37	delete_controllerimages
124	Can add slice	38	add_slice
125	Can change slice	38	change_slice
126	Can delete slice	38	delete_slice
127	Can add slice role	39	add_slicerole
128	Can change slice role	39	change_slicerole
129	Can delete slice role	39	delete_slicerole
130	Can add slice privilege	40	add_sliceprivilege
131	Can change slice privilege	40	change_sliceprivilege
132	Can delete slice privilege	40	delete_sliceprivilege
133	Can add controller slice	41	add_controllerslice
134	Can change controller slice	41	change_controllerslice
135	Can delete controller slice	41	delete_controllerslice
136	Can add controller user	42	add_controlleruser
137	Can change controller user	42	change_controlleruser
138	Can delete controller user	42	delete_controlleruser
139	Can add controller site privilege	43	add_controllersiteprivilege
140	Can change controller site privilege	43	change_controllersiteprivilege
141	Can delete controller site privilege	43	delete_controllersiteprivilege
142	Can add controller slice privilege	44	add_controllersliceprivilege
143	Can change controller slice privilege	44	change_controllersliceprivilege
144	Can delete controller slice privilege	44	delete_controllersliceprivilege
145	Can add service resource	45	add_serviceresource
146	Can change service resource	45	change_serviceresource
147	Can delete service resource	45	delete_serviceresource
148	Can add user credential	46	add_usercredential
149	Can change user credential	46	change_usercredential
150	Can delete user credential	46	delete_usercredential
151	Can add site credential	47	add_sitecredential
152	Can change site credential	47	change_sitecredential
153	Can delete site credential	47	delete_sitecredential
154	Can add slice credential	48	add_slicecredential
155	Can change slice credential	48	change_slicecredential
156	Can delete slice credential	48	delete_slicecredential
157	Can add controller credential	49	add_controllercredential
158	Can change controller credential	49	change_controllercredential
159	Can delete controller credential	49	delete_controllercredential
160	Can add node	50	add_node
161	Can change node	50	change_node
162	Can delete node	50	delete_node
163	Can add node label	51	add_nodelabel
164	Can change node label	51	change_nodelabel
165	Can delete node label	51	delete_nodelabel
166	Can add slice tag	52	add_slicetag
167	Can change slice tag	52	change_slicetag
168	Can delete slice tag	52	delete_slicetag
169	Can add instance	53	add_instance
170	Can change instance	53	change_instance
171	Can delete instance	53	delete_instance
172	Can add reservation	54	add_reservation
173	Can change reservation	54	change_reservation
174	Can delete reservation	54	delete_reservation
175	Can add reserved resource	55	add_reservedresource
176	Can change reserved resource	55	change_reservedresource
177	Can delete reserved resource	55	delete_reservedresource
178	Can add network template	56	add_networktemplate
179	Can change network template	56	change_networktemplate
180	Can delete network template	56	delete_networktemplate
181	Can add network	57	add_network
182	Can change network	57	change_network
183	Can delete network	57	delete_network
184	Can add controller network	58	add_controllernetwork
185	Can change controller network	58	change_controllernetwork
186	Can delete controller network	58	delete_controllernetwork
187	Can add network slice	59	add_networkslice
188	Can change network slice	59	change_networkslice
189	Can delete network slice	59	delete_networkslice
190	Can add port	60	add_port
191	Can change port	60	change_port
192	Can delete port	60	delete_port
193	Can add router	61	add_router
194	Can change router	61	change_router
195	Can delete router	61	delete_router
196	Can add network parameter type	62	add_networkparametertype
197	Can change network parameter type	62	change_networkparametertype
198	Can delete network parameter type	62	delete_networkparametertype
199	Can add network parameter	63	add_networkparameter
200	Can change network parameter	63	change_networkparameter
201	Can delete network parameter	63	delete_networkparameter
202	Can add address pool	64	add_addresspool
203	Can change address pool	64	change_addresspool
204	Can delete address pool	64	delete_addresspool
205	Can add account	65	add_account
206	Can change account	65	change_account
207	Can delete account	65	delete_account
208	Can add invoice	66	add_invoice
209	Can change invoice	66	change_invoice
210	Can delete invoice	66	delete_invoice
211	Can add usable object	67	add_usableobject
212	Can change usable object	67	change_usableobject
213	Can delete usable object	67	delete_usableobject
214	Can add payment	68	add_payment
215	Can change payment	68	change_payment
216	Can delete payment	68	delete_payment
217	Can add charge	69	add_charge
218	Can change charge	69	change_charge
219	Can delete charge	69	delete_charge
220	Can add program	70	add_program
221	Can change program	70	change_program
222	Can delete program	70	delete_program
223	Can add HPC Service	75	add_hpcservice
224	Can change HPC Service	75	change_hpcservice
225	Can delete HPC Service	75	delete_hpcservice
226	Can add service provider	76	add_serviceprovider
227	Can change service provider	76	change_serviceprovider
228	Can delete service provider	76	delete_serviceprovider
229	Can add content provider	77	add_contentprovider
230	Can change content provider	77	change_contentprovider
231	Can delete content provider	77	delete_contentprovider
232	Can add origin server	78	add_originserver
233	Can change origin server	78	change_originserver
234	Can delete origin server	78	delete_originserver
235	Can add cdn prefix	79	add_cdnprefix
236	Can change cdn prefix	79	change_cdnprefix
237	Can delete cdn prefix	79	delete_cdnprefix
238	Can add access map	80	add_accessmap
239	Can change access map	80	change_accessmap
240	Can delete access map	80	delete_accessmap
241	Can add site map	81	add_sitemap
242	Can change site map	81	change_sitemap
243	Can delete site map	81	delete_sitemap
244	Can add hpc health check	82	add_hpchealthcheck
245	Can change hpc health check	82	change_hpchealthcheck
246	Can delete hpc health check	82	delete_hpchealthcheck
247	Can add cord subscriber root	11	add_cordsubscriberroot
248	Can change cord subscriber root	11	change_cordsubscriberroot
249	Can delete cord subscriber root	11	delete_cordsubscriberroot
250	Can add vOLT Service	7	add_voltservice
251	Can change vOLT Service	7	change_voltservice
252	Can delete vOLT Service	7	delete_voltservice
253	Can add volt tenant	12	add_volttenant
254	Can change volt tenant	12	change_volttenant
255	Can delete volt tenant	12	delete_volttenant
256	Can add vSG Service	7	add_vsgservice
257	Can change vSG Service	7	change_vsgservice
258	Can delete vSG Service	7	delete_vsgservice
259	Can add vsg tenant	12	add_vsgtenant
260	Can change vsg tenant	12	change_vsgtenant
261	Can delete vsg tenant	12	delete_vsgtenant
262	Can add vBNG Service	7	add_vbngservice
263	Can change vBNG Service	7	change_vbngservice
264	Can delete vBNG Service	7	delete_vbngservice
265	Can add vbng tenant	12	add_vbngtenant
266	Can change vbng tenant	12	change_vbngtenant
267	Can delete vbng tenant	12	delete_vbngtenant
274	Can add ONOS Service	7	add_onosservice
275	Can change ONOS Service	7	change_onosservice
276	Can delete ONOS Service	7	delete_onosservice
277	Can add onos app	12	add_onosapp
278	Can change onos app	12	change_onosapp
279	Can delete onos app	12	delete_onosapp
280	Can add Ceilometer Service	7	add_ceilometerservice
281	Can change Ceilometer Service	7	change_ceilometerservice
282	Can delete Ceilometer Service	7	delete_ceilometerservice
283	Can add monitoring channel	12	add_monitoringchannel
284	Can change monitoring channel	12	change_monitoringchannel
285	Can delete monitoring channel	12	delete_monitoringchannel
286	Can add sFlow Collection Service	7	add_sflowservice
287	Can change sFlow Collection Service	7	change_sflowservice
288	Can delete sFlow Collection Service	7	delete_sflowservice
289	Can add s flow tenant	12	add_sflowtenant
290	Can change s flow tenant	12	change_sflowtenant
291	Can delete s flow tenant	12	delete_sflowtenant
292	Can add Request Router Service	98	add_requestrouterservice
293	Can change Request Router Service	98	change_requestrouterservice
294	Can delete Request Router Service	98	delete_requestrouterservice
295	Can add service map	99	add_servicemap
296	Can change service map	99	change_servicemap
297	Can delete service map	99	delete_servicemap
298	Can add Syndicate Service	100	add_syndicateservice
299	Can change Syndicate Service	100	change_syndicateservice
300	Can delete Syndicate Service	100	delete_syndicateservice
301	Can add syndicate principal	101	add_syndicateprincipal
302	Can change syndicate principal	101	change_syndicateprincipal
303	Can delete syndicate principal	101	delete_syndicateprincipal
304	Can add volume	102	add_volume
305	Can change volume	102	change_volume
306	Can delete volume	102	delete_volume
307	Can add volume access right	103	add_volumeaccessright
308	Can change volume access right	103	change_volumeaccessright
309	Can delete volume access right	103	delete_volumeaccessright
310	Can add slice secret	104	add_slicesecret
311	Can change slice secret	104	change_slicesecret
312	Can delete slice secret	104	delete_slicesecret
313	Can add volume slice	105	add_volumeslice
314	Can change volume slice	105	change_volumeslice
315	Can delete volume slice	105	delete_volumeslice
316	Can add vTR Service	7	add_vtrservice
317	Can change vTR Service	7	change_vtrservice
318	Can delete vTR Service	7	delete_vtrservice
319	Can add vtr tenant	12	add_vtrtenant
320	Can change vtr tenant	12	change_vtrtenant
321	Can delete vtr tenant	12	delete_vtrtenant
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_permission_id_seq', 321, true);


--
-- Data for Name: core_account; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_account (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, site_id) FROM stdin;
\.


--
-- Name: core_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_account_id_seq', 1, false);


--
-- Data for Name: core_addresspool; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_addresspool (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, addresses, inuse) FROM stdin;
\.


--
-- Name: core_addresspool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_addresspool_id_seq', 1, false);


--
-- Data for Name: core_charge; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_charge (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, kind, state, date, amount, "coreHours", account_id, invoice_id, object_id, slice_id) FROM stdin;
\.


--
-- Name: core_charge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_charge_id_seq', 1, false);


--
-- Data for Name: core_controller; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controller (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, backend_type, version, auth_url, admin_user, admin_password, admin_tenant, domain, rabbit_host, rabbit_user, rabbit_password, deployment_id) FROM stdin;
1	2016-04-05 17:41:57.870164+00	2016-04-05 17:41:57.870189+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	CloudLab	OpenStack	Juno	http://sample/v2	admin	adminpassword	admin	Default	\N	\N	\N	1
\.


--
-- Name: core_controller_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controller_id_seq', 1, true);


--
-- Data for Name: core_controllercredential; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllercredential (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, key_id, enc_value, controller_id) FROM stdin;
\.


--
-- Name: core_controllercredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllercredential_id_seq', 1, false);


--
-- Data for Name: core_controllerdashboardview; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllerdashboardview (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, enabled, url, controller_id, "dashboardView_id") FROM stdin;
\.


--
-- Name: core_controllerdashboardview_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllerdashboardview_id_seq', 1, false);


--
-- Data for Name: core_controllerimages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllerimages (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, glance_image_id, controller_id, image_id) FROM stdin;
\.


--
-- Name: core_controllerimages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllerimages_id_seq', 1, false);


--
-- Data for Name: core_controllernetwork; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllernetwork (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, net_id, router_id, subnet_id, subnet, controller_id, network_id) FROM stdin;
\.


--
-- Name: core_controllernetwork_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllernetwork_id_seq', 1, false);


--
-- Data for Name: core_controllerrole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllerrole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
\.


--
-- Name: core_controllerrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllerrole_id_seq', 1, false);


--
-- Data for Name: core_controllersite; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllersite (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, tenant_id, controller_id, site_id) FROM stdin;
\.


--
-- Name: core_controllersite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllersite_id_seq', 1, false);


--
-- Data for Name: core_controllersiteprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllersiteprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, controller_id, site_privilege_id) FROM stdin;
\.


--
-- Name: core_controllersiteprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllersiteprivilege_id_seq', 1, false);


--
-- Data for Name: core_controllerslice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllerslice (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, tenant_id, controller_id, slice_id) FROM stdin;
\.


--
-- Name: core_controllerslice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllerslice_id_seq', 1, false);


--
-- Data for Name: core_controllersliceprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controllersliceprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, controller_id, slice_privilege_id) FROM stdin;
\.


--
-- Name: core_controllersliceprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controllersliceprivilege_id_seq', 1, false);


--
-- Data for Name: core_controlleruser; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_controlleruser (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, kuser_id, controller_id, user_id) FROM stdin;
\.


--
-- Name: core_controlleruser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_controlleruser_id_seq', 1, false);


--
-- Data for Name: core_dashboardview; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_dashboardview (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, url, enabled) FROM stdin;
--1	2015-02-17 22:06:38.953+00	2015-02-17 22:06:38.953+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	xsh	template:xsh	t
2	2015-02-17 22:06:39.011+00	2015-02-17 22:06:39.011+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Customize	template:customize	t
3	2015-02-17 22:06:39.069+00	2015-02-17 22:06:39.244+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Tenant	template:xosTenant	t
4	2015-02-17 22:06:39.302+00	2015-02-17 22:06:39.302+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Developer	template:xosDeveloper_datatables	t
5	2016-04-05 17:42:11.341605+00	2016-04-05 17:42:11.341634+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Customer Care	template:xosDiagnostic	t
6	2016-04-05 18:46:36.638199+00	2016-04-05 18:46:36.638233+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	truckroll	template:xosTruckroll	t
\.


--
-- Data for Name: core_dashboardview_deployments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_dashboardview_deployments (id, dashboardview_id, deployment_id) FROM stdin;
1	3	1
\.


--
-- Name: core_dashboardview_deployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_dashboardview_deployments_id_seq', 1, true);


--
-- Name: core_dashboardview_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_dashboardview_id_seq', 6, true);


--
-- Data for Name: core_deployment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_deployment (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, "accessControl") FROM stdin;
1	2015-02-17 22:06:37.789+00	2016-04-05 17:41:57.865591+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	MyDeployment	allow all
\.


--
-- Name: core_deployment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_deployment_id_seq', 1, true);


--
-- Data for Name: core_deploymentprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_deploymentprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, deployment_id, role_id, user_id) FROM stdin;
\.


--
-- Name: core_deploymentprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_deploymentprivilege_id_seq', 1, false);


--
-- Data for Name: core_deploymentrole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_deploymentrole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
1	2015-02-17 22:06:38.894+00	2015-02-17 22:06:38.894+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	admin
\.


--
-- Name: core_deploymentrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_deploymentrole_id_seq', 1, true);


--
-- Data for Name: core_diag; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_diag (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name) FROM stdin;
\.


--
-- Name: core_diag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_diag_id_seq', 1, false);


--
-- Data for Name: core_flavor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_flavor (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, flavor, "order", "default") FROM stdin;
1	2015-02-17 22:06:38.095+00	2015-02-17 22:06:38.236+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	m1.small	\N	m1.small	0	f
2	2015-02-17 22:06:38.287+00	2015-02-17 22:06:38.394+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	m1.medium	\N	m1.medium	0	f
3	2015-02-17 22:06:38.445+00	2015-02-17 22:06:38.561+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	m1.large	\N	m1.large	0	f
\.


--
-- Data for Name: core_flavor_deployments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_flavor_deployments (id, flavor_id, deployment_id) FROM stdin;
1	1	1
2	2	1
3	3	1
\.


--
-- Name: core_flavor_deployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_flavor_deployments_id_seq', 3, true);


--
-- Name: core_flavor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_flavor_id_seq', 3, true);


--
-- Data for Name: core_image; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_image (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, kind, disk_format, container_format, path, tag) FROM stdin;
1	2016-04-05 17:41:57.84418+00	2016-04-05 17:41:57.844213+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	trusty-server-multi-nic	vm	QCOW2	BARE	\N	\N
2	2016-04-05 17:42:10.875232+00	2016-04-05 17:42:10.87526+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	docker-vcpe	container	na	na	andybavier/docker-vcpe	develop
\.


--
-- Name: core_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_image_id_seq', 2, true);


--
-- Data for Name: core_imagedeployments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_imagedeployments (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, deployment_id, image_id) FROM stdin;
1	2016-04-05 17:41:57.855026+00	2016-04-05 17:41:57.855053+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	1	1
\.


--
-- Name: core_imagedeployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_imagedeployments_id_seq', 1, true);


--
-- Data for Name: core_instance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_instance (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, instance_id, instance_uuid, name, instance_name, ip, "numberCores", "userData", isolation, volumes, creator_id, deployment_id, flavor_id, image_id, node_id, parent_id, slice_id) FROM stdin;
1	2016-04-05 17:42:11.041143+00	2016-04-05 17:42:11.041177+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	mysite_vcpe	\N	\N	0	\N	vm	/etc/dnsmasq.d,/etc/ufw	1	1	1	1	1	\N	1
2	2016-04-05 17:42:11.143845+00	2016-04-05 17:42:11.505705+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	onos_app_1	\N	\N	0	\N	vm	\N	1	1	1	1	2	\N	5
3	2016-04-05 17:42:11.180193+00	2016-04-05 17:42:11.508623+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	client1	\N	\N	0	\N	vm	\N	1	1	1	1	1	\N	4
4	2016-04-05 17:42:11.24868+00	2016-04-05 17:42:11.512938+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	onos_app_2	\N	\N	0	\N	vm	\N	1	1	1	1	2	\N	6
5	2016-04-05 17:42:11.32255+00	2016-04-05 17:42:11.516734+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	ovs_volt	\N	\N	0	\N	vm	\N	1	1	1	1	1	\N	3
6	2016-04-05 17:42:11.336187+00	2016-04-05 17:42:11.519581+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	ovs_vbng	\N	\N	0	\N	vm	\N	1	1	1	1	2	\N	2
\.


--
-- Name: core_instance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_instance_id_seq', 6, true);


--
-- Data for Name: core_invoice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_invoice (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, date, account_id) FROM stdin;
\.


--
-- Name: core_invoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_invoice_id_seq', 1, false);


--
-- Data for Name: core_network; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_network (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, subnet, ports, labels, guaranteed_bandwidth, permit_all_slices, topology_parameters, controller_url, controller_parameters, network_id, router_id, subnet_id, autoconnect, owner_id, template_id) FROM stdin;
1	2016-04-05 17:42:10.926943+00	2016-04-05 17:42:10.926967+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	wan_network		\N	\N	0	t	\N	\N	\N	\N	\N	\N	f	1	1
2	2016-04-05 17:42:10.963196+00	2016-04-05 17:42:10.963223+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	lan_network		\N	\N	0	t	\N	\N	\N	\N	\N	\N	f	1	1
3	2016-04-05 17:42:11.188082+00	2016-04-05 17:42:11.188111+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	public_network		\N	\N	0	t	\N	\N	\N	\N	\N	\N	f	2	5
4	2016-04-05 17:42:11.370317+00	2016-04-05 17:42:11.370343+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	subscriber_network		\N	\N	0	t	\N	\N	\N	\N	\N	\N	f	3	1
\.


--
-- Name: core_network_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_network_id_seq', 4, true);


--
-- Data for Name: core_network_permitted_slices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_network_permitted_slices (id, network_id, slice_id) FROM stdin;
\.


--
-- Name: core_network_permitted_slices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_network_permitted_slices_id_seq', 1, false);


--
-- Data for Name: core_networkparameter; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_networkparameter (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, value, object_id, content_type_id, parameter_id) FROM stdin;
1	2016-04-05 17:42:11.062812+00	2016-04-05 17:42:11.062838+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	432	1	60	5
2	2016-04-05 17:42:11.068024+00	2016-04-05 17:42:11.068048+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	222	1	60	6
3	2016-04-05 17:42:11.071633+00	2016-04-05 17:42:11.071645+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	stag-222	1	60	4
\.


--
-- Name: core_networkparameter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_networkparameter_id_seq', 3, true);


--
-- Data for Name: core_networkparametertype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_networkparametertype (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description) FROM stdin;
1	2016-04-05 17:42:09.268578+00	2016-04-05 17:42:09.26861+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	bridge	
2	2016-04-05 17:42:09.271808+00	2016-04-05 17:42:09.271835+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	next_hop	
3	2016-04-05 17:42:09.274484+00	2016-04-05 17:42:09.27451+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	device	
4	2016-04-05 17:42:09.276919+00	2016-04-05 17:42:09.276946+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	neutron_port_name	
5	2016-04-05 17:42:09.279956+00	2016-04-05 17:42:09.279984+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	c_tag	
6	2016-04-05 17:42:09.282047+00	2016-04-05 17:42:09.282073+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	s_tag	
\.


--
-- Name: core_networkparametertype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_networkparametertype_id_seq', 6, true);


--
-- Data for Name: core_networkslice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_networkslice (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, network_id, slice_id) FROM stdin;
1	2016-04-05 17:42:10.934539+00	2016-04-05 17:42:10.93457+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	1	1
2	2016-04-05 17:42:10.948028+00	2016-04-05 17:42:10.948057+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	1	2
3	2016-04-05 17:42:10.967241+00	2016-04-05 17:42:10.967274+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	2	1
4	2016-04-05 17:42:10.971959+00	2016-04-05 17:42:10.971989+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	2	3
5	2016-04-05 17:42:11.193081+00	2016-04-05 17:42:11.193111+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	3	2
6	2016-04-05 17:42:11.37604+00	2016-04-05 17:42:11.376067+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	4	3
7	2016-04-05 17:42:11.380003+00	2016-04-05 17:42:11.380064+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	4	4
\.


--
-- Name: core_networkslice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_networkslice_id_seq', 7, true);


--
-- Data for Name: core_networktemplate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_networktemplate (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, guaranteed_bandwidth, visibility, translation, access, shared_network_name, shared_network_id, topology_kind, controller_kind) FROM stdin;
3	2015-02-17 22:06:39.536+00	2015-02-17 22:06:39.536+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Public dedicated IPv4	Connect a instance to the public network	0	public	none	\N	ext-net	\N	bigswitch	\N
2	2015-02-17 22:06:39.477+00	2016-04-05 17:41:57.912367+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Public shared IPv4	Connect a instance to the public network	0	private	NAT	\N	nat-net	\N	bigswitch	\N
1	2015-02-17 22:06:39.419+00	2016-04-05 17:42:10.920852+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Private	A private virtual network	0	private	none	\N	\N	\N	bigswitch	\N
4	2016-04-05 17:42:10.950692+00	2016-04-05 17:42:10.950719+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Private-Direct	\N	0	private	none	direct	\N	\N	bigswitch	\N
5	2016-04-05 17:42:11.11517+00	2016-04-05 17:42:11.115197+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Public network hack	\N	0	private	NAT	\N	tun0-net	\N	bigswitch	\N
6	2016-04-05 17:42:11.309984+00	2016-04-05 17:42:11.310025+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Private-Indirect	\N	0	private	none	indirect	\N	\N	bigswitch	\N
\.


--
-- Name: core_networktemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_networktemplate_id_seq', 6, true);


--
-- Data for Name: core_node; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_node (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, site_id, site_deployment_id) FROM stdin;
1	2016-04-05 17:41:57.898724+00	2016-04-05 17:41:57.898751+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	node2.opencloud.us	1	1
2	2016-04-05 17:41:57.908261+00	2016-04-05 17:41:57.908283+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	t	node1.opencloud.us	1	1
\.


--
-- Name: core_node_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_node_id_seq', 2, true);


--
-- Data for Name: core_nodelabel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_nodelabel (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name) FROM stdin;
\.


--
-- Name: core_nodelabel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_nodelabel_id_seq', 1, false);


--
-- Data for Name: core_nodelabel_node; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_nodelabel_node (id, nodelabel_id, node_id) FROM stdin;
\.


--
-- Name: core_nodelabel_node_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_nodelabel_node_id_seq', 1, false);


--
-- Data for Name: core_payment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_payment (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, amount, date, account_id) FROM stdin;
\.


--
-- Name: core_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_payment_id_seq', 1, false);


--
-- Data for Name: core_port; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_port (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, ip, port_id, mac, xos_created, instance_id, network_id) FROM stdin;
1	2016-04-05 17:42:11.049219+00	2016-04-05 17:42:11.073126+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	\N	\N	f	1	2
\.


--
-- Name: core_port_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_port_id_seq', 1, true);


--
-- Data for Name: core_program; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_program (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, kind, command, contents, output, messages, status, owner_id) FROM stdin;
\.


--
-- Name: core_program_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_program_id_seq', 1, false);


--
-- Data for Name: core_project; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_project (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name) FROM stdin;
\.


--
-- Name: core_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_project_id_seq', 1, false);


--
-- Data for Name: core_reservation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_reservation (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, "startTime", duration, slice_id) FROM stdin;
\.


--
-- Name: core_reservation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_reservation_id_seq', 1, false);


--
-- Data for Name: core_reservedresource; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_reservedresource (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, quantity, instance_id, "reservationSet_id", resource_id) FROM stdin;
\.


--
-- Name: core_reservedresource_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_reservedresource_id_seq', 1, false);


--
-- Data for Name: core_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_role (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_type, role, description, content_type_id) FROM stdin;
\.


--
-- Name: core_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_role_id_seq', 1, false);


--
-- Data for Name: core_router; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_router (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, owner_id) FROM stdin;
\.


--
-- Name: core_router_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_router_id_seq', 1, false);


--
-- Data for Name: core_router_networks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_router_networks (id, router_id, network_id) FROM stdin;
\.


--
-- Name: core_router_networks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_router_networks_id_seq', 1, false);


--
-- Data for Name: core_router_permittedNetworks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY "core_router_permittedNetworks" (id, router_id, network_id) FROM stdin;
\.


--
-- Name: core_router_permittedNetworks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"core_router_permittedNetworks_id_seq"', 1, false);


--
-- Data for Name: core_service; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_service (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, description, enabled, kind, name, "versionNumber", published, view_url, icon_url, public_key, private_key_fn, service_specific_id, service_specific_attribute) FROM stdin;
1	2016-04-05 17:42:10.879967+00	2016-04-05 17:42:10.879992+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	vBNG	service_vbng		t	/admin/cord/vbngservice/$id$/	\N	\N	\N	\N	\N
2	2016-04-05 17:42:10.891972+00	2016-04-05 17:42:10.892005+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	vCPE	service_vsg		t	/admin/cord/vsgservice/$id$/	\N	\N	\N	\N	{"backend_network_label": "hpc_client"}
3	2016-04-05 17:42:10.974546+00	2016-04-05 17:42:10.97457+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	vOLT	service_volt		t	/admin/cord/voltservice/$id$/	\N	\N	\N	\N	\N
4	2016-04-05 17:42:11.119371+00	2016-04-05 17:42:11.119403+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	onos	service_ONOS_vBNG		t	/admin/onos/onosservice/$id$/	\N	\N	\N	\N	{"no_container": false}
5	2016-04-05 17:42:11.15434+00	2016-04-05 17:42:11.154366+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	onos	service_ONOS_vOLT		t	/admin/onos/onosservice/$id$/	\N	\N	\N	\N	{"no_container": false}
6	2016-04-05 17:42:11.183911+00	2016-04-05 17:42:11.183952+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	t	vTR	service_vtr		t	/admin/vtr/vtrservice/$id$/	\N	\N	\N	\N	\N
\.


--
-- Name: core_service_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_service_id_seq', 6, true);


--
-- Data for Name: core_serviceattribute; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_serviceattribute (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, value, service_id) FROM stdin;
1	2016-04-05 17:42:11.158787+00	2016-04-05 17:42:11.158814+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	rest_onos/v1/network/configuration/	{\n  "devices" : {\n    "of:0000000000000001" : {\n      "accessDevice" : {\n        "uplink" : "2",\n        "vlan"   : "222",\n        "defaultVlan" : "1"\n      },\n      "basic" : {\n        "driver" : "pmc-olt"\n      }\n    }\n  }\n}\n	5
\.


--
-- Name: core_serviceattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_serviceattribute_id_seq', 1, true);


--
-- Data for Name: core_serviceclass; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_serviceclass (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, commitment, "membershipFee", "membershipFeeMonths", "upgradeRequiresApproval") FROM stdin;
1	2015-02-17 22:06:39.361+00	2015-02-17 22:06:39.361+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	Best Effort	Best Effort	365	0	12	f
\.


--
-- Name: core_serviceclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_serviceclass_id_seq', 1, true);


--
-- Data for Name: core_serviceclass_upgradeFrom; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY "core_serviceclass_upgradeFrom" (id, from_serviceclass_id, to_serviceclass_id) FROM stdin;
\.


--
-- Name: core_serviceclass_upgradeFrom_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"core_serviceclass_upgradeFrom_id_seq"', 1, false);


--
-- Data for Name: core_serviceprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_serviceprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, service_id, user_id) FROM stdin;
\.


--
-- Name: core_serviceprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_serviceprivilege_id_seq', 1, false);


--
-- Data for Name: core_serviceresource; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_serviceresource (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, "maxUnitsDeployment", "maxUnitsNode", "maxDuration", "bucketInRate", "bucketMaxSize", cost, "calendarReservable", "serviceClass_id") FROM stdin;
\.


--
-- Name: core_serviceresource_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_serviceresource_id_seq', 1, false);


--
-- Data for Name: core_servicerole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_servicerole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
\.


--
-- Name: core_servicerole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_servicerole_id_seq', 1, false);


--
-- Data for Name: core_site; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_site (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, site_url, enabled, hosts_nodes, hosts_users, location, longitude, latitude, login_base, is_public, abbreviated_name) FROM stdin;
1	2015-02-17 22:06:37.837+00	2016-04-05 17:42:10.798018+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite	http://opencloud.us/	t	t	t	0,0	\N	\N	mysite	t	mysite
\.


--
-- Name: core_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_site_id_seq', 1, true);


--
-- Data for Name: core_sitecredential; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_sitecredential (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, key_id, enc_value, site_id) FROM stdin;
\.


--
-- Name: core_sitecredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_sitecredential_id_seq', 1, false);


--
-- Data for Name: core_sitedeployment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_sitedeployment (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, availability_zone, controller_id, deployment_id, site_id) FROM stdin;
1	2015-02-17 22:06:37.893+00	2016-04-05 17:41:57.888081+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	\N	1	1	1
\.


--
-- Name: core_sitedeployment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_sitedeployment_id_seq', 1, true);


--
-- Data for Name: core_siteprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_siteprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, site_id, user_id) FROM stdin;
\.


--
-- Name: core_siteprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_siteprivilege_id_seq', 1, false);


--
-- Data for Name: core_siterole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_siterole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
1	2015-02-17 22:06:38.62+00	2015-02-17 22:06:38.62+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	admin
2	2015-02-17 22:06:38.669+00	2015-02-17 22:06:38.67+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	pi
3	2015-02-17 22:06:38.73+00	2015-02-17 22:06:38.731+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	tech
\.


--
-- Name: core_siterole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_siterole_id_seq', 3, true);


--
-- Data for Name: core_slice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_slice (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, enabled, omf_friendly, description, slice_url, max_instances, network, exposed_ports, mount_data_sets, default_isolation, creator_id, default_flavor_id, default_image_id, service_id, "serviceClass_id", site_id) FROM stdin;
1	2016-04-05 17:42:10.909075+00	2016-04-05 17:42:10.909102+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_vcpe	t	f			10	\N	\N	GenBank	vm	1	\N	\N	2	1	1
2	2016-04-05 17:42:10.915949+00	2016-04-05 17:42:10.915976+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_vbng	t	f			10	\N	\N	GenBank	vm	1	\N	\N	\N	1	1
3	2016-04-05 17:42:10.958832+00	2016-04-05 17:42:10.958858+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_volt	t	f			10	\N	\N	GenBank	vm	1	\N	\N	\N	1	1
4	2016-04-05 17:42:11.112233+00	2016-04-05 17:42:11.112263+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_clients	t	f			10	\N	\N	GenBank	vm	1	\N	\N	\N	1	1
5	2016-04-05 17:42:11.127649+00	2016-04-05 17:42:11.127678+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_onos_vbng	t	f			10	\N	\N	GenBank	vm	1	\N	\N	4	1	1
6	2016-04-05 17:42:11.167287+00	2016-04-05 17:42:11.167313+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	mysite_onos_volt	t	f			10	\N	\N	GenBank	vm	1	\N	\N	5	1	1
\.


--
-- Name: core_slice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_slice_id_seq', 6, true);


--
-- Data for Name: core_slicecredential; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_slicecredential (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, key_id, enc_value, slice_id) FROM stdin;
\.


--
-- Name: core_slicecredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_slicecredential_id_seq', 1, false);


--
-- Data for Name: core_sliceprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_sliceprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, slice_id, user_id) FROM stdin;
\.


--
-- Name: core_sliceprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_sliceprivilege_id_seq', 1, false);


--
-- Data for Name: core_slicerole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_slicerole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
1	2015-02-17 22:06:38.778+00	2015-02-17 22:06:38.778+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	admin
2	2015-02-17 22:06:38.836+00	2015-02-17 22:06:38.836+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	access
\.


--
-- Name: core_slicerole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_slicerole_id_seq', 2, true);


--
-- Data for Name: core_slicetag; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_slicetag (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, value, slice_id) FROM stdin;
\.


--
-- Name: core_slicetag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_slicetag_id_seq', 1, false);


--
-- Data for Name: core_tag; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tag (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, value, object_id, content_type_id, service_id) FROM stdin;
1	2016-04-05 17:42:11.08141+00	2016-04-05 17:42:11.081432+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	s_tag	222	1	53	2
\.


--
-- Name: core_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tag_id_seq', 1, true);


--
-- Data for Name: core_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tenant (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, kind, service_specific_id, service_specific_attribute, connect_method, provider_service_id, subscriber_root_id, subscriber_service_id, subscriber_tenant_id, subscriber_user_id) FROM stdin;
1	2016-04-05 17:42:10.897527+00	2016-04-05 17:42:10.897558+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	coarse	\N	\N	na	1	\N	2	\N	\N
2	2016-04-05 17:42:10.978184+00	2016-04-05 17:42:10.978207+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	coarse	\N	\N	na	2	\N	3	\N	\N
3	2016-04-05 17:42:10.995794+00	2016-04-05 17:42:10.995832+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	vOLT	123	{"creator_id": 1, "c_tag": "432", "s_tag": "222"}	na	3	1	\N	\N	\N
5	2016-04-05 17:42:11.086763+00	2016-04-05 17:42:11.086785+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	vBNG	\N	\N	na	1	\N	\N	4	\N
6	2016-04-05 17:42:11.224376+00	2016-04-05 17:42:11.22441+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	onos	\N	{"creator_id": 1, "dependencies": "org.onosproject.proxyarp, org.onosproject.virtualbng, org.onosproject.openflow, org.onosproject.fwd", "name": "vBNG_ONOS_app"}	na	4	\N	1	\N	\N
7	2016-04-05 17:42:11.359136+00	2016-04-05 17:42:11.359169+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	onos	\N	{"creator_id": 1, "dependencies": "org.onosproject.openflow-base, org.onosproject.olt, org.ciena.onos.ext_notifier, org.ciena.onos.volt_event_publisher", "name": "vOLT_ONOS_app", "install_dependencies": "onos-ext-notifier-1.0-SNAPSHOT.oar, onos-ext-volt-event-publisher-1.0-SNAPSHOT.oar"}	na	5	\N	3	\N	\N
4	2016-04-05 17:42:11.006459+00	2016-04-05 21:11:13.789553+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	vCPE	\N	{"instance_id": 1, "creator_id": 1}	na	2	\N	\N	3	\N
\.


--
-- Name: core_tenant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tenant_id_seq', 7, true);


--
-- Data for Name: core_tenantattribute; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tenantattribute (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, value, tenant_id) FROM stdin;
1	2016-04-05 17:42:11.232458+00	2016-04-05 17:42:11.23249+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	config_network-cfg.json	{\n  "ports" : {\n    "of:0000000000000001/1" : {\n      "interfaces" : [\n        {\n          "ips"  : [ "10.0.1.253/24" ],\n          "mac"  : "00:00:00:00:00:99"\n        }\n      ]\n    },\n    "of:0000000000000001/2" : {\n      "interfaces" : [\n        {\n          "ips"  : [ "10.254.0.2/24" ],\n          "mac"  : "00:00:00:00:00:98"\n        }\n      ]\n    }\n  }\n}\n	6
2	2016-04-05 17:42:11.366036+00	2016-04-05 17:42:11.366073+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	component_config	{\n   "org.ciena.onos.ext_notifier.KafkaNotificationBridge":{\n      "rabbit.user": "<rabbit_user>",\n      "rabbit.password": "<rabbit_password>",\n      "rabbit.host": "<rabbit_host>",\n      "publish.rabbit": "true",\n      "volt.events.rabbit.topic": "notifications.info",\n      "volt.events.rabbit.exchange": "voltlistener",\n      "volt.events.opaque.info": "{project_id: <keystone_tenant_id>, user_id: <keystone_user_id>}",\n      "publish.volt.events": "true"\n   }\n}\n	7
\.


--
-- Name: core_tenantattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tenantattribute_id_seq', 2, true);


--
-- Data for Name: core_tenantroot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tenantroot (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, kind, name, service_specific_attribute, service_specific_id) FROM stdin;
1	2016-04-05 17:42:10.85283+00	2016-04-05 21:11:13.773087+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	CordSubscriberRoot	My House	{"status": "enabled", "cdn_enable": false, "users": [{"mac": "01:02:03:04:05:06", "level": "PG_13", "id": 0, "name": "Mom's PC"}, {"mac": "34:36:3B:C9:B6:A6", "id": 1, "name": "Jill's Laptop", "level": "PG_13"}, {"mac": "68:5B:35:9D:91:D5", "level": "PG_13", "id": 2, "name": "Jack's Laptop"}, {"mac": "90:E2:BA:82:F9:75", "id": 3, "name": "Dad's PC", "level": "PG_13"}], "downlink_speed": 1000000000, "url_filter_level": "R", "uplink_speed": 1000000000, "enable_uverse": false, "firewall_enable": false, "url_filter_enable": false}	123
\.


--
-- Name: core_tenantroot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tenantroot_id_seq', 1, true);


--
-- Data for Name: core_tenantrootprivilege; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tenantrootprivilege (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role_id, tenant_root_id, user_id) FROM stdin;
1	2016-04-05 17:42:10.864854+00	2016-04-05 17:42:10.864879+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	1	1	2
\.


--
-- Name: core_tenantrootprivilege_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tenantrootprivilege_id_seq', 1, true);


--
-- Data for Name: core_tenantrootrole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_tenantrootrole (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, role) FROM stdin;
1	2016-04-05 17:42:10.859991+00	2016-04-05 17:42:10.860017+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	admin
\.


--
-- Name: core_tenantrootrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_tenantrootrole_id_seq', 1, true);


--
-- Data for Name: core_usableobject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_usableobject (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name) FROM stdin;
\.


--
-- Name: core_usableobject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_usableobject_id_seq', 1, false);


--
-- Data for Name: core_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_user (id, password, last_login, email, username, firstname, lastname, phone, user_url, public_key, is_active, is_admin, is_staff, is_readonly, is_registering, is_appuser, login_page, created, updated, enacted, policed, backend_status, deleted, write_protect, timezone, site_id) FROM stdin;
2	pbkdf2_sha256$12000$Oc7yu5OUSNRK$lV5m9OLtVPWAfog5aX0CHYfh4gyLYj1iSvRq+wk8kTk=	2016-04-05 17:42:10.803373+00	johndoe@myhouse.com	johndoe@myhouse.com	john	doe	\N	\N	\N	t	f	t	f	f	f	\N	2016-04-05 17:42:10.844525+00	2016-04-05 17:42:10.844548+00	\N	\N	Provisioning in progress	f	f	America/New_York	1
1	pbkdf2_sha256$12000$Qufx9iqtaYma$xs0YurPOcj9qYQna/Qrb3K+im9Yr2XEVr0J4Kqek7AE=	2016-04-05 17:42:16.66369+00	padmin@vicci.org	padmin@vicci.org	XOS	admin	\N	\N	\N	t	t	t	f	f	f	\N	2015-02-17 22:06:38.059+00	2016-04-05 17:42:11.387962+00	\N	\N	Provisioning in progress	f	f	America/New_York	1
\.


--
-- Name: core_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_user_id_seq', 2, true);


--
-- Data for Name: core_usercredential; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_usercredential (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, key_id, enc_value, user_id) FROM stdin;
\.


--
-- Name: core_usercredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_usercredential_id_seq', 1, false);


--
-- Data for Name: core_userdashboardview; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY core_userdashboardview (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, "order", "dashboardView_id", user_id) FROM stdin;
2	2016-04-05 18:46:44.099329+00	2016-04-05 18:46:44.099362+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	0	5	1
3	2016-04-05 18:46:44.101231+00	2016-04-05 18:46:44.101257+00	\N	\N	{}	0 - Provisioning in progress	f	f	f	f	1	6	1
\.


--
-- Name: core_userdashboardview_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('core_userdashboardview_id_seq', 3, true);


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2016-04-05 18:46:36.64407+00	6	truckroll	1		29	1
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, true);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	permission	auth	permission
2	group	auth	group
3	content type	contenttypes	contenttype
4	session	sessions	session
5	log entry	admin	logentry
6	project	core	project
7	service	core	service
8	service attribute	core	serviceattribute
9	service role	core	servicerole
10	service privilege	core	serviceprivilege
11	tenant root	core	tenantroot
12	tenant	core	tenant
13	tenant attribute	core	tenantattribute
14	tenant root role	core	tenantrootrole
15	tenant root privilege	core	tenantrootprivilege
16	tag	core	tag
17	role	core	role
18	site	core	site
19	site role	core	siterole
20	site privilege	core	siteprivilege
21	deployment	core	deployment
22	deployment role	core	deploymentrole
23	deployment privilege	core	deploymentprivilege
24	controller role	core	controllerrole
25	controller	core	controller
26	site deployment	core	sitedeployment
27	controller site	core	controllersite
28	diag	core	diag
29	dashboard view	core	dashboardview
30	controller dashboard view	core	controllerdashboardview
31	user	core	user
32	user dashboard view	core	userdashboardview
33	service class	core	serviceclass
34	flavor	core	flavor
35	image	core	image
36	image deployments	core	imagedeployments
37	controller images	core	controllerimages
38	slice	core	slice
39	slice role	core	slicerole
40	slice privilege	core	sliceprivilege
41	controller slice	core	controllerslice
42	controller user	core	controlleruser
43	controller site privilege	core	controllersiteprivilege
44	controller slice privilege	core	controllersliceprivilege
45	service resource	core	serviceresource
46	user credential	core	usercredential
47	site credential	core	sitecredential
48	slice credential	core	slicecredential
49	controller credential	core	controllercredential
50	node	core	node
51	node label	core	nodelabel
52	slice tag	core	slicetag
53	instance	core	instance
54	reservation	core	reservation
55	reserved resource	core	reservedresource
56	network template	core	networktemplate
57	network	core	network
58	controller network	core	controllernetwork
59	network slice	core	networkslice
60	port	core	port
61	router	core	router
62	network parameter type	core	networkparametertype
63	network parameter	core	networkparameter
64	address pool	core	addresspool
65	account	core	account
66	invoice	core	invoice
67	usable object	core	usableobject
68	payment	core	payment
69	charge	core	charge
70	program	core	program
71	subscriber	core	subscriber
72	provider	core	provider
73	tenant with container	core	tenantwithcontainer
74	coarse tenant	core	coarsetenant
75	HPC Service	hpc	hpcservice
76	service provider	hpc	serviceprovider
77	content provider	hpc	contentprovider
78	origin server	hpc	originserver
79	cdn prefix	hpc	cdnprefix
80	access map	hpc	accessmap
81	site map	hpc	sitemap
82	hpc health check	hpc	hpchealthcheck
83	vBNG Service	cord	vbngservice
84	vsg tenant	cord	vsgtenant
85	volt tenant	cord	volttenant
86	vbng tenant	cord	vbngtenant
87	cord subscriber root	cord	cordsubscriberroot
88	vOLT Service	cord	voltservice
89	vSG Service	cord	vsgservice
92	ONOS Service	onos	onosservice
93	onos app	onos	onosapp
94	s flow tenant	ceilometer	sflowtenant
95	Ceilometer Service	ceilometer	ceilometerservice
96	sFlow Collection Service	ceilometer	sflowservice
97	monitoring channel	ceilometer	monitoringchannel
98	Request Router Service	requestrouter	requestrouterservice
99	service map	requestrouter	servicemap
100	Syndicate Service	syndicate_storage	syndicateservice
101	syndicate principal	syndicate_storage	syndicateprincipal
102	volume	syndicate_storage	volume
103	volume access right	syndicate_storage	volumeaccessright
104	slice secret	syndicate_storage	slicesecret
105	volume slice	syndicate_storage	volumeslice
106	vtr tenant	vtr	vtrtenant
107	vTR Service	vtr	vtrservice
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_content_type_id_seq', 107, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2016-04-05 17:41:25.364327+00
2	core	0001_initial	2016-04-05 17:41:45.947411+00
3	admin	0001_initial	2016-04-05 17:41:46.336359+00
4	auth	0001_initial	2016-04-05 17:41:46.384468+00
5	ceilometer	0001_initial	2016-04-05 17:41:46.659809+00
6	cord	0001_initial	2016-04-05 17:41:46.862406+00
8	hpc	0001_initial	2016-04-05 17:41:50.450946+00
9	onos	0001_initial	2016-04-05 17:41:50.637887+00
10	requestrouter	0001_initial	2016-04-05 17:41:51.319325+00
11	sessions	0001_initial	2016-04-05 17:41:51.331342+00
12	syndicate_storage	0001_initial	2016-04-05 17:41:53.077489+00
13	vtr	0001_initial	2016-04-05 17:41:53.270146+00
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_migrations_id_seq', 13, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
7ppjuoyfejs1zo7q3rn47a6sciqpqjxs	ZTMzOTkxNDYwNzJiZGI4NDdjMTM2YmU1ZDNjNmI2N2Y0NWM2MDdlMTp7Il9hdXRoX3VzZXJfaGFzaCI6IjVkMTdkNWYxYmQxYjNmOTJhMWJiYzc3YzE0NDNlMzNhNDRiNjQ0YzQiLCJhdXRoIjp7InVzZXJuYW1lIjoicGFkbWluQHZpY2NpLm9yZyIsInBhc3N3b3JkIjoibGV0bWVpbiJ9LCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOjF9	2016-04-19 17:42:16.666323+00
\.


--
-- Data for Name: hpc_accessmap; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_accessmap (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, map, "contentProvider_id") FROM stdin;
\.


--
-- Name: hpc_accessmap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_accessmap_id_seq', 1, false);


--
-- Data for Name: hpc_cdnprefix; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_cdnprefix (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, cdn_prefix_id, prefix, description, enabled, "contentProvider_id", "defaultOriginServer_id") FROM stdin;
\.


--
-- Name: hpc_cdnprefix_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_cdnprefix_id_seq', 1, false);


--
-- Data for Name: hpc_contentprovider; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_contentprovider (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, content_provider_id, name, enabled, description, "serviceProvider_id") FROM stdin;
\.


--
-- Name: hpc_contentprovider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_contentprovider_id_seq', 1, false);


--
-- Data for Name: hpc_contentprovider_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_contentprovider_users (id, contentprovider_id, user_id) FROM stdin;
\.


--
-- Name: hpc_contentprovider_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_contentprovider_users_id_seq', 1, false);


--
-- Data for Name: hpc_hpchealthcheck; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_hpchealthcheck (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, kind, resource_name, result_contains, result_min_size, result_max_size, "hpcService_id") FROM stdin;
\.


--
-- Name: hpc_hpchealthcheck_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_hpchealthcheck_id_seq', 1, false);


--
-- Data for Name: hpc_hpcservice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_hpcservice (service_ptr_id, cmi_hostname, hpc_port80, watcher_hpc_network, watcher_dnsdemux_network, watcher_dnsredir_network) FROM stdin;
\.


--
-- Data for Name: hpc_originserver; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_originserver (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, origin_server_id, url, authenticated, enabled, protocol, redirects, description, "contentProvider_id") FROM stdin;
\.


--
-- Name: hpc_originserver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_originserver_id_seq', 1, false);


--
-- Data for Name: hpc_serviceprovider; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_serviceprovider (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, service_provider_id, name, description, enabled, "hpcService_id") FROM stdin;
\.


--
-- Name: hpc_serviceprovider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_serviceprovider_id_seq', 1, false);


--
-- Data for Name: hpc_sitemap; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY hpc_sitemap (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, map, map_id, "cdnPrefix_id", "contentProvider_id", "hpcService_id", "serviceProvider_id") FROM stdin;
\.


--
-- Name: hpc_sitemap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('hpc_sitemap_id_seq', 1, false);


--
-- Data for Name: requestrouter_requestrouterservice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY requestrouter_requestrouterservice (service_ptr_id, "behindNat", "defaultTTL", "defaultAction", "lastResortAction", "maxAnswers") FROM stdin;
\.


--
-- Data for Name: requestrouter_servicemap; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY requestrouter_servicemap (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, prefix, "siteMap", "accessMap", owner_id, slice_id) FROM stdin;
\.


--
-- Name: requestrouter_servicemap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('requestrouter_servicemap_id_seq', 1, false);


--
-- Data for Name: syndicate_storage_slicesecret; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_slicesecret (id, secret, slice_id_id) FROM stdin;
\.


--
-- Name: syndicate_storage_slicesecret_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('syndicate_storage_slicesecret_id_seq', 1, false);


--
-- Data for Name: syndicate_storage_syndicateprincipal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_syndicateprincipal (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, principal_id, public_key_pem, sealed_private_key) FROM stdin;
\.


--
-- Name: syndicate_storage_syndicateprincipal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('syndicate_storage_syndicateprincipal_id_seq', 1, false);


--
-- Data for Name: syndicate_storage_syndicateservice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_syndicateservice (service_ptr_id) FROM stdin;
\.


--
-- Data for Name: syndicate_storage_volume; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_volume (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, name, description, blocksize, private, archive, cap_read_data, cap_write_data, cap_host_data, owner_id_id) FROM stdin;
\.


--
-- Name: syndicate_storage_volume_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('syndicate_storage_volume_id_seq', 1, false);


--
-- Data for Name: syndicate_storage_volumeaccessright; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_volumeaccessright (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, cap_read_data, cap_write_data, cap_host_data, owner_id_id, volume_id) FROM stdin;
\.


--
-- Name: syndicate_storage_volumeaccessright_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('syndicate_storage_volumeaccessright_id_seq', 1, false);


--
-- Data for Name: syndicate_storage_volumeslice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY syndicate_storage_volumeslice (id, created, updated, enacted, policed, backend_register, backend_status, deleted, write_protect, lazy_blocked, no_sync, cap_read_data, cap_write_data, cap_host_data, "UG_portnum", "RG_portnum", credentials_blob, slice_id_id, volume_id_id) FROM stdin;
\.


--
-- Name: syndicate_storage_volumeslice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('syndicate_storage_volumeslice_id_seq', 1, false);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_codename_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: core_account_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_account
    ADD CONSTRAINT core_account_pkey PRIMARY KEY (id);


--
-- Name: core_addresspool_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_addresspool
    ADD CONSTRAINT core_addresspool_pkey PRIMARY KEY (id);


--
-- Name: core_charge_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_charge
    ADD CONSTRAINT core_charge_pkey PRIMARY KEY (id);


--
-- Name: core_controller_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controller
    ADD CONSTRAINT core_controller_name_key UNIQUE (name);


--
-- Name: core_controller_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controller
    ADD CONSTRAINT core_controller_pkey PRIMARY KEY (id);


--
-- Name: core_controllercredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllercredential
    ADD CONSTRAINT core_controllercredential_pkey PRIMARY KEY (id);


--
-- Name: core_controllerdashboardview_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerdashboardview
    ADD CONSTRAINT core_controllerdashboardview_pkey PRIMARY KEY (id);


--
-- Name: core_controllerimages_image_id_77d3516dbca0a5d3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerimages
    ADD CONSTRAINT core_controllerimages_image_id_77d3516dbca0a5d3_uniq UNIQUE (image_id, controller_id);


--
-- Name: core_controllerimages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerimages
    ADD CONSTRAINT core_controllerimages_pkey PRIMARY KEY (id);


--
-- Name: core_controllernetwork_network_id_30ce4dc681f2844f_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllernetwork
    ADD CONSTRAINT core_controllernetwork_network_id_30ce4dc681f2844f_uniq UNIQUE (network_id, controller_id);


--
-- Name: core_controllernetwork_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllernetwork
    ADD CONSTRAINT core_controllernetwork_pkey PRIMARY KEY (id);


--
-- Name: core_controllerrole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerrole
    ADD CONSTRAINT core_controllerrole_pkey PRIMARY KEY (id);


--
-- Name: core_controllerrole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerrole
    ADD CONSTRAINT core_controllerrole_role_key UNIQUE (role);


--
-- Name: core_controllersite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersite
    ADD CONSTRAINT core_controllersite_pkey PRIMARY KEY (id);


--
-- Name: core_controllersite_site_id_22f56d79564bc81b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersite
    ADD CONSTRAINT core_controllersite_site_id_22f56d79564bc81b_uniq UNIQUE (site_id, controller_id);


--
-- Name: core_controllersiteprivileg_controller_id_5d0f19c7a7ceb9e5_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersiteprivilege
    ADD CONSTRAINT core_controllersiteprivileg_controller_id_5d0f19c7a7ceb9e5_uniq UNIQUE (controller_id, site_privilege_id, role_id);


--
-- Name: core_controllersiteprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersiteprivilege
    ADD CONSTRAINT core_controllersiteprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_controllerslice_controller_id_427703e66574ab83_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerslice
    ADD CONSTRAINT core_controllerslice_controller_id_427703e66574ab83_uniq UNIQUE (controller_id, slice_id);


--
-- Name: core_controllerslice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllerslice
    ADD CONSTRAINT core_controllerslice_pkey PRIMARY KEY (id);


--
-- Name: core_controllersliceprivile_controller_id_4e8a6f6f999d67c3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersliceprivilege
    ADD CONSTRAINT core_controllersliceprivile_controller_id_4e8a6f6f999d67c3_uniq UNIQUE (controller_id, slice_privilege_id);


--
-- Name: core_controllersliceprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controllersliceprivilege
    ADD CONSTRAINT core_controllersliceprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_controlleruser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controlleruser
    ADD CONSTRAINT core_controlleruser_pkey PRIMARY KEY (id);


--
-- Name: core_controlleruser_user_id_3beb039133bd099b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_controlleruser
    ADD CONSTRAINT core_controlleruser_user_id_3beb039133bd099b_uniq UNIQUE (user_id, controller_id);


--
-- Name: core_dashboardview_deployment_dashboardview_id_deployment_i_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_dashboardview_deployments
    ADD CONSTRAINT core_dashboardview_deployment_dashboardview_id_deployment_i_key UNIQUE (dashboardview_id, deployment_id);


--
-- Name: core_dashboardview_deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_dashboardview_deployments
    ADD CONSTRAINT core_dashboardview_deployments_pkey PRIMARY KEY (id);


--
-- Name: core_dashboardview_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_dashboardview
    ADD CONSTRAINT core_dashboardview_name_key UNIQUE (name);


--
-- Name: core_dashboardview_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_dashboardview
    ADD CONSTRAINT core_dashboardview_pkey PRIMARY KEY (id);


--
-- Name: core_deployment_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deployment
    ADD CONSTRAINT core_deployment_name_key UNIQUE (name);


--
-- Name: core_deployment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deployment
    ADD CONSTRAINT core_deployment_pkey PRIMARY KEY (id);


--
-- Name: core_deploymentprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deploymentprivilege
    ADD CONSTRAINT core_deploymentprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_deploymentprivilege_user_id_8f49da97c7cff06_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deploymentprivilege
    ADD CONSTRAINT core_deploymentprivilege_user_id_8f49da97c7cff06_uniq UNIQUE (user_id, deployment_id, role_id);


--
-- Name: core_deploymentrole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deploymentrole
    ADD CONSTRAINT core_deploymentrole_pkey PRIMARY KEY (id);


--
-- Name: core_deploymentrole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_deploymentrole
    ADD CONSTRAINT core_deploymentrole_role_key UNIQUE (role);


--
-- Name: core_diag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_diag
    ADD CONSTRAINT core_diag_pkey PRIMARY KEY (id);


--
-- Name: core_flavor_deployments_flavor_id_deployment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_flavor_deployments
    ADD CONSTRAINT core_flavor_deployments_flavor_id_deployment_id_key UNIQUE (flavor_id, deployment_id);


--
-- Name: core_flavor_deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_flavor_deployments
    ADD CONSTRAINT core_flavor_deployments_pkey PRIMARY KEY (id);


--
-- Name: core_flavor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_flavor
    ADD CONSTRAINT core_flavor_pkey PRIMARY KEY (id);


--
-- Name: core_image_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_image
    ADD CONSTRAINT core_image_name_key UNIQUE (name);


--
-- Name: core_image_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_image
    ADD CONSTRAINT core_image_pkey PRIMARY KEY (id);


--
-- Name: core_imagedeployments_image_id_3bc8a23925d399ff_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_imagedeployments
    ADD CONSTRAINT core_imagedeployments_image_id_3bc8a23925d399ff_uniq UNIQUE (image_id, deployment_id);


--
-- Name: core_imagedeployments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_imagedeployments
    ADD CONSTRAINT core_imagedeployments_pkey PRIMARY KEY (id);


--
-- Name: core_instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_pkey PRIMARY KEY (id);


--
-- Name: core_invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_invoice
    ADD CONSTRAINT core_invoice_pkey PRIMARY KEY (id);


--
-- Name: core_network_permitted_slices_network_id_slice_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_network_permitted_slices
    ADD CONSTRAINT core_network_permitted_slices_network_id_slice_id_key UNIQUE (network_id, slice_id);


--
-- Name: core_network_permitted_slices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_network_permitted_slices
    ADD CONSTRAINT core_network_permitted_slices_pkey PRIMARY KEY (id);


--
-- Name: core_network_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_network
    ADD CONSTRAINT core_network_pkey PRIMARY KEY (id);


--
-- Name: core_networkparameter_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_networkparameter
    ADD CONSTRAINT core_networkparameter_pkey PRIMARY KEY (id);


--
-- Name: core_networkparametertype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_networkparametertype
    ADD CONSTRAINT core_networkparametertype_pkey PRIMARY KEY (id);


--
-- Name: core_networkslice_network_id_78984d02ac7c1fb3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_networkslice
    ADD CONSTRAINT core_networkslice_network_id_78984d02ac7c1fb3_uniq UNIQUE (network_id, slice_id);


--
-- Name: core_networkslice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_networkslice
    ADD CONSTRAINT core_networkslice_pkey PRIMARY KEY (id);


--
-- Name: core_networktemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_networktemplate
    ADD CONSTRAINT core_networktemplate_pkey PRIMARY KEY (id);


--
-- Name: core_node_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_name_key UNIQUE (name);


--
-- Name: core_node_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_pkey PRIMARY KEY (id);


--
-- Name: core_nodelabel_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_nodelabel
    ADD CONSTRAINT core_nodelabel_name_key UNIQUE (name);


--
-- Name: core_nodelabel_node_nodelabel_id_node_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_nodelabel_node
    ADD CONSTRAINT core_nodelabel_node_nodelabel_id_node_id_key UNIQUE (nodelabel_id, node_id);


--
-- Name: core_nodelabel_node_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_nodelabel_node
    ADD CONSTRAINT core_nodelabel_node_pkey PRIMARY KEY (id);


--
-- Name: core_nodelabel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_nodelabel
    ADD CONSTRAINT core_nodelabel_pkey PRIMARY KEY (id);


--
-- Name: core_payment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_payment
    ADD CONSTRAINT core_payment_pkey PRIMARY KEY (id);


--
-- Name: core_port_network_id_693ab091ccd5a89a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_port
    ADD CONSTRAINT core_port_network_id_693ab091ccd5a89a_uniq UNIQUE (network_id, instance_id);


--
-- Name: core_port_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_port
    ADD CONSTRAINT core_port_pkey PRIMARY KEY (id);


--
-- Name: core_program_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_program
    ADD CONSTRAINT core_program_pkey PRIMARY KEY (id);


--
-- Name: core_project_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_project
    ADD CONSTRAINT core_project_name_key UNIQUE (name);


--
-- Name: core_project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_project
    ADD CONSTRAINT core_project_pkey PRIMARY KEY (id);


--
-- Name: core_reservation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_reservation
    ADD CONSTRAINT core_reservation_pkey PRIMARY KEY (id);


--
-- Name: core_reservedresource_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_reservedresource
    ADD CONSTRAINT core_reservedresource_pkey PRIMARY KEY (id);


--
-- Name: core_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_role
    ADD CONSTRAINT core_role_pkey PRIMARY KEY (id);


--
-- Name: core_router_networks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_router_networks
    ADD CONSTRAINT core_router_networks_pkey PRIMARY KEY (id);


--
-- Name: core_router_networks_router_id_network_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_router_networks
    ADD CONSTRAINT core_router_networks_router_id_network_id_key UNIQUE (router_id, network_id);


--
-- Name: core_router_permittedNetworks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "core_router_permittedNetworks"
    ADD CONSTRAINT "core_router_permittedNetworks_pkey" PRIMARY KEY (id);


--
-- Name: core_router_permittedNetworks_router_id_network_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "core_router_permittedNetworks"
    ADD CONSTRAINT "core_router_permittedNetworks_router_id_network_id_key" UNIQUE (router_id, network_id);


--
-- Name: core_router_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_router
    ADD CONSTRAINT core_router_pkey PRIMARY KEY (id);


--
-- Name: core_service_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_service
    ADD CONSTRAINT core_service_pkey PRIMARY KEY (id);


--
-- Name: core_serviceattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_serviceattribute
    ADD CONSTRAINT core_serviceattribute_pkey PRIMARY KEY (id);


--
-- Name: core_serviceclass_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_serviceclass
    ADD CONSTRAINT core_serviceclass_pkey PRIMARY KEY (id);


--
-- Name: core_serviceclass_upgradeFrom_from_serviceclass_id_to_servi_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "core_serviceclass_upgradeFrom"
    ADD CONSTRAINT "core_serviceclass_upgradeFrom_from_serviceclass_id_to_servi_key" UNIQUE (from_serviceclass_id, to_serviceclass_id);


--
-- Name: core_serviceclass_upgradeFrom_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "core_serviceclass_upgradeFrom"
    ADD CONSTRAINT "core_serviceclass_upgradeFrom_pkey" PRIMARY KEY (id);


--
-- Name: core_serviceprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_serviceprivilege
    ADD CONSTRAINT core_serviceprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_serviceprivilege_user_id_3e7ef04b1340e86c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_serviceprivilege
    ADD CONSTRAINT core_serviceprivilege_user_id_3e7ef04b1340e86c_uniq UNIQUE (user_id, service_id, role_id);


--
-- Name: core_serviceresource_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_serviceresource
    ADD CONSTRAINT core_serviceresource_pkey PRIMARY KEY (id);


--
-- Name: core_servicerole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_servicerole
    ADD CONSTRAINT core_servicerole_pkey PRIMARY KEY (id);


--
-- Name: core_servicerole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_servicerole
    ADD CONSTRAINT core_servicerole_role_key UNIQUE (role);


--
-- Name: core_site_login_base_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_site
    ADD CONSTRAINT core_site_login_base_key UNIQUE (login_base);


--
-- Name: core_site_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_site
    ADD CONSTRAINT core_site_pkey PRIMARY KEY (id);


--
-- Name: core_sitecredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_sitecredential
    ADD CONSTRAINT core_sitecredential_pkey PRIMARY KEY (id);


--
-- Name: core_sitedeployment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_sitedeployment
    ADD CONSTRAINT core_sitedeployment_pkey PRIMARY KEY (id);


--
-- Name: core_sitedeployment_site_id_ed533b8a1954fbb_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_sitedeployment
    ADD CONSTRAINT core_sitedeployment_site_id_ed533b8a1954fbb_uniq UNIQUE (site_id, deployment_id, controller_id);


--
-- Name: core_siteprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_siteprivilege
    ADD CONSTRAINT core_siteprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_siterole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_siterole
    ADD CONSTRAINT core_siterole_pkey PRIMARY KEY (id);


--
-- Name: core_siterole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_siterole
    ADD CONSTRAINT core_siterole_role_key UNIQUE (role);


--
-- Name: core_slice_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_name_key UNIQUE (name);


--
-- Name: core_slice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_pkey PRIMARY KEY (id);


--
-- Name: core_slicecredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slicecredential
    ADD CONSTRAINT core_slicecredential_pkey PRIMARY KEY (id);


--
-- Name: core_sliceprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_sliceprivilege
    ADD CONSTRAINT core_sliceprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_sliceprivilege_user_id_6bed734e37df8596_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_sliceprivilege
    ADD CONSTRAINT core_sliceprivilege_user_id_6bed734e37df8596_uniq UNIQUE (user_id, slice_id, role_id);


--
-- Name: core_slicerole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slicerole
    ADD CONSTRAINT core_slicerole_pkey PRIMARY KEY (id);


--
-- Name: core_slicerole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slicerole
    ADD CONSTRAINT core_slicerole_role_key UNIQUE (role);


--
-- Name: core_slicetag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_slicetag
    ADD CONSTRAINT core_slicetag_pkey PRIMARY KEY (id);


--
-- Name: core_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tag
    ADD CONSTRAINT core_tag_pkey PRIMARY KEY (id);


--
-- Name: core_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core_tenant_pkey PRIMARY KEY (id);


--
-- Name: core_tenantattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantattribute
    ADD CONSTRAINT core_tenantattribute_pkey PRIMARY KEY (id);


--
-- Name: core_tenantroot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantroot
    ADD CONSTRAINT core_tenantroot_pkey PRIMARY KEY (id);


--
-- Name: core_tenantrootprivilege_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantrootprivilege
    ADD CONSTRAINT core_tenantrootprivilege_pkey PRIMARY KEY (id);


--
-- Name: core_tenantrootprivilege_user_id_2bfebdce70c89f50_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantrootprivilege
    ADD CONSTRAINT core_tenantrootprivilege_user_id_2bfebdce70c89f50_uniq UNIQUE (user_id, tenant_root_id, role_id);


--
-- Name: core_tenantrootrole_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantrootrole
    ADD CONSTRAINT core_tenantrootrole_pkey PRIMARY KEY (id);


--
-- Name: core_tenantrootrole_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_tenantrootrole
    ADD CONSTRAINT core_tenantrootrole_role_key UNIQUE (role);


--
-- Name: core_usableobject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_usableobject
    ADD CONSTRAINT core_usableobject_pkey PRIMARY KEY (id);


--
-- Name: core_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_user
    ADD CONSTRAINT core_user_email_key UNIQUE (email);


--
-- Name: core_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_user
    ADD CONSTRAINT core_user_pkey PRIMARY KEY (id);


--
-- Name: core_usercredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_usercredential
    ADD CONSTRAINT core_usercredential_pkey PRIMARY KEY (id);


--
-- Name: core_userdashboardview_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY core_userdashboardview
    ADD CONSTRAINT core_userdashboardview_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_45f3b1d93ec8c61c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_45f3b1d93ec8c61c_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: hpc_accessmap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_accessmap
    ADD CONSTRAINT hpc_accessmap_pkey PRIMARY KEY (id);


--
-- Name: hpc_cdnprefix_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_cdnprefix
    ADD CONSTRAINT hpc_cdnprefix_pkey PRIMARY KEY (id);


--
-- Name: hpc_contentprovider_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_contentprovider
    ADD CONSTRAINT hpc_contentprovider_pkey PRIMARY KEY (id);


--
-- Name: hpc_contentprovider_users_contentprovider_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_contentprovider_users
    ADD CONSTRAINT hpc_contentprovider_users_contentprovider_id_user_id_key UNIQUE (contentprovider_id, user_id);


--
-- Name: hpc_contentprovider_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_contentprovider_users
    ADD CONSTRAINT hpc_contentprovider_users_pkey PRIMARY KEY (id);


--
-- Name: hpc_hpchealthcheck_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_hpchealthcheck
    ADD CONSTRAINT hpc_hpchealthcheck_pkey PRIMARY KEY (id);


--
-- Name: hpc_hpcservice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_hpcservice
    ADD CONSTRAINT hpc_hpcservice_pkey PRIMARY KEY (service_ptr_id);


--
-- Name: hpc_originserver_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_originserver
    ADD CONSTRAINT hpc_originserver_pkey PRIMARY KEY (id);


--
-- Name: hpc_serviceprovider_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_serviceprovider
    ADD CONSTRAINT hpc_serviceprovider_pkey PRIMARY KEY (id);


--
-- Name: hpc_sitemap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hpc_sitemap
    ADD CONSTRAINT hpc_sitemap_pkey PRIMARY KEY (id);


--
-- Name: requestrouter_requestrouterservice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY requestrouter_requestrouterservice
    ADD CONSTRAINT requestrouter_requestrouterservice_pkey PRIMARY KEY (service_ptr_id);


--
-- Name: requestrouter_servicemap_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY requestrouter_servicemap
    ADD CONSTRAINT requestrouter_servicemap_name_key UNIQUE (name);


--
-- Name: requestrouter_servicemap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY requestrouter_servicemap
    ADD CONSTRAINT requestrouter_servicemap_pkey PRIMARY KEY (id);


--
-- Name: syndicate_storage_slicesecret_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_slicesecret
    ADD CONSTRAINT syndicate_storage_slicesecret_pkey PRIMARY KEY (id);


--
-- Name: syndicate_storage_syndicateprincipal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_syndicateprincipal
    ADD CONSTRAINT syndicate_storage_syndicateprincipal_pkey PRIMARY KEY (id);


--
-- Name: syndicate_storage_syndicateprincipal_principal_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_syndicateprincipal
    ADD CONSTRAINT syndicate_storage_syndicateprincipal_principal_id_key UNIQUE (principal_id);


--
-- Name: syndicate_storage_syndicateservice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_syndicateservice
    ADD CONSTRAINT syndicate_storage_syndicateservice_pkey PRIMARY KEY (service_ptr_id);


--
-- Name: syndicate_storage_volume_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_volume
    ADD CONSTRAINT syndicate_storage_volume_pkey PRIMARY KEY (id);


--
-- Name: syndicate_storage_volumeaccessright_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_volumeaccessright
    ADD CONSTRAINT syndicate_storage_volumeaccessright_pkey PRIMARY KEY (id);


--
-- Name: syndicate_storage_volumeslice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY syndicate_storage_volumeslice
    ADD CONSTRAINT syndicate_storage_volumeslice_pkey PRIMARY KEY (id);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: core_account_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_account_9365d6e7 ON core_account USING btree (site_id);


--
-- Name: core_charge_8a089c2a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_charge_8a089c2a ON core_charge USING btree (account_id);


--
-- Name: core_charge_af31437c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_charge_af31437c ON core_charge USING btree (object_id);


--
-- Name: core_charge_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_charge_be7f3a0f ON core_charge USING btree (slice_id);


--
-- Name: core_charge_f1f5d967; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_charge_f1f5d967 ON core_charge USING btree (invoice_id);


--
-- Name: core_controller_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controller_5921cd4f ON core_controller USING btree (deployment_id);


--
-- Name: core_controllercredential_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllercredential_a31c1112 ON core_controllercredential USING btree (controller_id);


--
-- Name: core_controllercredential_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllercredential_b068931c ON core_controllercredential USING btree (name);


--
-- Name: core_controllerdashboardview_5da0369f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerdashboardview_5da0369f ON core_controllerdashboardview USING btree ("dashboardView_id");


--
-- Name: core_controllerdashboardview_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerdashboardview_a31c1112 ON core_controllerdashboardview USING btree (controller_id);


--
-- Name: core_controllerimages_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerimages_a31c1112 ON core_controllerimages USING btree (controller_id);


--
-- Name: core_controllerimages_f33175e6; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerimages_f33175e6 ON core_controllerimages USING btree (image_id);


--
-- Name: core_controllernetwork_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllernetwork_4e19114d ON core_controllernetwork USING btree (network_id);


--
-- Name: core_controllernetwork_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllernetwork_a31c1112 ON core_controllernetwork USING btree (controller_id);


--
-- Name: core_controllersite_38543614; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersite_38543614 ON core_controllersite USING btree (tenant_id);


--
-- Name: core_controllersite_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersite_9365d6e7 ON core_controllersite USING btree (site_id);


--
-- Name: core_controllersite_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersite_a31c1112 ON core_controllersite USING btree (controller_id);


--
-- Name: core_controllersiteprivilege_28116b8e; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersiteprivilege_28116b8e ON core_controllersiteprivilege USING btree (site_privilege_id);


--
-- Name: core_controllersiteprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersiteprivilege_84566833 ON core_controllersiteprivilege USING btree (role_id);


--
-- Name: core_controllersiteprivilege_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersiteprivilege_a31c1112 ON core_controllersiteprivilege USING btree (controller_id);


--
-- Name: core_controllerslice_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerslice_a31c1112 ON core_controllerslice USING btree (controller_id);


--
-- Name: core_controllerslice_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllerslice_be7f3a0f ON core_controllerslice USING btree (slice_id);


--
-- Name: core_controllersliceprivilege_25740d9a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersliceprivilege_25740d9a ON core_controllersliceprivilege USING btree (slice_privilege_id);


--
-- Name: core_controllersliceprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersliceprivilege_84566833 ON core_controllersliceprivilege USING btree (role_id);


--
-- Name: core_controllersliceprivilege_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controllersliceprivilege_a31c1112 ON core_controllersliceprivilege USING btree (controller_id);


--
-- Name: core_controlleruser_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controlleruser_a31c1112 ON core_controlleruser USING btree (controller_id);


--
-- Name: core_controlleruser_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_controlleruser_e8701ad4 ON core_controlleruser USING btree (user_id);


--
-- Name: core_dashboardview_deployments_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_dashboardview_deployments_5921cd4f ON core_dashboardview_deployments USING btree (deployment_id);


--
-- Name: core_dashboardview_deployments_79bd56c8; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_dashboardview_deployments_79bd56c8 ON core_dashboardview_deployments USING btree (dashboardview_id);


--
-- Name: core_deploymentprivilege_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_deploymentprivilege_5921cd4f ON core_deploymentprivilege USING btree (deployment_id);


--
-- Name: core_deploymentprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_deploymentprivilege_84566833 ON core_deploymentprivilege USING btree (role_id);


--
-- Name: core_deploymentprivilege_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_deploymentprivilege_e8701ad4 ON core_deploymentprivilege USING btree (user_id);


--
-- Name: core_flavor_deployments_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_flavor_deployments_5921cd4f ON core_flavor_deployments USING btree (deployment_id);


--
-- Name: core_flavor_deployments_dd3f198d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_flavor_deployments_dd3f198d ON core_flavor_deployments USING btree (flavor_id);


--
-- Name: core_imagedeployments_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_imagedeployments_5921cd4f ON core_imagedeployments USING btree (deployment_id);


--
-- Name: core_imagedeployments_f33175e6; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_imagedeployments_f33175e6 ON core_imagedeployments USING btree (image_id);


--
-- Name: core_instance_3700153c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_3700153c ON core_instance USING btree (creator_id);


--
-- Name: core_instance_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_5921cd4f ON core_instance USING btree (deployment_id);


--
-- Name: core_instance_6be37982; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_6be37982 ON core_instance USING btree (parent_id);


--
-- Name: core_instance_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_be7f3a0f ON core_instance USING btree (slice_id);


--
-- Name: core_instance_c693ebc8; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_c693ebc8 ON core_instance USING btree (node_id);


--
-- Name: core_instance_dd3f198d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_dd3f198d ON core_instance USING btree (flavor_id);


--
-- Name: core_instance_f33175e6; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_instance_f33175e6 ON core_instance USING btree (image_id);


--
-- Name: core_invoice_8a089c2a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_invoice_8a089c2a ON core_invoice USING btree (account_id);


--
-- Name: core_network_5e7b1936; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_network_5e7b1936 ON core_network USING btree (owner_id);


--
-- Name: core_network_74f53564; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_network_74f53564 ON core_network USING btree (template_id);


--
-- Name: core_network_permitted_slices_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_network_permitted_slices_4e19114d ON core_network_permitted_slices USING btree (network_id);


--
-- Name: core_network_permitted_slices_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_network_permitted_slices_be7f3a0f ON core_network_permitted_slices USING btree (slice_id);


--
-- Name: core_networkparameter_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_networkparameter_417f1b1c ON core_networkparameter USING btree (content_type_id);


--
-- Name: core_networkparameter_80740216; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_networkparameter_80740216 ON core_networkparameter USING btree (parameter_id);


--
-- Name: core_networkparametertype_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_networkparametertype_b068931c ON core_networkparametertype USING btree (name);


--
-- Name: core_networkslice_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_networkslice_4e19114d ON core_networkslice USING btree (network_id);


--
-- Name: core_networkslice_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_networkslice_be7f3a0f ON core_networkslice USING btree (slice_id);


--
-- Name: core_node_86aed61a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_node_86aed61a ON core_node USING btree (site_deployment_id);


--
-- Name: core_node_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_node_9365d6e7 ON core_node USING btree (site_id);


--
-- Name: core_nodelabel_node_c693ebc8; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_nodelabel_node_c693ebc8 ON core_nodelabel_node USING btree (node_id);


--
-- Name: core_nodelabel_node_dd685172; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_nodelabel_node_dd685172 ON core_nodelabel_node USING btree (nodelabel_id);


--
-- Name: core_payment_8a089c2a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_payment_8a089c2a ON core_payment USING btree (account_id);


--
-- Name: core_port_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_port_4e19114d ON core_port USING btree (network_id);


--
-- Name: core_port_51afcc4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_port_51afcc4f ON core_port USING btree (instance_id);


--
-- Name: core_program_5e7b1936; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_program_5e7b1936 ON core_program USING btree (owner_id);


--
-- Name: core_reservation_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_reservation_be7f3a0f ON core_reservation USING btree (slice_id);


--
-- Name: core_reservedresource_51afcc4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_reservedresource_51afcc4f ON core_reservedresource USING btree (instance_id);


--
-- Name: core_reservedresource_732beb09; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_reservedresource_732beb09 ON core_reservedresource USING btree ("reservationSet_id");


--
-- Name: core_reservedresource_e2f3ef5b; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_reservedresource_e2f3ef5b ON core_reservedresource USING btree (resource_id);


--
-- Name: core_role_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_role_417f1b1c ON core_role USING btree (content_type_id);


--
-- Name: core_router_5e7b1936; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_router_5e7b1936 ON core_router USING btree (owner_id);


--
-- Name: core_router_networks_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_router_networks_4e19114d ON core_router_networks USING btree (network_id);


--
-- Name: core_router_networks_52d4f3af; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_router_networks_52d4f3af ON core_router_networks USING btree (router_id);


--
-- Name: core_router_permittednetworks_4e19114d; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_router_permittednetworks_4e19114d ON "core_router_permittedNetworks" USING btree (network_id);


--
-- Name: core_router_permittednetworks_52d4f3af; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_router_permittednetworks_52d4f3af ON "core_router_permittedNetworks" USING btree (router_id);


--
-- Name: core_serviceattribute_b0dc1e29; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceattribute_b0dc1e29 ON core_serviceattribute USING btree (service_id);


--
-- Name: core_serviceclass_upgradefrom_a90aba97; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceclass_upgradefrom_a90aba97 ON "core_serviceclass_upgradeFrom" USING btree (to_serviceclass_id);


--
-- Name: core_serviceclass_upgradefrom_e970e0f1; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceclass_upgradefrom_e970e0f1 ON "core_serviceclass_upgradeFrom" USING btree (from_serviceclass_id);


--
-- Name: core_serviceprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceprivilege_84566833 ON core_serviceprivilege USING btree (role_id);


--
-- Name: core_serviceprivilege_b0dc1e29; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceprivilege_b0dc1e29 ON core_serviceprivilege USING btree (service_id);


--
-- Name: core_serviceprivilege_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceprivilege_e8701ad4 ON core_serviceprivilege USING btree (user_id);


--
-- Name: core_serviceresource_aa578034; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_serviceresource_aa578034 ON core_serviceresource USING btree ("serviceClass_id");


--
-- Name: core_sitecredential_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sitecredential_9365d6e7 ON core_sitecredential USING btree (site_id);


--
-- Name: core_sitecredential_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sitecredential_b068931c ON core_sitecredential USING btree (name);


--
-- Name: core_sitedeployment_5921cd4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sitedeployment_5921cd4f ON core_sitedeployment USING btree (deployment_id);


--
-- Name: core_sitedeployment_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sitedeployment_9365d6e7 ON core_sitedeployment USING btree (site_id);


--
-- Name: core_sitedeployment_a31c1112; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sitedeployment_a31c1112 ON core_sitedeployment USING btree (controller_id);


--
-- Name: core_siteprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_siteprivilege_84566833 ON core_siteprivilege USING btree (role_id);


--
-- Name: core_siteprivilege_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_siteprivilege_9365d6e7 ON core_siteprivilege USING btree (site_id);


--
-- Name: core_siteprivilege_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_siteprivilege_e8701ad4 ON core_siteprivilege USING btree (user_id);


--
-- Name: core_slice_3700153c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_3700153c ON core_slice USING btree (creator_id);


--
-- Name: core_slice_531a000f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_531a000f ON core_slice USING btree (default_flavor_id);


--
-- Name: core_slice_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_9365d6e7 ON core_slice USING btree (site_id);


--
-- Name: core_slice_a82f732f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_a82f732f ON core_slice USING btree (default_image_id);


--
-- Name: core_slice_aa578034; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_aa578034 ON core_slice USING btree ("serviceClass_id");


--
-- Name: core_slice_b0dc1e29; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slice_b0dc1e29 ON core_slice USING btree (service_id);


--
-- Name: core_slicecredential_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slicecredential_b068931c ON core_slicecredential USING btree (name);


--
-- Name: core_slicecredential_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slicecredential_be7f3a0f ON core_slicecredential USING btree (slice_id);


--
-- Name: core_sliceprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sliceprivilege_84566833 ON core_sliceprivilege USING btree (role_id);


--
-- Name: core_sliceprivilege_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sliceprivilege_be7f3a0f ON core_sliceprivilege USING btree (slice_id);


--
-- Name: core_sliceprivilege_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_sliceprivilege_e8701ad4 ON core_sliceprivilege USING btree (user_id);


--
-- Name: core_slicetag_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_slicetag_be7f3a0f ON core_slicetag USING btree (slice_id);


--
-- Name: core_tag_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tag_417f1b1c ON core_tag USING btree (content_type_id);


--
-- Name: core_tag_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tag_b068931c ON core_tag USING btree (name);


--
-- Name: core_tag_b0dc1e29; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tag_b0dc1e29 ON core_tag USING btree (service_id);


--
-- Name: core_tenant_6d0512e4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenant_6d0512e4 ON core_tenant USING btree (subscriber_tenant_id);


--
-- Name: core_tenant_a5c60fe7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenant_a5c60fe7 ON core_tenant USING btree (subscriber_service_id);


--
-- Name: core_tenant_d1fbfb28; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenant_d1fbfb28 ON core_tenant USING btree (provider_service_id);


--
-- Name: core_tenant_ec8cbfdc; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenant_ec8cbfdc ON core_tenant USING btree (subscriber_user_id);


--
-- Name: core_tenant_f687e49c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenant_f687e49c ON core_tenant USING btree (subscriber_root_id);


--
-- Name: core_tenantattribute_38543614; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenantattribute_38543614 ON core_tenantattribute USING btree (tenant_id);


--
-- Name: core_tenantrootprivilege_84566833; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenantrootprivilege_84566833 ON core_tenantrootprivilege USING btree (role_id);


--
-- Name: core_tenantrootprivilege_ad876f96; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenantrootprivilege_ad876f96 ON core_tenantrootprivilege USING btree (tenant_root_id);


--
-- Name: core_tenantrootprivilege_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_tenantrootprivilege_e8701ad4 ON core_tenantrootprivilege USING btree (user_id);


--
-- Name: core_user_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_user_9365d6e7 ON core_user USING btree (site_id);


--
-- Name: core_usercredential_b068931c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_usercredential_b068931c ON core_usercredential USING btree (name);


--
-- Name: core_usercredential_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_usercredential_e8701ad4 ON core_usercredential USING btree (user_id);


--
-- Name: core_userdashboardview_5da0369f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_userdashboardview_5da0369f ON core_userdashboardview USING btree ("dashboardView_id");


--
-- Name: core_userdashboardview_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX core_userdashboardview_e8701ad4 ON core_userdashboardview USING btree (user_id);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_de54fa62; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);


--
-- Name: hpc_accessmap_bc4912a0; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_accessmap_bc4912a0 ON hpc_accessmap USING btree ("contentProvider_id");


--
-- Name: hpc_cdnprefix_8473b38b; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_cdnprefix_8473b38b ON hpc_cdnprefix USING btree ("defaultOriginServer_id");


--
-- Name: hpc_cdnprefix_bc4912a0; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_cdnprefix_bc4912a0 ON hpc_cdnprefix USING btree ("contentProvider_id");


--
-- Name: hpc_contentprovider_ebdbc659; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_contentprovider_ebdbc659 ON hpc_contentprovider USING btree ("serviceProvider_id");


--
-- Name: hpc_contentprovider_users_82c06917; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_contentprovider_users_82c06917 ON hpc_contentprovider_users USING btree (contentprovider_id);


--
-- Name: hpc_contentprovider_users_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_contentprovider_users_e8701ad4 ON hpc_contentprovider_users USING btree (user_id);


--
-- Name: hpc_hpchealthcheck_591847bf; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_hpchealthcheck_591847bf ON hpc_hpchealthcheck USING btree ("hpcService_id");


--
-- Name: hpc_originserver_bc4912a0; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_originserver_bc4912a0 ON hpc_originserver USING btree ("contentProvider_id");


--
-- Name: hpc_serviceprovider_591847bf; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_serviceprovider_591847bf ON hpc_serviceprovider USING btree ("hpcService_id");


--
-- Name: hpc_sitemap_23b3ec8f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_sitemap_23b3ec8f ON hpc_sitemap USING btree ("cdnPrefix_id");


--
-- Name: hpc_sitemap_591847bf; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_sitemap_591847bf ON hpc_sitemap USING btree ("hpcService_id");


--
-- Name: hpc_sitemap_bc4912a0; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_sitemap_bc4912a0 ON hpc_sitemap USING btree ("contentProvider_id");


--
-- Name: hpc_sitemap_ebdbc659; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hpc_sitemap_ebdbc659 ON hpc_sitemap USING btree ("serviceProvider_id");


--
-- Name: requestrouter_servicemap_5e7b1936; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX requestrouter_servicemap_5e7b1936 ON requestrouter_servicemap USING btree (owner_id);


--
-- Name: requestrouter_servicemap_be7f3a0f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX requestrouter_servicemap_be7f3a0f ON requestrouter_servicemap USING btree (slice_id);


--
-- Name: syndicate_storage_slicesecret_b717f5ab; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_slicesecret_b717f5ab ON syndicate_storage_slicesecret USING btree (slice_id_id);


--
-- Name: syndicate_storage_volume_279564bf; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_volume_279564bf ON syndicate_storage_volume USING btree (owner_id_id);


--
-- Name: syndicate_storage_volumeaccessright_279564bf; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_volumeaccessright_279564bf ON syndicate_storage_volumeaccessright USING btree (owner_id_id);


--
-- Name: syndicate_storage_volumeaccessright_654102bb; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_volumeaccessright_654102bb ON syndicate_storage_volumeaccessright USING btree (volume_id);


--
-- Name: syndicate_storage_volumeslice_5b591651; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_volumeslice_5b591651 ON syndicate_storage_volumeslice USING btree (volume_id_id);


--
-- Name: syndicate_storage_volumeslice_b717f5ab; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX syndicate_storage_volumeslice_b717f5ab ON syndicate_storage_volumeslice USING btree (slice_id_id);


--
-- Name: auth_content_type_id_508cf46651277a81_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_content_type_id_508cf46651277a81_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: b8a90faf34a5dd47a7f1e2f88e99f8a2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_hpchealthcheck
    ADD CONSTRAINT b8a90faf34a5dd47a7f1e2f88e99f8a2 FOREIGN KEY ("hpcService_id") REFERENCES hpc_hpcservice(service_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: c_from_serviceclass_id_188a83eaefe26390_fk_core_serviceclass_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_serviceclass_upgradeFrom"
    ADD CONSTRAINT c_from_serviceclass_id_188a83eaefe26390_fk_core_serviceclass_id FOREIGN KEY (from_serviceclass_id) REFERENCES core_serviceclass(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: c_parameter_id_2c17791ba32bd8c8_fk_core_networkparametertype_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkparameter
    ADD CONSTRAINT c_parameter_id_2c17791ba32bd8c8_fk_core_networkparametertype_id FOREIGN KEY (parameter_id) REFERENCES core_networkparametertype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: c_site_deployment_id_2dc763428bdc2781_fk_core_sitedeployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT c_site_deployment_id_2dc763428bdc2781_fk_core_sitedeployment_id FOREIGN KEY (site_deployment_id) REFERENCES core_sitedeployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: co_slice_privilege_id_21402f4f2399079_fk_core_sliceprivilege_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersliceprivilege
    ADD CONSTRAINT co_slice_privilege_id_21402f4f2399079_fk_core_sliceprivilege_id FOREIGN KEY (slice_privilege_id) REFERENCES core_sliceprivilege(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cor_site_privilege_id_41490e8c05c2e685_fk_core_siteprivilege_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersiteprivilege
    ADD CONSTRAINT cor_site_privilege_id_41490e8c05c2e685_fk_core_siteprivilege_id FOREIGN KEY (site_privilege_id) REFERENCES core_siteprivilege(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cor_to_serviceclass_id_4e2748248647c43b_fk_core_serviceclass_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_serviceclass_upgradeFrom"
    ADD CONSTRAINT cor_to_serviceclass_id_4e2748248647c43b_fk_core_serviceclass_id FOREIGN KEY (to_serviceclass_id) REFERENCES core_serviceclass(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core__reservationset_id_395058233c59a671_fk_core_reservation_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservedresource
    ADD CONSTRAINT core__reservationset_id_395058233c59a671_fk_core_reservation_id FOREIGN KEY ("reservationSet_id") REFERENCES core_reservation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core__subscriber_root_id_26f21610cb2711f9_fk_core_tenantroot_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core__subscriber_root_id_26f21610cb2711f9_fk_core_tenantroot_id FOREIGN KEY (subscriber_root_id) REFERENCES core_tenantroot(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core__subscriber_service_id_5049d522dc2feae7_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core__subscriber_service_id_5049d522dc2feae7_fk_core_service_id FOREIGN KEY (subscriber_service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_account_site_id_7d8af010f408acb2_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_account
    ADD CONSTRAINT core_account_site_id_7d8af010f408acb2_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_charge_account_id_277c66c32427fb_fk_core_account_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_charge
    ADD CONSTRAINT core_charge_account_id_277c66c32427fb_fk_core_account_id FOREIGN KEY (account_id) REFERENCES core_account(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_charge_invoice_id_7af39adf58aad977_fk_core_invoice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_charge
    ADD CONSTRAINT core_charge_invoice_id_7af39adf58aad977_fk_core_invoice_id FOREIGN KEY (invoice_id) REFERENCES core_invoice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_charge_object_id_349f8834f1bf5ce6_fk_core_usableobject_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_charge
    ADD CONSTRAINT core_charge_object_id_349f8834f1bf5ce6_fk_core_usableobject_id FOREIGN KEY (object_id) REFERENCES core_usableobject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_charge_slice_id_5f33de3b320604f2_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_charge
    ADD CONSTRAINT core_charge_slice_id_5f33de3b320604f2_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_content_type_id_150a10ada282bcf9_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_role
    ADD CONSTRAINT core_content_type_id_150a10ada282bcf9_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_content_type_id_3cc30601489a3056_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkparameter
    ADD CONSTRAINT core_content_type_id_3cc30601489a3056_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_content_type_id_413c7b5400f8ad9c_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tag
    ADD CONSTRAINT core_content_type_id_413c7b5400f8ad9c_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_11d29f7e2a4a5462_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersiteprivilege
    ADD CONSTRAINT core_contr_controller_id_11d29f7e2a4a5462_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_1f82c3216437715f_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerdashboardview
    ADD CONSTRAINT core_contr_controller_id_1f82c3216437715f_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_46178c1d21384e5e_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersite
    ADD CONSTRAINT core_contr_controller_id_46178c1d21384e5e_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_4fb982de67c3b742_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersliceprivilege
    ADD CONSTRAINT core_contr_controller_id_4fb982de67c3b742_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_5cd05d37bbdf1d96_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controlleruser
    ADD CONSTRAINT core_contr_controller_id_5cd05d37bbdf1d96_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_60b467e792b15198_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllernetwork
    ADD CONSTRAINT core_contr_controller_id_60b467e792b15198_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_controller_id_7095bdbd27f73f56_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerslice
    ADD CONSTRAINT core_contr_controller_id_7095bdbd27f73f56_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contr_deployment_id_772a055c58b6e43a_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controller
    ADD CONSTRAINT core_contr_deployment_id_772a055c58b6e43a_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contro_controller_id_5906172a2f34d3a_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllercredential
    ADD CONSTRAINT core_contro_controller_id_5906172a2f34d3a_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_contro_controller_id_6d1311b7cc69cd7_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerimages
    ADD CONSTRAINT core_contro_controller_id_6d1311b7cc69cd7_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_controllerimage_image_id_5713221a6b077f6b_fk_core_image_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerimages
    ADD CONSTRAINT core_controllerimage_image_id_5713221a6b077f6b_fk_core_image_id FOREIGN KEY (image_id) REFERENCES core_image(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_controllern_network_id_3fe7748f6851d06f_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllernetwork
    ADD CONSTRAINT core_controllern_network_id_3fe7748f6851d06f_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_controllersite_site_id_4fa87f0734a60665_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllersite
    ADD CONSTRAINT core_controllersite_site_id_4fa87f0734a60665_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_controllerslice_slice_id_7005d287c601356b_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerslice
    ADD CONSTRAINT core_controllerslice_slice_id_7005d287c601356b_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_controlleruser_user_id_60dc3a7220b1005b_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controlleruser
    ADD CONSTRAINT core_controlleruser_user_id_60dc3a7220b1005b_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_dashbo_deployment_id_8b902dfc7ab128b_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_dashboardview_deployments
    ADD CONSTRAINT core_dashbo_deployment_id_8b902dfc7ab128b_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_dashboardview_id_1241776e11825a15_fk_core_dashboardview_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_controllerdashboardview
    ADD CONSTRAINT core_dashboardview_id_1241776e11825a15_fk_core_dashboardview_id FOREIGN KEY ("dashboardView_id") REFERENCES core_dashboardview(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_dashboardview_id_623d5d799346e0f8_fk_core_dashboardview_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_dashboardview_deployments
    ADD CONSTRAINT core_dashboardview_id_623d5d799346e0f8_fk_core_dashboardview_id FOREIGN KEY (dashboardview_id) REFERENCES core_dashboardview(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_dashboardview_id_7d9723f531eefdde_fk_core_dashboardview_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_userdashboardview
    ADD CONSTRAINT core_dashboardview_id_7d9723f531eefdde_fk_core_dashboardview_id FOREIGN KEY ("dashboardView_id") REFERENCES core_dashboardview(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deplo_deployment_id_4606c90fff2e5ecf_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deploymentprivilege
    ADD CONSTRAINT core_deplo_deployment_id_4606c90fff2e5ecf_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deploym_role_id_221f61258b29e608_fk_core_deploymentrole_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deploymentprivilege
    ADD CONSTRAINT core_deploym_role_id_221f61258b29e608_fk_core_deploymentrole_id FOREIGN KEY (role_id) REFERENCES core_deploymentrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deploymentprivile_user_id_2ac00d41376e2a8d_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_deploymentprivilege
    ADD CONSTRAINT core_deploymentprivile_user_id_2ac00d41376e2a8d_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_flavo_deployment_id_33af1c761c0497e3_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_flavor_deployments
    ADD CONSTRAINT core_flavo_deployment_id_33af1c761c0497e3_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_flavor_deploy_flavor_id_3e598722be0b3446_fk_core_flavor_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_flavor_deployments
    ADD CONSTRAINT core_flavor_deploy_flavor_id_3e598722be0b3446_fk_core_flavor_id FOREIGN KEY (flavor_id) REFERENCES core_flavor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_image_deployment_id_31772dfdcf4b80eb_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_imagedeployments
    ADD CONSTRAINT core_image_deployment_id_31772dfdcf4b80eb_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_imagedeployment_image_id_4a6df22c06603b40_fk_core_image_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_imagedeployments
    ADD CONSTRAINT core_imagedeployment_image_id_4a6df22c06603b40_fk_core_image_id FOREIGN KEY (image_id) REFERENCES core_image(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_insta_deployment_id_111e2cdd025ec8ef_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_insta_deployment_id_111e2cdd025ec8ef_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_creator_id_66a7e8c819d15b29_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_creator_id_66a7e8c819d15b29_fk_core_user_id FOREIGN KEY (creator_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_flavor_id_61bc3198a5673218_fk_core_flavor_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_flavor_id_61bc3198a5673218_fk_core_flavor_id FOREIGN KEY (flavor_id) REFERENCES core_flavor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_image_id_5c8c96fe9a61802c_fk_core_image_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_image_id_5c8c96fe9a61802c_fk_core_image_id FOREIGN KEY (image_id) REFERENCES core_image(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_node_id_ae899cb7a62df9a_fk_core_node_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_node_id_ae899cb7a62df9a_fk_core_node_id FOREIGN KEY (node_id) REFERENCES core_node(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_parent_id_20ac3a3c727decb4_fk_core_instance_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_parent_id_20ac3a3c727decb4_fk_core_instance_id FOREIGN KEY (parent_id) REFERENCES core_instance(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_instance_slice_id_2ddcfe06a9e4c985_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_instance
    ADD CONSTRAINT core_instance_slice_id_2ddcfe06a9e4c985_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_invoice_account_id_7802a49ab0cec433_fk_core_account_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_invoice
    ADD CONSTRAINT core_invoice_account_id_7802a49ab0cec433_fk_core_account_id FOREIGN KEY (account_id) REFERENCES core_account(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_ne_template_id_7268a8d58aa4008e_fk_core_networktemplate_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network
    ADD CONSTRAINT core_ne_template_id_7268a8d58aa4008e_fk_core_networktemplate_id FOREIGN KEY (template_id) REFERENCES core_networktemplate(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_network_owner_id_1b5a720eac1f1d6c_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network
    ADD CONSTRAINT core_network_owner_id_1b5a720eac1f1d6c_fk_core_slice_id FOREIGN KEY (owner_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_network_perm_network_id_79f8a18a0197dd1_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network_permitted_slices
    ADD CONSTRAINT core_network_perm_network_id_79f8a18a0197dd1_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_network_permitt_slice_id_7d7e6e1a0b962f45_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_network_permitted_slices
    ADD CONSTRAINT core_network_permitt_slice_id_7d7e6e1a0b962f45_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_networkslic_network_id_2823f40a154bc2e6_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkslice
    ADD CONSTRAINT core_networkslic_network_id_2823f40a154bc2e6_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_networkslice_slice_id_801f34a8ab285a0_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_networkslice
    ADD CONSTRAINT core_networkslice_slice_id_801f34a8ab285a0_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_node_site_id_28bac05ef1a512ce_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_site_id_28bac05ef1a512ce_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_nodelab_nodelabel_id_6bbea668080a7ba5_fk_core_nodelabel_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_nodelabel_node
    ADD CONSTRAINT core_nodelab_nodelabel_id_6bbea668080a7ba5_fk_core_nodelabel_id FOREIGN KEY (nodelabel_id) REFERENCES core_nodelabel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_nodelabel_node_node_id_b98c651a6265ec0_fk_core_node_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_nodelabel_node
    ADD CONSTRAINT core_nodelabel_node_node_id_b98c651a6265ec0_fk_core_node_id FOREIGN KEY (node_id) REFERENCES core_node(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_payment_account_id_3cc9ae7e7b925002_fk_core_account_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_payment
    ADD CONSTRAINT core_payment_account_id_3cc9ae7e7b925002_fk_core_account_id FOREIGN KEY (account_id) REFERENCES core_account(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_port_instance_id_5bdb1ae59ca1dc73_fk_core_instance_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_port
    ADD CONSTRAINT core_port_instance_id_5bdb1ae59ca1dc73_fk_core_instance_id FOREIGN KEY (instance_id) REFERENCES core_instance(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_port_network_id_655a9dc4ef32f845_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_port
    ADD CONSTRAINT core_port_network_id_655a9dc4ef32f845_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_program_owner_id_491cb2182952268e_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_program
    ADD CONSTRAINT core_program_owner_id_491cb2182952268e_fk_core_user_id FOREIGN KEY (owner_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_re_resource_id_1126f44e743a899d_fk_core_serviceresource_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservedresource
    ADD CONSTRAINT core_re_resource_id_1126f44e743a899d_fk_core_serviceresource_id FOREIGN KEY (resource_id) REFERENCES core_serviceresource(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_reservation_slice_id_4df07726653daed_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservation
    ADD CONSTRAINT core_reservation_slice_id_4df07726653daed_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_reservedr_instance_id_626caea355f5195e_fk_core_instance_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_reservedresource
    ADD CONSTRAINT core_reservedr_instance_id_626caea355f5195e_fk_core_instance_id FOREIGN KEY (instance_id) REFERENCES core_instance(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_router_netw_network_id_12bc59c5ca78fdc0_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_router_networks
    ADD CONSTRAINT core_router_netw_network_id_12bc59c5ca78fdc0_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_router_networ_router_id_3cf4f94bd7970e88_fk_core_router_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_router_networks
    ADD CONSTRAINT core_router_networ_router_id_3cf4f94bd7970e88_fk_core_router_id FOREIGN KEY (router_id) REFERENCES core_router(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_router_owner_id_13c4ac38c56512c6_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_router
    ADD CONSTRAINT core_router_owner_id_13c4ac38c56512c6_fk_core_slice_id FOREIGN KEY (owner_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_router_permi_network_id_8ee54284c93cd43_fk_core_network_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_router_permittedNetworks"
    ADD CONSTRAINT core_router_permi_network_id_8ee54284c93cd43_fk_core_network_id FOREIGN KEY (network_id) REFERENCES core_network(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_router_permit_router_id_3506769cdaf40bb5_fk_core_router_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "core_router_permittedNetworks"
    ADD CONSTRAINT core_router_permit_router_id_3506769cdaf40bb5_fk_core_router_id FOREIGN KEY (router_id) REFERENCES core_router(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_s_serviceclass_id_7fa5b55190a88c84_fk_core_serviceclass_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceresource
    ADD CONSTRAINT core_s_serviceclass_id_7fa5b55190a88c84_fk_core_serviceclass_id FOREIGN KEY ("serviceClass_id") REFERENCES core_serviceclass(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_serviceattr_service_id_5dd88bdc4a289e9e_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceattribute
    ADD CONSTRAINT core_serviceattr_service_id_5dd88bdc4a289e9e_fk_core_service_id FOREIGN KEY (service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_servicepri_role_id_2516e31051d592b9_fk_core_servicerole_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceprivilege
    ADD CONSTRAINT core_servicepri_role_id_2516e31051d592b9_fk_core_servicerole_id FOREIGN KEY (role_id) REFERENCES core_servicerole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_servicepriv_service_id_326f2584a82884fb_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceprivilege
    ADD CONSTRAINT core_servicepriv_service_id_326f2584a82884fb_fk_core_service_id FOREIGN KEY (service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_serviceprivilege_user_id_5e78485b5063e04_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_serviceprivilege
    ADD CONSTRAINT core_serviceprivilege_user_id_5e78485b5063e04_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sitecredential_site_id_2ede808de256b5ca_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitecredential
    ADD CONSTRAINT core_sitecredential_site_id_2ede808de256b5ca_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sited_controller_id_30291acda546cff3_fk_core_controller_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitedeployment
    ADD CONSTRAINT core_sited_controller_id_30291acda546cff3_fk_core_controller_id FOREIGN KEY (controller_id) REFERENCES core_controller(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sited_deployment_id_2073c8bc2ac33aee_fk_core_deployment_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitedeployment
    ADD CONSTRAINT core_sited_deployment_id_2073c8bc2ac33aee_fk_core_deployment_id FOREIGN KEY (deployment_id) REFERENCES core_deployment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sitedeployment_site_id_10d760d1d81e2090_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sitedeployment
    ADD CONSTRAINT core_sitedeployment_site_id_10d760d1d81e2090_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_siteprivilege_role_id_71e5069ae809cb06_fk_core_siterole_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_siteprivilege
    ADD CONSTRAINT core_siteprivilege_role_id_71e5069ae809cb06_fk_core_siterole_id FOREIGN KEY (role_id) REFERENCES core_siterole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_siteprivilege_site_id_33ec92307c1cb3bd_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_siteprivilege
    ADD CONSTRAINT core_siteprivilege_site_id_33ec92307c1cb3bd_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_siteprivilege_user_id_4a58c40e58eea8c5_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_siteprivilege
    ADD CONSTRAINT core_siteprivilege_user_id_4a58c40e58eea8c5_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sl_serviceclass_id_77da7f94b58488b_fk_core_serviceclass_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_sl_serviceclass_id_77da7f94b58488b_fk_core_serviceclass_id FOREIGN KEY ("serviceClass_id") REFERENCES core_serviceclass(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slice_creator_id_7c5fa82797e0d281_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_creator_id_7c5fa82797e0d281_fk_core_user_id FOREIGN KEY (creator_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slice_default_flavor_id_7e9b60d7e92ce276_fk_core_flavor_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_default_flavor_id_7e9b60d7e92ce276_fk_core_flavor_id FOREIGN KEY (default_flavor_id) REFERENCES core_flavor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slice_default_image_id_4cc5967fffec96da_fk_core_image_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_default_image_id_4cc5967fffec96da_fk_core_image_id FOREIGN KEY (default_image_id) REFERENCES core_image(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slice_service_id_56ec7a0b3401bf7c_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_service_id_56ec7a0b3401bf7c_fk_core_service_id FOREIGN KEY (service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slice_site_id_13fe089488dd45_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slice
    ADD CONSTRAINT core_slice_site_id_13fe089488dd45_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slicecredential_slice_id_1c79ffce7dd61f3c_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slicecredential
    ADD CONSTRAINT core_slicecredential_slice_id_1c79ffce7dd61f3c_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sliceprivile_role_id_1d55e0b0ac43107a_fk_core_slicerole_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sliceprivilege
    ADD CONSTRAINT core_sliceprivile_role_id_1d55e0b0ac43107a_fk_core_slicerole_id FOREIGN KEY (role_id) REFERENCES core_slicerole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sliceprivilege_slice_id_3fbaadbffeb24835_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sliceprivilege
    ADD CONSTRAINT core_sliceprivilege_slice_id_3fbaadbffeb24835_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_sliceprivilege_user_id_253eeb2ddef0e745_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_sliceprivilege
    ADD CONSTRAINT core_sliceprivilege_user_id_253eeb2ddef0e745_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_slicetag_slice_id_75dfa2524457256_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_slicetag
    ADD CONSTRAINT core_slicetag_slice_id_75dfa2524457256_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tag_service_id_5e53fc9f784e1c0_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tag
    ADD CONSTRAINT core_tag_service_id_5e53fc9f784e1c0_fk_core_service_id FOREIGN KEY (service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_te_provider_service_id_6f2ead723387396a_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core_te_provider_service_id_6f2ead723387396a_fk_core_service_id FOREIGN KEY (provider_service_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_te_subscriber_tenant_id_5c45dc20d190aa0f_fk_core_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core_te_subscriber_tenant_id_5c45dc20d190aa0f_fk_core_tenant_id FOREIGN KEY (subscriber_tenant_id) REFERENCES core_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tena_tenant_root_id_27d6362f903728d9_fk_core_tenantroot_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantrootprivilege
    ADD CONSTRAINT core_tena_tenant_root_id_27d6362f903728d9_fk_core_tenantroot_id FOREIGN KEY (tenant_root_id) REFERENCES core_tenantroot(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tenant_subscriber_user_id_2fad15bb074ed3d6_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenant
    ADD CONSTRAINT core_tenant_subscriber_user_id_2fad15bb074ed3d6_fk_core_user_id FOREIGN KEY (subscriber_user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tenantattribut_tenant_id_aef1dc094229bec_fk_core_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantattribute
    ADD CONSTRAINT core_tenantattribut_tenant_id_aef1dc094229bec_fk_core_tenant_id FOREIGN KEY (tenant_id) REFERENCES core_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tenantro_role_id_56bfa65de5fb299_fk_core_tenantrootrole_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantrootprivilege
    ADD CONSTRAINT core_tenantro_role_id_56bfa65de5fb299_fk_core_tenantrootrole_id FOREIGN KEY (role_id) REFERENCES core_tenantrootrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_tenantrootprivile_user_id_77f85e71ff279b56_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_tenantrootprivilege
    ADD CONSTRAINT core_tenantrootprivile_user_id_77f85e71ff279b56_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_user_site_id_3cc7d076f7b58a7_fk_core_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_user
    ADD CONSTRAINT core_user_site_id_3cc7d076f7b58a7_fk_core_site_id FOREIGN KEY (site_id) REFERENCES core_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_usercredential_user_id_2db1046eae94c01a_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_usercredential
    ADD CONSTRAINT core_usercredential_user_id_2db1046eae94c01a_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_userdashboardview_user_id_66fac29b72c1b321_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY core_userdashboardview
    ADD CONSTRAINT core_userdashboardview_user_id_66fac29b72c1b321_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: d9aeae61481f9ccd18f57c7b51a38461; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_sitemap
    ADD CONSTRAINT d9aeae61481f9ccd18f57c7b51a38461 FOREIGN KEY ("hpcService_id") REFERENCES hpc_hpcservice(service_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: defaultoriginserver_id_3cb657d79e69f1e9_fk_hpc_originserver_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_cdnprefix
    ADD CONSTRAINT defaultoriginserver_id_3cb657d79e69f1e9_fk_hpc_originserver_id FOREIGN KEY ("defaultOriginServer_id") REFERENCES hpc_originserver(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djan_content_type_id_697914295151027a_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT djan_content_type_id_697914295151027a_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_52fdd58701c5f563_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_52fdd58701c5f563_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ea3ce8ae9fc3a320680647cef82b1a56; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_serviceprovider
    ADD CONSTRAINT ea3ce8ae9fc3a320680647cef82b1a56 FOREIGN KEY ("hpcService_id") REFERENCES hpc_hpcservice(service_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_contentprovider_id_1420a46480bb1aff_fk_hpc_contentprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_contentprovider_users
    ADD CONSTRAINT h_contentprovider_id_1420a46480bb1aff_fk_hpc_contentprovider_id FOREIGN KEY (contentprovider_id) REFERENCES hpc_contentprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_contentprovider_id_2f27d5fdbb2459c8_fk_hpc_contentprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_originserver
    ADD CONSTRAINT h_contentprovider_id_2f27d5fdbb2459c8_fk_hpc_contentprovider_id FOREIGN KEY ("contentProvider_id") REFERENCES hpc_contentprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_contentprovider_id_63639a8e6ca8e2cd_fk_hpc_contentprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_cdnprefix
    ADD CONSTRAINT h_contentprovider_id_63639a8e6ca8e2cd_fk_hpc_contentprovider_id FOREIGN KEY ("contentProvider_id") REFERENCES hpc_contentprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_contentprovider_id_7acf72f284b3b30e_fk_hpc_contentprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_accessmap
    ADD CONSTRAINT h_contentprovider_id_7acf72f284b3b30e_fk_hpc_contentprovider_id FOREIGN KEY ("contentProvider_id") REFERENCES hpc_contentprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_serviceprovider_id_1b9fb41a73ac1b6a_fk_hpc_serviceprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_contentprovider
    ADD CONSTRAINT h_serviceprovider_id_1b9fb41a73ac1b6a_fk_hpc_serviceprovider_id FOREIGN KEY ("serviceProvider_id") REFERENCES hpc_serviceprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: h_serviceprovider_id_788bfbe86c90f205_fk_hpc_serviceprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_sitemap
    ADD CONSTRAINT h_serviceprovider_id_788bfbe86c90f205_fk_hpc_serviceprovider_id FOREIGN KEY ("serviceProvider_id") REFERENCES hpc_serviceprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hp_contentprovider_id_2a37a8e8bee9c03_fk_hpc_contentprovider_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_sitemap
    ADD CONSTRAINT hp_contentprovider_id_2a37a8e8bee9c03_fk_hpc_contentprovider_id FOREIGN KEY ("contentProvider_id") REFERENCES hpc_contentprovider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hpc_contentprovider_us_user_id_480a7cd783fecf37_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_contentprovider_users
    ADD CONSTRAINT hpc_contentprovider_us_user_id_480a7cd783fecf37_fk_core_user_id FOREIGN KEY (user_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hpc_hpcservi_service_ptr_id_1b2f328c77b1554d_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_hpcservice
    ADD CONSTRAINT hpc_hpcservi_service_ptr_id_1b2f328c77b1554d_fk_core_service_id FOREIGN KEY (service_ptr_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hpc_sitemap_cdnprefix_id_3c0b2f75c5a9a81e_fk_hpc_cdnprefix_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hpc_sitemap
    ADD CONSTRAINT hpc_sitemap_cdnprefix_id_3c0b2f75c5a9a81e_fk_hpc_cdnprefix_id FOREIGN KEY ("cdnPrefix_id") REFERENCES hpc_cdnprefix(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: requestroute_service_ptr_id_479451a78740d081_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY requestrouter_requestrouterservice
    ADD CONSTRAINT requestroute_service_ptr_id_479451a78740d081_fk_core_service_id FOREIGN KEY (service_ptr_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: requestrouter_serv_owner_id_5c71a9586041d2bc_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY requestrouter_servicemap
    ADD CONSTRAINT requestrouter_serv_owner_id_5c71a9586041d2bc_fk_core_service_id FOREIGN KEY (owner_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: requestrouter_servic_slice_id_50e57057a561f22f_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY requestrouter_servicemap
    ADD CONSTRAINT requestrouter_servic_slice_id_50e57057a561f22f_fk_core_slice_id FOREIGN KEY (slice_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sy_volume_id_id_7dd16c76bfd7b129_fk_syndicate_storage_volume_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeslice
    ADD CONSTRAINT sy_volume_id_id_7dd16c76bfd7b129_fk_syndicate_storage_volume_id FOREIGN KEY (volume_id_id) REFERENCES syndicate_storage_volume(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndi_volume_id_3718f5b02d2245ce_fk_syndicate_storage_volume_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeaccessright
    ADD CONSTRAINT syndi_volume_id_3718f5b02d2245ce_fk_syndicate_storage_volume_id FOREIGN KEY (volume_id) REFERENCES syndicate_storage_volume(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndicate_st_service_ptr_id_26ca3aeabed50b6d_fk_core_service_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_syndicateservice
    ADD CONSTRAINT syndicate_st_service_ptr_id_26ca3aeabed50b6d_fk_core_service_id FOREIGN KEY (service_ptr_id) REFERENCES core_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndicate_storage__owner_id_id_3d3e3d492d6cd6b5_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeaccessright
    ADD CONSTRAINT syndicate_storage__owner_id_id_3d3e3d492d6cd6b5_fk_core_user_id FOREIGN KEY (owner_id_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndicate_storage__owner_id_id_7a99f36bf51f2c78_fk_core_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volume
    ADD CONSTRAINT syndicate_storage__owner_id_id_7a99f36bf51f2c78_fk_core_user_id FOREIGN KEY (owner_id_id) REFERENCES core_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndicate_storage_slice_id_id_1c80c36535559ad6_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_slicesecret
    ADD CONSTRAINT syndicate_storage_slice_id_id_1c80c36535559ad6_fk_core_slice_id FOREIGN KEY (slice_id_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: syndicate_storage_slice_id_id_36fa39a9ae458538_fk_core_slice_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY syndicate_storage_volumeslice
    ADD CONSTRAINT syndicate_storage_slice_id_id_36fa39a9ae458538_fk_core_slice_id FOREIGN KEY (slice_id_id) REFERENCES core_slice(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

