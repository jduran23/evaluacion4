
#https://github.com/jduran23/evaluacion_4.git

import json
import conf
from sys import exit
from acitoolkit.acitoolkit import *

APIC_HOST = "https://10.10.20.14"
APIC_USERNAME = conf(conf.usuario)
APIC_PASSWORD = conf(conf.clave)

tenant_name = "Usach_2"
vrf_name = "Usach_VRF"
bridge_domain_name = "Usach_WEB_BD"
bridge_domain_subnet = "192.168.10.1/24"
bridge_domain_subnet_name = "Usach_Web_Subnet"
app_prof_name = "Usach_Web_APP"
epg_portal_name = "Usach_Web_EPG"
epg_users_name = "Usach_BBDD__EPG"

# Create Tenant
tenant = Tenant(tenant_name)

# Create VRF
vrf = Context(vrf_name, tenant)

# Create Bridge Domain
bridge_domain = BridgeDomain(bridge_domain_name, tenant)
bridge_domain.add_context(vrf)

# Create public subnet and assign gateway
subnet = Subnet(bridge_domain_subnet_name, bridge_domain)
subnet.set_scope("public")
subnet.set_addr(bridge_domain_subnet)

# Create http filter and filter entry
filter_http = Filter("http", tenant)
filter_entry_tcp80 = FilterEntry(
    "tcp-80", filter_http, etherT="ip", prot="tcp", dFromPort="http", dToPort="http"
)

# Create Portal contract and use http filter
contract_portal = Contract("Portal", tenant)
contract_subject_http = ContractSubject("http", contract_portal)
contract_subject_http.add_filter(filter_http)

# Create Application Profile
app_profile = AppProfile(app_prof_name, tenant)

# Create Portal EPG and associate bridge domain and contracts
epg_portal = EPG(epg_portal_name, app_profile)
epg_portal.add_bd(bridge_domain)
epg_portal.provide(contract_portal)

# Create Users EPG and associate bridge domain and contracts
epg_users = EPG(epg_users_name, app_profile)
epg_users.add_bd(bridge_domain)
epg_users.consume(contract_portal)

print(f'Candidate Tenant configuration as JSON payload:\n {tenant.get_json()}')

# Connect and push configuration to APIC
session = Session(APIC_HOST, APIC_USERNAME, APIC_PASSWORD)
session.login()

resp = session.push_to_apic(tenant.get_url(), data=tenant.get_json())

if not resp.ok:
    print(f'API return code {resp.status_code} with message {resp.text}')
    exit(1)
