# MPASSid Auth Data service
![](http://img.shields.io/:license-mit-blue.svg)
![](https://travis-ci.org/CSCfi/MPASSid-data.svg?branch=master)

MPASSid Auth Data service is a proxy for actual data store, or multiple datastores, which contain user
identity and role information.

Based on Educloud Alliance reference implementation. See [Educloud  Alliance](http://docs.educloudalliance.org "Educloud alliance") for more information.


## Contribution

Developer information and more detailed documentation will be available in <http://www.mpass.fi> 

## Quick install guide
Currently ansible scripts only support single server installation. Alll the components are installed  in one server (database, httpd, MPASSid data component) 
### Prerequisites

RedHat/CentOS 7 server (ie. virtual machine) with root privileges.


### Installation steps
##### 1 Download just the ansible scripts (**ansible.tar.gz**) or clone this entire repository

##### 2 Configure installation parameters in ...roles/vars/secure.yml. Parametters are

| Parameter | Description| 
|----------| -----------|
| app_root  |Directory where applicattion is installed|
| git_repo | Temporary directory used during installation|
| db_name | PostgreSQL database name |
| db_user | PostgreSQL database username |
| db_pass | PostrgeSQL pasword for username |
| db_serv | IP/FQDN from PostgreSQL database server |
| ServerName | Apache configuration Servername |
| ServerAdmin | Apache admin contact email |
| SSLCertificateFile | Apache path to SSL certificate |
|  SSLCertificateKeyFile | Apache path to SSL private key |

##### 3  Login to your server and run ansible
`$ sudo  ansible-playbook -i "localhost," -c local mpass-data.yml`

##### 4 Create Django administrator account
Activate python virtual environment.
`$ cd {app_root} `
`$ source env/bin/activate`

Change to mpass-data home and run Django management utils
 `$ cd mpass-data`
 `$ python manage.py createsuperuser `

#####  5 Create user for API-access

Login to Django administration <https://servername.fi/sysdamin/>  using username/password created above and create new user.
+ Select *Users* -> *Add user+* 
+ Give username for example: *api_user* Click *Save* and again *Save*
+ Go back to main screen 
+ Select *Tokens*  -> *Add Token +*
+ Select username you created and click *Save*

![](https://drive.google.com/file/d/19uixudlbA8bfM4GplJegEyoK6WrGcfb3/view)


##### 6 Test API connection 
Test API  for example using Curl
`$ curl -k --header "Authorization: Token c2d748e9e453e42a80e8c45289da4642738d1af5" https://127.0.0.1/api/1/query?ldap_test=pvirtane`

Above query  should return
``` JSON
{"username":"MPASSOID.53b1af17cb284998638b5","attributes":[{"name":"legacyId","value":"f0ba7691aeff3ef2302d6edce5303641"},{"name":"municipalityCode","value":"1"},{"name":"ldap_test","value":"pvirtane"}],"first_name":"Pekka-Testi","last_name":"Virtanen","roles":[{"municipality":"KuntaYksi","school":"DemolaTestSchool","role":"Oppilas","group":"9A"}]}
```

###End
