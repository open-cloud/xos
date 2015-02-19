from xos.settings import STATISTICS_DRIVER

if (STATISTICS_DRIVER=="ceilometer"):
    from observer import ceilometer
    driver = ceilometer.CeilometerDriver()
elif (not STATISTICS_DRIVER) or (STATISTICS_DRIVER.lower() == "none"):
    # disabled
    driver = None
else:
    driver = None
    print "WARNING: Unknown statistics driver %s" % STATISTICS_DRIVER
