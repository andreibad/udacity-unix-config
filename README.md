# udacity-unix-config

 IP address:54.184.77.212
 
 URL: http://54.184.77.212.xip.io/
 
 summary of software installed:
 
 updated ubuntu to latest packages
 apache2
 libapache2-mod-wsgi-py3
 postgresql
 pip
 
 summary of configurations made:
 https://gist.github.com/andreibad/b5c68fd7ec6d4860e9c8a538c768e64c <- my apache sites-enabled config 
 installed necessary python packages such as:
 flask
 sqlalchemy
 python-psycopg2/bionic
 created catalog user for postgres, set passwords for postgres and catalog users, and configured postgres to allow local access to postgres from those 2 users. 
 
 
 
 list of third-party resources used to complete this project:
 https://gist.github.com/shyamgupta/d8ba035403e8165510585b805cf64ee6
 https://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIDaemonProcess.html
 https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps#step-four-%E2%80%93-configure-and-enable-a-new-virtual-host
