sp=Create("ServiceProvider", {"account": "openstack", "name": "openstack", "enabled": True})
cp=Create("ContentProvider", {"account": "test", "name": "test", "enabled": True, "service_provider_id": sp})
ors=Create("OriginServer", {"url": "http://www.cs.arizona.edu/", "content_provider_id": cp, "service_type": "HyperCache"})
pre=Create("CDNPrefix", {"service": "HyperCache", "enabled": True, "content_provider_id": cp, "cdn_prefix": "test.vicci.org", "default_origin_server": "http://www.cs.arizona.edu/"})
