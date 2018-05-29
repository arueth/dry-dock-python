# dry-dock-python

A container with a set of python scripts for doing post-install configuration of Docker EE environments.

## Configuration

Configuration for the scripts is controlled by YAML files in the ```conf/``` directory. The configuration file parser can expand environment variables and also read Docker secrets.

```$ENVIRONMENT_VARIABLE```

```<%= SECRET( [ <absolute path to the secret> | <environment variable containing the path to the secret> ) %>```

### auth.yml
```
auth:
  backend: 'ldap'
  ldap:
    server_url: 'ldap://ldap.example.com'
    reader_dn: 'CN=reader,OU=Users,OU=Example,DC=example,DC=com'
    reader_password: <%= SECRET(/run/secrets/ldap_reader_password) %>
    tls_skip_verify: True
    start_tls: False
    no_simple_pagination: False
    jit_user_provisioning: True
  user_search_configs:
    base_dn: 'OU=Users,OU=Example,DC=example,DC=com'
    username_attr: 'uid'
    full_name_attr: 'cn'
    filter: '(&(objectClass=person)(objectClass=user))'
    scope_subtree: True
    match_group: False
    match_group_iterate: False
    match_group_dn: ''
    match_group_member_attr: ''
```

```backend```: ```[ 'ldap | 'mgmt' ]``` The authentication backend to use. Should be set to ```'ldap'``` to apply the configuration.

```ldap```:
* ```server_url```: URL of the LDAP server.
* ```reader_dn```: LDAP account used to search for users and groups. 
* ```reader_password```: LDAP password for the reader account. We recommend this account be a "read-only" account with minimal LDAP privileges just sufficient to search for users.
* ```tls_skip_verify```: ```[ True | False ]``` - Whether to skip verification of the server's certificate when establishing a TLS connection, not recommended unless testing on a secure network.
* ```start_tls```: ```[ True | False ]``` - Whether to use StartTLS to secure the connection to the server, ignored if server URL scheme is 'ldaps://'.
* ```no_simple_pagination```: ```[ True | False ]``` - The server does not support the Simple Paged Results control extension.
* ```jit_user_provisioning```: ```[ True | False ]``` - Whether to only create user accounts upon first login (recommended).

```user_search_configs```:
* ```base_dn```: The distinguished name of the element from which the LDAP server will search for users.
* ```username_attr```: The name of the attribute of the LDAP user element which should be selected as the username.
* ```full_name_attr```: The name of the attribute of the LDAP full name element.
* ```filter```: The LDAP search filter used to select user elements, may be left blank.
* ```scope_subtree```: ```[ True | False ]``` - A search scope defines how deep to search within the search base. One Level indicates a search of objects immediately subordinate to the base object, but does not include the base object itself. Subtree indicates a search of the base object and the entire subtree of which the base object distinguished name is the topmost object.
* ```match_group```: ```[ True | False ]``` - Whether to sync users using LDAP that also matches in the group specified below. This feature is helpful when the LDAP server does not support MemberOf overlay.
* ```match_group_iterate```: ```[ True | False ]``` - When using the Match Group Members option to sync users, this option syncs users by iterating over the target group's membership and makes a separate LDAP query for eachmember rather than using a broad user search filter. This option can be more efficient in situations where the number of members of the target group is significantly smaller than the number of users which would match a broad search filter.
* ```match_group_dn ```: The DN of the LDAP group.
* ```match_group_member_attr```: The name of the LDAP group entry attribute which corresponds to DN of members.

### certbot.yml
```
email: user@example.com 
always_apply_certs:
  dtr: False
  ucp: False 
aws:
  access_key_id: <%= SECRET(/run/secrets/aws_access_key_id) %>
  secret_access_key: <%= SECRET(/run/secrets/aws_secret_access_key) %>
```

```email```: email address that will receive certbot notifications.

```always_apply_certs```
* ```dtr```: ```[ True | False ]``` - Specify whether to apply the DTR certificates even if they haven't been renewed.
* ```ucp```: ```[ True | False ]``` - Specify whether to apply the UCP certificates even if they haven't been renewed.

```aws```
* ```access_key_id```: AWS access key ID to use for Route53 access. With the default configuration, this should be included as a secret with the target name 'aws_access_key_id'.
* ```secret_access_key```: AWS secret access key to use for Route53 access. With the default configuration, this should be included as a secret with the target name 'aws_secret_access_key'.

### dtr.yml
```
endpoint: 'dtr.example.com'
use_ssl: True
credentials:
  username: <%= SECRET(/run/secrets/dtr-username) %>
  password: <%= SECRET(/run/secrets/dtr-password) %>
ssl_certificate:
  domain_name: 'dtr.example.com'
  sans:
    - 'dtr-001.example.com'
    - 'dtr-002.example.com'
    - 'dtr-003.example.com'
```

```endpoint```: The DTR endpoint, this is the value used for the external URL.

```use_ssl```: ```[ True | False ]``` - specify whether to use SSL when communicating with DTR.

```credentials```
* ```username```: Username used to login to DTR. With the default configuration, this should be included as a secret with the target name 'dtr-username'.
* ```password```: Password used to login to DTR. With the default configuration, this should be included as a secret with the target name 'dtr-password'.

```ssl_certificate```:
* ```domain_name```: The primary domain name to be used on the DTR certificate.
* ```sans```: A list of SANs to include on the DTR certificate. If no SANs are required, the key and list can deleted.

### interlock.yml
```
http_port: 80
https_port: 8443
architecture: "x86_64"
```

```http_port```: HTTP port to use for Layer 7 routing.

```https_port```: HTTPS port to use for Layer 7 routing.

```architecture```: The system architecture that the Layer 7 Routing services will be run on. The L7 Routing service can still route to applications on different architecture.

### logging.yml
```
log_level: 'DEBUG'
```

```log_level```: ```[ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG' ]``` - specify the log level to set for logging.  

### ucp.yml
```
endpoint: 'ucp.example.com'
use_ssl: True
credentials:
  username: <%= SECRET(/run/secrets/ucp-username) %>
  password: <%= SECRET(/run/secrets/ucp-password) %>
ssl_certificate:
  domain_name: 'ucp.example.com'
  sans:
    - 'ucp-001.example.com'
    - 'ucp-002.example.com'
    - 'ucp-003.example.com'
```

```endpoint```: The UCP endpoint, this is the value used for the external URL.

```use_ssl```: ```[ True | False ]``` - specify whether to use SSL when communicating with UCP.

```credentials```
* ```username```: Username used to login to UCP. With the default configuration, this should be included as a secret with the target name 'ucp-username'.
* ```password```: Password used to login to UCP. With the default configuration, this should be included as a secret with the target name 'ucp-password'.

```ssl_certificate```:
* ```domain_name```: The primary domain name to be used on the UCP certificate.
* ```sans```: A list of SANs to include on the UCP certificate. If no SANs are required, the key and list can deleted.

## Usage
### cert-management-certbot.py
Required configuration files: certbot.yml, dtr.yml, logging.yml, ucp.yml
```
python /usr/src/dry-dock/bin/cert-management-certbot.py --conf_dir example
```

### configure-authentication-and-authorization.py
Required configuration files: auth.yml, logging.yml, ucp.yml
```
python /usr/src/dry-dock/bin/configure-authentication-and-authorization.py --conf_dir example
```


### configure-layer-7-routing.py
Required configuration files: interlock.yml, logging.yml, ucp.yml
```
python /usr/src/dry-dock/bin/configure-layer-7-routing.py --conf_dir example
```