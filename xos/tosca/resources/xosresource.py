import os
import pdb
import json
import subprocess

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
            raise Exception("Failed to find requirement in %s using relationship %s" % (self.nodetemplate.name, relationship_name))

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

    def get_xos_object(self, cls, throw_exception=True, **kwargs):
        objs = cls.objects.filter(**kwargs)
        if not objs:
            if throw_exception:
                raise Exception("Failed to find %s filtered by %s" % (cls.__name__, str(kwargs)))
            return None
        return objs[0]

    def get_existing_objs(self):
        return self.xos_model.objects.filter(**{self.name_field: self.nodetemplate.name})

    def get_xos_args(self):
        return {}

    def get_model_class_name(self):
        return self.xos_model.__name__

    def create_or_update(self):
        existing_objs = self.get_existing_objs()
        if existing_objs:
            self.info("%s %s already exists" % (self.get_model_class_name(), self.nodetemplate.name))
            self.update(existing_objs[0])
        else:
            self.create()

    def can_delete(self, obj):
        return True

    def postprocess_privileges(self, roleclass, privclass, rolemap, obj, toFieldName):
        for (rel, role) in rolemap:
            for email in self.get_requirements(rel):
                role = self.get_xos_object(roleclass, role=role)
                user = self.get_xos_object(User, email=email)
                if not privclass.objects.filter(user=user, role=role, **{toFieldName: obj}):
                    sp = privclass(user=user, role=role, **{toFieldName: obj})
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

        return v

    def get_xos_args(self):
        args = {}

        if self.name_field:
            args[self.name_field] = self.nodetemplate.name

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

