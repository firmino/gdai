# GDAI

## 1. Commands

**Including application running on port 8000** 
'''sh
docker-compose up 
'''


'''
certbot certonly --standalone -d gdai.site -d www.gdai.site  --email firminodefaria@gmail.com --agree-tos --non-interactive  --config-dir ./certbot/config   --work-dir ./certbot/work   --logs-dir ./certbot/logs
'''