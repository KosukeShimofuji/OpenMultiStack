# OpenMultiStack

OpenMultiStackは複数のOpenStack Providerをまたがってcomptue nodeの作成や破棄といった操作と管理を一元化するために作成しました。

# Deploy

 * 検証環境の作成

```
$ cd OpenMultiStack/ansible
$ vagrant up
$ ansible-playbook -i development site.yml
```

 * デプロイ用のディレクトリを作成

```
# mkdir -p /var/www/
# cd /var/www/
# git clone git@github.com:KosukeShimofuji/OpenMultiStack.git
# cd OpenMultiStack
```

 * pyenvのインストール

```
# git clone https://github.com/yyuu/pyenv.git /var/www/OpenMultiStack/.pyenv
# cat ~/.bash_profile
export PYENV_ROOT=/var/www/OpenMultiStack/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)"
```

 * Python 3.5.1のインストール

```
# CFLAGS="-fPIC" pyenv install 3.5.1
# pyenv global 3.5.1
```

 * Pythonモジュールのインストール

```
# pip install --upgrade pip
# pip install django
# pip install psycopg2 # djangoからpostgresqlを操作するために必要
# pip install djangorestframework
# pip install django-filter 
# pip install python-openstackclient
# pip install python-neutronclient
# pip install celery
# pip install django-celery
# pip install sqlalchemy
```

 * モデルのマイグレート

```
# python manage.py makemigrations open_multi_stack
# python manage.py migrate
```

 * django test serverの起動

```
$ python manage.py runserver 0.0.0.0:8000
```

 * celery serverの起動

```
# celery -A django_project worker -l info -c 1
```

 * 管理ユーザの作成

```
# python manage.py createsuperuser
Username (leave blank to use 'kosuke'): kosuke
Email address: kosuke.shimofuji@gmail.com
Password:
Password (again):
Superuser created successfully.
```

 * mod_wsgiのインストール

```
# apt-get install apache2-dev
# wget https://pypi.python.org/packages/c3/4e/f9bd165369642344e8fdbe78c7e820143f73d3beabfba71365f27ee5e4d3/mod_wsgi-4.5.3.tar.gz
# tar zxvf mod_wsgi-4.5.3.tar.gz
# cd mod_wsgi-4.5.3
# ./configure --with-python=/var/www/OpenMultiStack/.pyenv/versions/3.5.1/bin/python
#  make
#  make install
# cat /etc/apache2/mods-available/wsgi.load
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
# a2enmod wsgi
```

 * Apache用の設定ファイルを用意する。 

/etc/apache2/sites-available/open_multi_stack.conf

```
WSGISocketPrefix /var/run/wsgi

<VirtualHost *:80>

  ServerName   oms.test

  WSGIScriptReloading On
  WSGIDaemonProcess  oms.test python-path=/var/www/OpenMultiStack/django_project:/var/www/OpenMultiStack/.pyenv/versions/3.5.1/lib/python3.5/site-packages python-home=/var/www/OpenMultiStack/.pyenv/versions/3.5.1 user=www-data group=www-data processes=2 threads=25
  WSGIProcessGroup oms.test
  WSGIScriptAlias    / /var/www/OpenMultiStack/django_project/django_project/wsgi.py

  Alias /static/ /var/www/OpenMultiStack/static/

  <Directory /var/www/OpenMultiStack/static>
  Order deny,allow
  Allow from all
  </Directory>

  <Directory "/var/www/OpenMultiStack/django_project/django_project">
  <Files wsgi.py>
        Require all granted
  </Files>
  </Directory>

  ErrorLog /var/log/apache2/django-error.log
  CustomLog /var/log/apache2/django-access.log combined

</VirtualHost>
```

 * 静的ファイルをを集める。

```
python manage.py collectstatic
```


## Issue

 * 著名なOpenStackプロバイダは1リージョンにつき20インスタンスまでの制限が存在する

## Wish

 * 複数のリージョンを意識することなくインスタンスを立ち上げたい
 * 複数のOpenStackプロバイダを意識することなくインスタンスを立ち上げたい
 * 複数クライアントから送出されるインスタンス立ち上げ命令、インスタンス破棄命令を集約したい
 * RESTFul APIでやり取りをしたい
 * 認証されたクライアントのみからの命令を処理したい

## Preparation for Development

 * install python 3.5.1

```
$ pyenv install 3.5.1
```

 * setting virtualenv for OpenMultiStack

```
$ pyenv virtualenv 3.5.1 OpenMultiStack
$ pyenv global OpenMultiStack
```

 * install related Django python module

```
$ pip install --upgrade pip
$ pip install django
$ pip install psycopg2 # djangoからpostgresqlを操作するために必要
$ pip install djangorestframework
$ pip install django-filter 
```

 * install openstack client

```
$ pip install python-openstackclient
```

## Create Django project and app

```
$ django-admin startproject django_project
$ cd django_project
$ python manage.py startapp open_multi_stack
$ tree
.
├── django_project
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-35.pyc
│   │   └── settings.cpython-35.pyc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── open_multi_stack
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py

4 directories, 14 files
```

## Definition of the model

### open_stack_account 

 * [models.py](https://github.com/KosukeShimofuji/OpenMultiStack/blob/master/django_project/open_multi_stack/models.py)にモデルを定義していく。

### create migrate script 

```
$ python manage.py makemigrations open_multi_stack
Migrations for 'open_multi_stack':
  0001_initial.py:
    - Create model OpenStackAccount
```

### view sqlmigrate

```
$ python manage.py sqlmigrate open_multi_stack 0001
BEGIN;
--
-- Create model OpenStackAccount
--
CREATE TABLE "open_multi_stack_openstackaccount" ("id" serial NOT NULL PRIMARY KEY, "username" varchar(128) NOT NULL, "tenantname" varchar(128) NOT NULL, "tenant_id" varchar(128) NOT NULL, "password" varchar(128) NOT NULL, "auth_url" varchar(128) NOT NULL, "version" varchar(128) NOT NULL, "status" varchar(12) NOT NULL, "provider" varchar(128) NOT NULL);

COMMIT;
```

### execute migration

```
$ python manage.py migrate
Operations to perform:
  Apply all migrations: sessions, contenttypes, admin, auth, open_multi_stack
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying open_multi_stack.0001_initial... OK
  Applying sessions.0001_initial... OK
```

### 作成されたテーブルの確認

```
$ psql -h127.0.0.1 -Udjango
ユーザ django のパスワード:
psql (9.4.8)
SSL接続(プロトコル: TLSv1.2, 暗号化方式: ECDHE-RSA-AES256-GCM-SHA384, ビット長: 256, 圧縮: オフ)
"help" でヘルプを表示します.

django=> \dt
                         リレーションの一覧
 スキーマ |                名前                 |    型    | 所有者
----------+-------------------------------------+----------+--------
 public   | auth_group                          | テーブル | django
 public   | auth_group_permissions              | テーブル | django
 public   | auth_permission                     | テーブル | django
 public   | auth_user                           | テーブル | django
 public   | auth_user_groups                    | テーブル | django
 public   | auth_user_user_permissions          | テーブル | django
 public   | django_admin_log                    | テーブル | django
 public   | django_content_type                 | テーブル | django
 public   | django_migrations                   | テーブル | django
 public   | django_session                      | テーブル | django
 public   | open_multi_stack_openstackaccount | テーブル | django
(11 行)

django=> \d open_multi_stack_openstackaccount
                                 テーブル "public.open_multi_stack_openstackaccount"
     列     |           型           |                                      修飾語
------------+------------------------+----------------------------------------------------------------------------------
 id         | integer                | not null default nextval('open_multi_stack_open_stack_account_id_seq'::regclass)
 username   | character varying(128) | not null
 tenantname | character varying(128) | not null
 tenant_id  | character varying(128) | not null
 password   | character varying(128) | not null
 auth_url   | character varying(128) | not null
 version    | character varying(128) | not null
 status     | character varying(12)  | not null
 provider   | character varying(128) | not null
インデックス:
    "open_multi_stack_open_stack_account_pkey" PRIMARY KEY, btree (id)
```

## 管理画面からデータベースを編集できるようにする

 * 管理アカウントの作成

```
$ python manage.py createsuperuser
Username (leave blank to use 'kosuke'): admin
Email address: kosuke.shimofuji@gmail.com
Password:
Password (again):
Superuser created successfully.
```

 * 作成したアカウント情報

```
admin:KraddInkasEatUljOundirbagphidab5
```

 * 開発用サーバの起動

```
$ python manage.py runserver 0.0.0.0:8000
```


 * 管理画面へのアクセス

http://openmultistack.test:8000/admin/

 * 管理画面のインデックスページ

![django admin index](https://raw.githubusercontent.com/KosukeShimofuji/OpenMultiStack/image/django_admin_index.png)

 * OpenStackAccountテーブルの編集ページ
 
![django admin openstackaccount edit page](https://raw.githubusercontent.com/KosukeShimofuji/OpenMultiStack/image/django_admin_edit_openstackaccount.png)

# 参考文献

 * http://www.openstack.org/
 * http://docs.djangoproject.jp/en/latest/topics/signals.html
 * https://remotestance.com/blog/1271/
 * http://qiita.com/nk_yohn3301/items/a68d8df18867e2c40449
 * https://www.conoha.jp/agreement/
 * http://docs.openstack.org/ja/api/quick-start/content/index.html#authenticate
 * http://qiita.com/kimihiro_n/items/86e0a9e619720e57ecd8
 * http://docs.openstack.org/ja/user-guide/sdk.html
 * http://unching-star.hatenablog.jp/entry/2015/12/02/113459#f-58c78a61
 * https://www.digitalocean.com/community/tutorials/how-to-run-django-with-mod_wsgi-and-apache-with-a-virtualenv-python-environment-on-a-debian-vps
 * http://hideharaaws.hatenablog.com/entry/2014/12/12/230825
