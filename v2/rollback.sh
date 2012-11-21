sudo killall redis-server
sudo cp ~/redis-backups/211112.rdb /var/lib/redis/dump.rdb
sudo redis-server /etc/redis/redis.conf &