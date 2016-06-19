import filecmp
import subprocess
import tempfile
from subprocess import check_output, CalledProcessError

from os.path import join
from syncloud_app import util
from syncloud_app.logger import get_logger

#from cryptography import x509
#from cryptography.hazmat.backends import default_backend
#import datetime


class Tls:
    def __init__(self, platform_config, user_platform_config, info, nginx):
        self.info = info
        self.log = get_logger('tls')
        self.platform_config = platform_config
        self.user_platform_config = user_platform_config
        self.nginx = nginx
        self.openssl_bin = '{0}/lib/openssl/bin/openssl'.format(self.platform_config.app_dir())
        self.certbot_bin = '{0}/lib/certbot/bin/certbot'.format(self.platform_config.app_dir())
        self.log_dir = self.platform_config.get_log_root()
        self.certbot_config_dir = join(self.platform_config.data_dir(), 'certbot')

    #def cert_info(self):
        #cert_data = open(self.platform_config.get_ssl_certificate_file(), 'r').read()
        #cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        #self.log.info('issuer: {0}'.format(cert.issuer))
        #days_left = (cert.not_valid_after - datetime.datetime.now()).days
        #self.log.info('days left: {0}'.format(days_left))

    def generate_real_certificate(self):
        
        #self.cert_info()

        if (not self.platform_config.is_certbot_enabled()):
            return self.log.info('certbot is not enabled, not running')

        try:

            self.log.info('running certbot')
            output = check_output(
                '{0} --logs-dir={1} --config-dir={2} --agree-tos --email {3} '
                'certonly --cert-path {4} --key-path {5} '
                '--webroot --webroot-path {6} '
                '-d {7} '.format(self.certbot_bin,
                                self.log_dir,
                                self.certbot_config_dir,
                                self.user_platform_config.get_user_email(),
                                self.platform_config.get_ssl_certificate_file(),
                                self.platform_config.get_ssl_key_file(),
                                self.platform_config.www_root(),
                                self.info.domain()), stderr=subprocess.STDOUT, shell=True)

            self.log.info(output)
            #self.cert_info()
            self.nginx.reload()

        except CalledProcessError, e:
            self.log.warn('unable to generate real certificate: {0}'.format(e))
            self.log.warn(e.output)

    def generate_self_signed_certificate(self):

        key_file = self.platform_config.get_ssl_key_file()
        try:

            output = check_output('{0} genrsa -out {1} 4096 2>&1'.format(self.openssl_bin, key_file), stderr=subprocess.STDOUT, shell=True)
            self.log.info(output)
        except CalledProcessError, e:
            self.log.warn('unable to generate self-signed certificate: {0}'.format(e))
            self.log.warn(e.output)
            raise e

        cert_file = self.platform_config.get_ssl_certificate_file()
        fd, temp_configfile = tempfile.mkstemp()
        util.transform_file(self.platform_config.get_openssl_config(), temp_configfile, {'domain': self.info.domain()})
        cmd = '{0} req -new -x509 -days 3650 -config {1} -key {2} -out {3} 2>&1'.format(self.openssl_bin, temp_configfile, key_file, cert_file)
        self.log.info('running: ' + cmd)
        output = check_output(cmd, shell=True)
        self.log.info(output)

        self.nginx.reload()

    def is_default_certificate_installed(self):
        return filecmp.cmp(
            self.platform_config.get_ssl_certificate_file(),
            self.platform_config.get_default_ssl_certificate_file())
