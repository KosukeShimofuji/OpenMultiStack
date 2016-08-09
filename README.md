# OpenMultiStack

OpenMultiStackは複数のOpenStack Providerをまたがってcomptue nodeの作成や破棄といった操作と管理を一元化するために作成しました。OpenMultiStackには次のような機能が実装されています。

 * OpenStackアカウントの集約
 * WebインターフェイスからOpenStack Providerのアカウント登録できる
 * Webインターフェイスからインスタンス情報の一覧を見ることができる
 * いずれかのOpenStack Providerにメンテナンスや不具合があったとしても他のOpenStack Providerを使って可能な限り確実にインスタンスを立ち上げるように努力する
 * クライアントとの通信はRESTful APIで行う

# 検証環境のデプロイ

 * 検証環境の作成

```
$ cd OpenMultiStack/ansible
$ vagrant up
$ ansible-playbook -i development site.yml
```

 * デプロイ用の構成を作成

```
$ sudo mkdir -p /var/www/OpenMultiStack/
$ cd ~/
$ git clone git@github.com:KosukeShimofuji/OpenMultiStack.git
$ cd OpenMultiStack
```

 * pyenvのインストール

```
$ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
$ cat ~/.bash_profile
export PYENV_ROOT=/home/kosuke/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)"
```

 * Python 3.5.1のインストール

```
$ CFLAGS="-fPIC" pyenv install 3.5.1
$ pyenv global 3.5.1
```

 * Pythonモジュールのインストール

```
$ pip install --upgrade pip
$ pip install django
$ pip install psycopg2 # djangoからpostgresqlを操作するために必要
$ pip install djangorestframework
$ pip install django-filter 
$ pip install python-openstackclient
$ pip install python-neutronclient
$ pip install celery
$ pip install django-celery
$ pip install sqlalchemy
```

 * モデルのマイグレート

```
$ cd OpenMultiStack/django_project/
$ python manage.py makemigrations open_multi_stack
$ python manage.py migrate
```

 * django test serverの起動

```
$ python manage.py runserver 0.0.0.0:8000
```

 * celery serverの起動

```
$ celery -A django_project worker -l info -c 1
```

 * 管理ユーザの作成

```
$ python manage.py createsuperuser
Username (leave blank to use 'kosuke'): kosuke
Email address: kosuke.shimofuji@gmail.com
Password:
Password (again):
Superuser created successfully.
```

 * mod_wsgiのインストール

```
$ sudo apt-get install apache2-dev
$ wget https://pypi.python.org/packages/c3/4e/f9bd165369642344e8fdbe78c7e820143f73d3beabfba71365f27ee5e4d3/mod_wsgi-4.5.3.tar.gz
$ tar zxvf mod_wsgi-4.5.3.tar.gz
$ cd mod_wsgi-4.5.3
$ ./configure --with-python=/home/kosuke/.pyenv/versions/3.5.1/bin/python
$ make
$ sudo make install
$ sudo sh -c 'cat > /etc/apache2/mods-available/wsgi.load'
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
CTRL+C
$ sudo a2enmod wsgi
```

 * 静的ファイルをを集める

```
$ sudo mkdir -p /var/www/OpenMultiStack/static/
$ cat >>  OpenMultiStack/django_project/django_project/settings.py
STATIC_ROOT = '/var/www/OpenMultiStack/static/'
CTRL+C
$ sudo chown kosuke:kosuke /var/www/OpenMultiStack/static/
$ python manage.py collectstatic
$ sudo chown www-data:www-data -R /var/www/OpenMultiStack/static/
```

 * Apache用の設定ファイルを用意する

```
# cat /etc/apache2/sites-available/open_multi_stack.conf
WSGISocketPrefix /var/run/wsgi

<VirtualHost *:80>

  ServerName   oms.test

  WSGIScriptReloading On
  WSGIDaemonProcess  oms.test python-path=/home/kosuke/OpenMultiStack/django_project:/home/kosuke/OpenMultiStack/.pyenv/versions/3.5.1/lib/python3.5/site-packages python-home=/home/kosuke/.pyenv/versions/3.5.1 user=www-data group=www-data processes=2 threads=25
  WSGIProcessGroup oms.test
  WSGIScriptAlias    / /home/kosuke/OpenMultiStack/django_project/django_project/wsgi.py

  Alias /static/ /var/www/OpenMultiStack/static/

  <Directory /var/www/OpenMultiStack/static>
  Order deny,allow
  Allow from all
  </Directory>

  <Directory "/home/kosuke/OpenMultiStack/django_project/django_project">
  <Files wsgi.py>
        Require all granted
  </Files>
  </Directory>

  ErrorLog /var/log/apache2/django-error.log
  CustomLog /var/log/apache2/django-access.log combined

</VirtualHost>
```

 * celeryの起動スクリプトを作成する

```
$ wget https://raw.githubusercontent.com/celery/celery/3.1/extra/generic-init.d/celeryd -O /etc/init.d/celeryd
$ chmod 700 /etc/init.d/celeryd
```

 * /etc/default/celerydを用意する

```
$ sudo sh -c 'cat > /etc/default/celeryd'
# Names of nodes to start
#   most people will only start one node:
CELERYD_NODES="worker1"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS (see `celery multi --help` for examples):
#CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
#CELERYD_NODES=10

# Absolute or relative path to the 'celery' command:
#CELERY_BIN="/usr/local/bin/celery"
#CELERY_BIN="/virtualenvs/def/bin/celery"
CELERY_BIN="/home/kosuke/.pyenv/shims/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="django_project"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# Where to chdir at start.
CELERYD_CHDIR="/home/kosuke/OpenMultiStack/django_project/"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %N will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/home/kosuke/OpenMultiStack/log/celery/%N.log"
CELERYD_PID_FILE="/home/kosuke/OpenMultiStack/run/celery/%N.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists, e.g. nobody).
CELERYD_USER="kosuke"
CELERYD_GROUP="kosuke"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
``` 

 * celeryの起動

```
# /etc/init.d/celeryd start
```

 * Apacheの起動

```
# a2ensite open_multi_stack
# /etc/init.d/apache2 start
```

# 使い方

## OpenStackアカウントの追加

管理画面(http://oms.test/admin/)にログインしてAccountテーブルにOpenStackのアカウントを追加します。

## インスタンス立ち上げ命令

```
$ curl -X POST http://oms.test/api/queues/
{"id":1,"status":"REQUEST","regist_datetime":"2016-08-09T02:29:34.461432Z","instance":null}
```

## インスタンス立ち上げ命令の進捗

```
$ curl -X GET http://oms.test/api/queues/1/
{"id":1,"status":"RUN","regist_datetime":"2016-08-09T02:29:34.461432Z","instance":{"id":1,"name":"133-130-111-194","instance_id":"bec7c0ea-2262-4d73-aa6d-002d1e231103","ip_addr":"133.130.111.194","key_name":"gShakAACHA","key_raw":"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2KfxQQDKJ6jE6SofdMWJGLTng4Bk2mPZH0tyke3nimphJbcK\nONEKCGWga87eiqhX4xFRz1xDp8w4tESB8pfy1y4a+FlCHiE5H/XaTFjDgbZs9WJ1\n+B4gjIQZT2TROCpGsyTCbnKmwI+cyTanFGskwye6Tcw7JvBF7l9oL8psX6McxNIm\njGZknPpHZZWvLJ0zpq9zCbnJgPbiUOuD64N5hYRGE293CsXkDWUy6YEPtgKU85/Y\nqbN9CQIzxd0WlAkKYT+A5Ri2G1tnOTqEiBRKAevftaQ/pxkHIkKk2Y6IT+7UNrGX\n3Dnc5Gl13640SNeFsdgOx6GXPAauZtaEGFh8sQIDAQABAoIBAQDTlpCirya+vLAy\nFpVJ8XEG1AYWA1p7fnAZhBGMOw+ZunLN5ojxHBX0RWv6XboxKF9Mvylqnezk/ymR\nxCY0yfi79acZS/Kqgj/L2ssrLLUjBQo8S8ByZNnc4VXml8tMUt1hL1FDlG0OOjMg\nv2NFKa5peW8Vc5OBX76sIjkaE1LrwhAfiLWYBd4Iv90LvmU7i69dCXSaZxTtkzJs\nb5zMrJR36GyUhCvlrbPnYpZ+knEM2DmRYm8zqrUDDGxaXjI+eIDceBnAT4TWfiJz\nGXnMxLi4ljJ01b+1FmLCZ89FqxmFuWoW820kEQDmCFriXUr3r7cAFIoZc3Vj/S8I\nBLMSg9/BAoGBAPlpWrwfRA/pOpS5bVqFTvRaTTM3UrgZfWY67plo44ERFN5gPwsS\nKK6pT5oOiVxHPdCDUZXABHxoz+nRA/5qR+oBHPZEU+Cv0hvUMryaZo3jVoWvg1M7\nRBv0J8xowjWuOr07OeAiwY04RkCUlm42Zdong8Docw/+dbIW5FWrhNblAoGBAN5h\nFCtfDqC8JAU+sdJ6WERZ5lCCaKup90TTqfjogEGFMtS2oDyz5FmLWhjoHXGt/deV\nQ21+ZxWPukx9NpspBgE80j/pOShmGcswkempTgnzCdgdraYHv+WHfzuEOjkgPmr5\nv+u5KEveVl6LO24fIvG6kXGS2CNosHm9WSeQjoXdAoGAVHd0ri9cipLvLv0ZZsWs\n9p46dPTwg77GNEATHEtkeQqC6cjosOQmePiIJ+FybZkG+z3t/Gw6WLPabhJGavwt\nfLeBynlbesWwv5H+2NblknoCjGXjcOWqbFkkvVphI3LtG7caI6lBqYT8bdSkmZC8\nr8QgH83ZYfpIe9a637Sl2W0CgYBs3tA2D5qkvJdR7gi2x+jwxaaJId9Gs7Z3/rxH\nPOSVrzVciHBYZ6XS5PNeID1SC2GsKspRD8I9/xixG9ghDGuBLZqtaWvvSFU2cfft\nklK/cjoOkTETiNW89KIorCqpDw0f6Fe6evKsehSEwtt8pUfBWpqcJM0mQLmtUDMW\nuKHeDQKBgDMERcBoMU+tg6ByVp8Bk96Q91EJNVfK3i6M4/XDFBWJIelCESu0RXbb\nOSmxwX7UK2CF+Roj2/h5OlwvF9Rjy5nVsGaB/oSBAGaHFwgpHEWoqyEK1hbVIV1B\ns4OJDA7iMZ2Q9oRvXH8UHks83pnlcYCPAyqH3ZS8wFuUow6t7k8d\n-----END RSA PRIVATE KEY-----\n","account":{"provider":"conoha","region_name":"tyo1","tenant_name":"gnct26543406"}}}
```

## インスタンスの破棄命令

```
$ curl -X DELETE http://oms.test/api/queues/1/
$ curl -X GET http://oms.test/api/queues/1/
{"detail":"Not found."}kosukeshimofuji@PMAC280S ~ $
```


