import common

def test_unregister():
	common.run("subscription-manager unregister")

def test_uninstall_cert(audreyvars):
	cert_rpm = common.s_format("candlepin-cert-consumer-{KATELLO_HOST}", audreyvars)
	cmd = "rpm -e %s" % cert_rpm
	common.run(cmd)