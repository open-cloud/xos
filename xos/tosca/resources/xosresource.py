import os
import pdb
import json
import subprocess
import sys

from core.models import User

class XOSResource(object):
    xos_base_class = "XOSResource"
    xos_model = None
    name_field = "name"
    copyin_props = []
    provides = None

    def __init__(self, user, nodetemplate, engine):
        self.dirty = False
        self.deferred_sync = []
        self.user = user
        self.nodetemplate = nodetemplate
        self.engine = engine

    @property
    def full_name(self):
        return self.nodetemplate.name

    @property
    def obj_name(self):
        if "#" in self.nodetemplate.name:
            return self.nodetemplate.name.split("#",1)[1]
        else:
            return self.nodetemplate.name

    def get_all_required_node_names(self):
        results = []
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                results.append(v["node"])
        return results

    def get_requirements(self, relationship_name, throw_exception=False):
        """ helper to search the list of requirements for a particular relationship
            type.
        """

        results = []
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                if (v["relationship"] == relationship_name):
                    results.append(v["node"])

        if (not results) and throw_exception:
            raise Exception("Failed to find requirement in %s using relationship %s" % (self.full_name, relationship_name))

        return results

    def get_requirement(self, relationship_name, throw_exception=False):
        reqs = self.get_requirements(relationship_name, throw_exception)
        if not reqs:
            return None
        return reqs[0]

    def get_scalable(self):
        scalable = self.nodetemplate.get_capabilities().get("scalable", None)
        if scalable:
            return {"min_instances": scalable.get_property_value("min_instances"),
                    "max_instances": scalable.get_property_value("max_instances"),
                    "default_instances": scalable.get_property_value("default_instances")}
        else:
            return {}

    def get_property(self, name):
        return self.nodetemplate.get_property_value(name)

    def get_property_default(self, name, default=None):
        props = self.nodetemplate.get_properties()
        if props and name in props.keys():
            return props[name].value
        return default

    def get_xos_object(self, cls, throw_exception=True, **kwargs):
        # do the same parsing that we do for objname
        for (k,v) in kwargs.items():
            if (k=="name") and ("#" in v):
                kwargs[k] = v.split("#",1)[1]

        objs = cls.objects.filter(**kwargs)
        if not objs:
            if throw_exception:
                raise Exception("Failed to find %s filtered by %s" % (cls.__name__, str(kwargs)))
            return None
        return objs[0]

    def get_replaces_objs(self):
        replaces = self.get_property_default("replaces", None)
        if replaces:
            return self.xos_model.objects.filter(**{self.name_field: replaces})
        else:
            return []

    def get_existing_objs(self):
        return self.xos_model.objects.filter(**{self.name_field: self.obj_name})

    def get_model_class_name(self):
        return self.xos_model.__name__

    def create_or_update(self):
        replaces_objs = self.get_replaces_objs()
        existing_objs = self.get_existing_objs()

        if (replaces_objs and existing_objs):
            ro = replaces_objs[0]
            self.info("deleting %s:%s" % (self.get_model_class_name(), getattr(ro,self.name_field)))
            ro.delete()

            # in case we wanted to throw an error instead...
            #self.error("CRITICAL ERROR: Both %s and %s exist!" % (getattr(ro,self.name_field), self.obj_name))
            #sys.exit(-1)

        if (replaces_objs and not existing_objs):
            ro = replaces_objs[0]
            self.info("renaming %s:%s to %s" % (self.get_model_class_name(), getattr(ro,self.name_field), self.obj_name))
            setattr(ro, self.name_field, self.obj_name)
            ro.save()
            existing_objs = self.get_existing_objs()

        if existing_objs:
            if self.get_property_default("no-update", False):
                self.info("%s:%s (%s) already exists. Skipping update due to 'no-update' property" % (self.get_model_class_name(), self.obj_name, self.full_name))
            else:
                self.info("%s:%s (%s) already exists" % (self.get_model_class_name(), self.obj_name, self.full_name))
                self.update(existing_objs[0])
        else:
            if self.get_property_default("no-create", False):
                self.info("%s:%s (%s) does not exist, but 'no-create' is specified" % (self.get_model_class_name(), self.obj_name, self.full_name))
            else:
                self.create()

    def can_delete(self, obj):
        if self.get_property_default("no-delete",False):
            self.info("%s:%s %s is marked 'no-delete'. Skipping delete." % (self.get_model_class_name(), self.obj_name, self.full_name))
            return False
        return True

    def postprocess_privileges(self, roleclass, privclass, rolemap, obj, toFieldName):
        for (rel, role) in rolemap:
            for email in self.get_requirements(rel):
                role_obj = self.get_xos_object(roleclass, throw_exception=False, role=role)
                if not role_obj:
                    # if the role doesn't exist, make it
                    self.info("Creating %s %s" % (roleclass.__name__, role))
                    role_obj = roleclass(role=role)
                    role_obj.save()

                user = self.get_xos_object(User, email=email)
                if not privclass.objects.filter(user=user, role=role_obj, **{toFieldName: obj}):
                    sp = privclass(user=user, role=role_obj, **{toFieldName: obj})
                    sp.save()
                    self.info("Added privilege on %s role %s for %s" % (str(obj), str(role), str(user)))

    def postprocess(self, obj):
        pass

    def intrinsic_get_artifact(self, obj=None, name=None, method=None):
        if obj!="SELF":
            raise Exception("only SELF is supported for get_artifact first arg")
        if method!="LOCAL_FILE":
            raise Exception("only LOCAL_FILE is supported for get_artifact third arg")

        for (k,v) in self.nodetemplate.entity_tpl.get("artifacts", {}).items():
            if k == name:
                if not os.path.exists(v):
                    raise Exception("Artifact local file %s for artifact %s does not exist" % (v, k))
                return open(v).read()

        raise Exception("artifact %s not found" % name)

    def intrinsic_get_script_env(self, obj=None, name=None, varname=None, method=None):
        if obj!="SELF":
            raise Exception("only SELF is supported for get_artifact first arg")
        if method!="LOCAL_FILE":
            raise Exception("only LOCAL_FILE is supported for get_artifact fourth arg")

        for (k,v) in self.nodetemplate.entity_tpl.get("artifacts", {}).items():
            if k == name:
                if not os.path.exists(v):
                    raise Exception("Artifact local file %s for artifact %s does not exist" % (v, k))
                return subprocess.Popen('/bin/bash -c "source %s &> /dev/null; echo \\$%s"' % (v, varname), shell=True, stdout=subprocess.PIPE).stdout.read().strip()

        raise Exception("artifact %s not found" % name)

    def intrinsic_path_join(self, obj=None, name=None, varname=None, method=None):
        if obj!="SELF":
            raise Exception("only SELF is supported for get_artifact first arg")
        if method!="ENV_VAR":
            raise Exception("only ENV_VAR is supported for get_artifact fourth arg")

        if not (name in os.environ):
            raise Exception("environment variable %s not found" % name)

        return os.path.join(os.environ[name], varname)

    def try_intrinsic_function(self, v):
        try:
            jsv = v.replace("'", '"')
            jsv = json.loads(jsv)
        except:
            #import traceback
            #traceback.print_exc()
            return v

        if type(jsv)!=dict:
            return v

        if "get_artifact" in jsv:
            return self.intrinsic_get_artifact(*jsv["get_artifact"])
        elif "get_script_env" in jsv:
            return self.intrinsic_get_script_env(*jsv["get_script_env"])
        elif "path_join" in jsv:
            return self.intrinsic_path_join(*jsv["path_join"])

        return v

    def get_xos_args(self):
        args = {}

        if self.name_field:
            args[self.name_field] = self.obj_name

        # copy simple string properties from the template into the arguments
        for prop in self.copyin_props:
            v = self.get_property(prop)

            v = self.try_intrinsic_function(v)

            if v is not None:
                args[prop] = v

        return args

    def create(self):
        xos_args = self.get_xos_args()
        xos_obj = self.xos_model(**xos_args)
        if self.user:
            xos_obj.caller = self.user
        xos_obj.save()

        self.info("Created %s '%s'" % (self.xos_model.__name__,str(xos_obj)))

        self.postprocess(xos_obj)

    def update(self, obj):
        xos_args = self.get_xos_args()
        for (k,v) in xos_args.items():
            setattr(obj, k, v)
        self.postprocess(obj)
        obj.save()

    def delete(self, obj):
        if (self.can_delete(obj)):
            self.info("destroying object %s" % str(obj))
            obj.delete(purge=True)   # XXX TODO: turn off purge before production

    def info(self, s):
        self.engine.log(s)

