# OpenMultiStack

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

1レコードがopenstack clientのenvrcに相当するテーブルを作成する

 * [コミット](https://github.com/KosukeShimofuji/OpenMultiStack/commit/d970757c623110a24fe464186b0f33066cbff70c)

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


# 参考文献

 * http://www.openstack.org/
 * http://docs.djangoproject.jp/en/latest/topics/signals.html
 * https://remotestance.com/blog/1271/
 * http://qiita.com/nk_yohn3301/items/a68d8df18867e2c40449
 * https://www.conoha.jp/agreement/
 * http://docs.openstack.org/ja/api/quick-start/content/index.html#authenticate
 * http://qiita.com/kimihiro_n/items/86e0a9e619720e57ecd8


