#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from subprocess import call
from telnetlib import Telnet
from tempfile import NamedTemporaryFile


# memcached server to check
MEMCACHED_SERVER = '127.0.0.1'
MEMCACHED_PORT = 11211
# containing zabbix_sender configuration
ZABBIX_CONFIG = '/etc/zabbix/zabbix_sender.conf'
LOGFILE = '/tmp/zabbix_memcached.log'


ITEMS = (
    'bytes',
    'cmd_get',
    'cmd_set',
    'curr_items',
    'curr_connections',
    'limit_maxbytes',
    'uptime',
    'get_hits',
    'get_misses',
)


########################################################################
class Item(object):
    """Simple data container"""

    #----------------------------------------------------------------------
    def __init__(self, key, value):
        self.key = key
        self.value = value


########################################################################
class MemcachedStatsReader(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, server, port):
        self._server = server
        self._port = port
        self._stats_raw = None
        self._stats = None

    #----------------------------------------------------------------------
    def read(self):
        self._read_stats()
        self._parse_stats()
        return self._stats

    #----------------------------------------------------------------------
    def _read_stats(self):
        connection = Telnet(self._server, self._port)
        connection.write('stats\n')
        connection.write('quit\n')
        self._stats_raw = connection.read_all()

    #----------------------------------------------------------------------
    def _parse_stats(self):
        self._stats = list()
        for line in self._stats_raw.splitlines():
            if not line.startswith('STAT'):
                continue
            parts = line.split()
            if not parts[1] in ITEMS:
                continue
            item = Item(parts[1], parts[2])
            self._stats.append(item)


########################################################################
class ZabbixSender(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config, logfile):
        self._config = config
        self._logfile = logfile
        self._tempfile = None

    #----------------------------------------------------------------------
    def send(self, stats):
        self._write_temporary_file(stats)
        self._send_data_to_zabbix()

    #----------------------------------------------------------------------
    def _write_temporary_file(self, stats):
        self._tempfile = NamedTemporaryFile()
        for item in stats:
            self._tempfile.write(u'- memcached[%s] %s\n' % (item.key, item.value))

        self._tempfile.flush()

    #----------------------------------------------------------------------
    def _send_data_to_zabbix(self):
        cmd = [u'zabbix_sender', u'-c', self._config, u'-i', self._tempfile.name]
        logfile = open(self._logfile, 'a')
        call(cmd, stdout=logfile)
        logfile.close()
        self._tempfile.close()


#----------------------------------------------------------------------
def main():
    reader = MemcachedStatsReader(MEMCACHED_SERVER, MEMCACHED_PORT)
    items = reader.read()

    sender = ZabbixSender(ZABBIX_CONFIG, LOGFILE)
    sender.send(items)


if __name__ == '__main__':
    main()
