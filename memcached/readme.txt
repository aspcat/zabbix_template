ServerActive=[zabbix server ip]:[port];
SourceIP=[source ip];
Hostname=[hostname as configured in zabbix];
Then import the template on your Zabbix server and set up a cronjob for the zabbix_memcached.py script:

*/5 * * * *  zabbix /usr/bin/python /etc/zabbix/user/zabbix_memcached.py