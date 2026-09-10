from urllib.parse import uses_fragment
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from numpy import empty
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from .models import User
from .serializers import UserSerializer

from datetime import datetime
from datetime import timedelta

import hashlib
import psutil
import cpuinfo
import os
import time
import signal
import subprocess
import re
import json
import secrets

from django.contrib.auth.hashers import make_password, check_password


# Create your views here.

processid = False

SESSION_TTL = 12 * 60 * 60


def is_logged_in(request):
    """
    Checks if the cookie value is present in the database and has not expired.
    """
    req_data = request.data or {}
    cookie_val = req_data.get("cookie")
    if not cookie_val:
        return False
    users = User.objects.filter(cookie__startswith=cookie_val + ":")
    if not users:
        return False
    stored = users[0].cookie
    try:
        expires = int(stored.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return False
    return int(time.time()) < expires

@api_view(['POST'])
def login(request):
    """
    If user exists, set a cookie to log in
    """
    req_data = request.data

    users = User.objects.all()
    user = list(users.filter(username=req_data.get("username")))
    if user:
        user = user[0]
        if not check_password(req_data.get("password") or "", user.password):
            return Response(False)
        token = secrets.token_urlsafe(32)
        expires = int(time.time()) + SESSION_TTL
        user.cookie = "{}:{}".format(token, expires)
        user.save()

        data = {
            "cookie": token
        }

        return Response(data)

    else:
        print("Incorrect Credentials")
        return Response(False)

@api_view(['POST'])
def register(request):
    """
    Register new user
    """
    req_data = request.data

    users = User.objects.all()
    user = list(users.filter(username=req_data.get("username")))
    if user:
        return Response(False) #if username exists, return False
    else:
        store_corporate = User(username=req_data.get("username"),
                               password=make_password(req_data.get("password") or ""))
        store_corporate.save()
        return Response(True)

@api_view(["GET"])
def test_api(request):
    """Endpoint to check if the endpoint works or not"""
    data = {
        "status" : "ep_working"
    }
    return Response(data)

@api_view(["POST"])
def get_uptime(request):
    """Endpoint to get the uptime of the system
        Returns:
            json object of "uptime" mapped to uptime in seconds
    """
    if not is_logged_in(request):
        raise Http404
    try:
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        uptime = str(timedelta(seconds=uptime.seconds))
        data = {
            "status": 200,
            "uptime": uptime
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404

@api_view(["POST"])
def get_processor(request):
    """Endpoint to get the uptime of the system
        Returns:
            json object of information containing bits,count, brand, frequency, l3 cache size, l2 cache size, l1 cache size, l1 instruction cache size and vendor
    """
    if not is_logged_in(request):
        raise Http404
    try:
        info = cpuinfo.get_cpu_info()
        data = {
            "status": 200,
            "bits": info["bits"],
            "count": info["count"],
            "brand": info["brand_raw"],
            "hz_advertised": info["hz_advertised"][0],
            "l3_cache_size": info["l3_cache_size"],
            "l2_cache_size": info["l2_cache_size"],
            "l1_data_cache_size": info["l1_data_cache_size"],
            "l1_instruction_cache_size": info["l1_instruction_cache_size"],
            "vendor_id": info["vendor_id_raw"]
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_cpu(request):
    """Endpoint to get information regarding cpu
        Returns:
            json object of information containing percentage usage, number of cpus, percentage usage per cpu
    """
    if not is_logged_in(request):
        raise Http404
    try:
        percent = psutil.cpu_percent()
        count = psutil.cpu_count()
        percpu = psutil.cpu_percent(interval=1, percpu=True)
        data = {
            "status": 200,
            "percentage": percent,
            "count": count,
            "per_cpu": percpu
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_username(request):
    """Endpoint to get information of user logged in
        Returns:
            username of logged in user
    """
    if not is_logged_in(request):
        raise Http404
    try:
        username = os.getlogin()
        data = {
            "status": 200,
            "username": username
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_ram(request):
    """Endpoint to get information regarding ram
        Returns:
            json object of information containing total ram of the system, percentage used, amount used and amount free
    """
    if not is_logged_in(request):
        raise Http404
    try:
        ram = psutil.virtual_memory()
        total = float(ram.total / 1073741824)
        percent = ram.percent
        used = float(ram.used / 1073741824)
        free = float(ram.available / 1073741824)
        data = {
            "status": 200,
            "total": float("{0: .2f}".format(total)),
            "percent": percent,
            "used": float("{0: .2f}".format(used)),
            "free": float("{0: .2f}".format(free))
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_swap(request):
    """Endpoint to get information regarding swap
        Returns:
            json object of information containing total swap memory of the system, percentage used, amount used and amount free
    """
    if not is_logged_in(request):
        raise Http404
    try:
        swap = psutil.swap_memory()
        total = float(swap.total / 1073741824)
        percent = swap.percent
        used = float(swap.used / 1073741824)
        free = float(swap.free / 1073741824)
        data = {
            "status": 200,
            "total": float("{0: .2f}".format(total)),
            "percent": percent,
            "used": float("{0: .2f}".format(used)),
            "free": float("{0: .2f}".format(free))
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_hdd(request):
    """Endpoint to get information regarding ram
        Returns:
            json object of information containing hdd device, path, type of formatting, total hdd available, percentage used, amount used and amount free
    """
    if not is_logged_in(request):
        raise Http404
    try:
        hdd = psutil.disk_partitions()
        data = []
        for each in hdd:
            device = each.device
            path = each.mountpoint
            fstype = each.fstype

            drive = psutil.disk_usage(path)
            total = drive.total
            total = total / 1000000000
            used = drive.used
            used = used / 1000000000
            free = drive.free
            free = free / 1000000000
            percent = drive.percent
            drives = {
                "device": device,
                "path": path,
                "fstype": fstype,
                "total": float("{0: .2f}".format(total)),
                "used": float("{0: .2f}".format(used)),
                "free": float("{0: .2f}".format(free)),
                "percent": percent
            }
            data.append(drives)
        if data:
            data_dict = {
                "status": 200,
                "data": data,
            }
            return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_process(request):
    """Endpoint to get information regarding processes running in the system
        Returns:
            json object of information containing pids and details of the processes runnung in the system
    """
    if not is_logged_in(request):
        raise Http404
    try:
        pids = psutil.pids()
        data = get_process_details(pids)
        if data:
            data_dict = {
                "status": 200,
                "data": data,
            }
            return Response(data)

    except Exception:
        raise Http404


def get_process_details(pids):
    """Get information regarding a process

    Parameters:
        pid (list) : list of pid of the process
    Returns:
        Dictionary containing pid, command, cpu, name, start time, status, user running it and memory consumed for each process
    """
    processes = []
    for pid in pids:
        pro = {}
        try:
            process = psutil.Process(pid=pid)
            pinfo = process.as_dict(attrs=['pid', 'name', 'username', 'cmdline',
                                           'cpu_percent', 'create_time', 'status', 'memory_percent'])
            pro = {
                "pid": pinfo['pid'],
                "cmd": pinfo['cmdline'],
                "cpu": float("{0: .2f}".format(float(pinfo['cpu_percent']))),
                "name": pinfo['name'],
                "createTime": datetime.fromtimestamp(pinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S"),
                "status": pinfo['status'],
                "username": pinfo['username'],
                "memory": float("{0: .2f}".format(pinfo['memory_percent']))
            }
            processes.append(pro)
        except psutil.NoSuchProcess as e:
            print(e)
        except Exception as e:
            print(e)
    processes = sorted(processes, key=lambda k: (k['cpu'], k['memory']), reverse=True)
    return processes


@api_view(["POST"])
def get_diskio(request):
    """Endpoint to get information regarding diskios
        Returns:
            json object of information containing reads and writes happening
    """
    if not is_logged_in(request):
        raise Http404
    try:
        diskiocounters = psutil.disk_io_counters()
        diskreadold = diskiocounters.read_bytes
        diskwriteold = diskiocounters.write_bytes
        time.sleep(1)
        diskiocounters = psutil.disk_io_counters()
        diskreadnew = diskiocounters.read_bytes
        diskwritenew = diskiocounters.write_bytes
        reads = diskreadnew - diskreadold
        writes = diskwritenew - diskwriteold
        data = {
            "status": 200,
            "read": reads / 1024,
            "write": writes / 1024
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def get_networks(request):
    """Endpoint to get information regarding netios
        Returns:
            json object of information containing packet transfers happening over the network
    """
    if not is_logged_in(request):
        raise Http404
    try:
        data = []
        oldnetio = psutil.net_io_counters(pernic=True)
        time.sleep(1)
        newnetio = psutil.net_io_counters(pernic=True)
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for key in oldnetio:
            ipv4 = '_'
            ipv6 = '_'
            try:
                for ad in addrs[key]:
                    if str(ad.family) == 'AddressFamily.AF_INET':
                        ipv4 = ad.address
                    if str(ad.family) == 'AddressFamily.AF_INET6':
                        ipv6 = ad.address
                isup = "yes" if stats[key].isup else "no"
                oldnetwork = oldnetio[key]
                newnetwork = newnetio[key]
                sent = (newnetwork.bytes_sent - oldnetwork.bytes_sent) / 1024
                receive = (newnetwork.bytes_recv - oldnetwork.bytes_recv) / 1024
                net = {
                    "name": key,
                    "sent": sent, 
                    "receive": receive,
                    "isup": isup, 
                    "ipv4": ipv4, 
                    "ipv6": ipv6
                }
                data.append(net)
            except Exception as e:
                print('key' + str(e))
        data_dict = {
            "status": 200,
            "data": data,
        }
        return Response(data)
    except Exception as e:
        print(e)
    raise Http404


@api_view(["POST"])
def check_status(request):
    """Endpoint to get information regarding securetea app running
        Returns:
            get status of securetea app running
    """
    if not is_logged_in(request):
        raise Http404
    global processid
    if processid:
        data = {
            "status": 200
        }
        return Response(data)
    return HttpResponse(status=204)

@api_view(["POST"])
def stop(request):
    """Endpoint to stop running securetea app"""
    if not is_logged_in(request):
        raise Http404
    
    runserver_kill = subprocess.run(["pkill", "-f", "runserver"])
    return Response(status=204)

def get_list(list_var):
    """Returns empty string if variable is None."""
    if list_var:
        return list_var
    else:
        return ""


def get_integer(bool_var):
    """Returns string value for the bool variable."""
    if bool_var:
        return "1"
    else:
        return "0"


@api_view(["GET", "POST"])
def sleep(request):
    """Endpoint to get start running securetea app with given configuration"""  
    if not is_logged_in(request):
        raise Http404
    
    global processid
    if request.method == 'GET':
        try:
            if not processid:
                processid = subprocess.Popen(
                    ['python3', '../SecureTea.py'], stdout=subprocess.PIPE,
                    preexec_fn=os.setsid)
                data = {
                    "status": 200
                }
                return Response(data)
            else:
                data = {
                    "status": 200
                }
                return Response(data)
        except Exception as e:
            print(e)
        raise Http404

    creds = request.data or {}
    args_list = ["--debug", "--skip_input", "--skip_config_file"]

    if creds.get("hist_logger"):
        args_list.append("--hist")

    # Telegram parsing
    if (creds.get("telegram_token") and
        creds.get("telegram_userId")):

        args_list.append("--telegram_bot_token=" + str(creds['telegram_token']))
        args_list.append("--telegram_user_id=" + str(creds['telegram_userId']))

    # Twilio SMS parsing
    if (creds.get("twilio_sid") and
        creds.get("twilio_token") and
        creds.get("twilio_from") and
        creds.get("twilio_to")):

        args_list.append("--twilio_sid=" + str(creds['twilio_sid']))
        args_list.append("--twilio_token=" + str(creds['twilio_token']))
        args_list.append("--twilio_from=" + str(creds['twilio_from']))
        args_list.append("--twilio_to=" + str(creds['twilio_to']))

    # Whatsapp parsing
    if (creds.get("whatsapp_sid") and
        creds.get("whatsapp_token") and
        creds.get("whatsapp_from") and
        creds.get("whatsapp_to")):

        args_list.append("--whatsapp_sid=" + str(creds['whatsapp_sid']))
        args_list.append("--whatsapp_token=" + str(creds['whatsapp_token']))
        args_list.append("--whatsapp_from=" + str(creds['whatsapp_from']))
        args_list.append("--whatsapp_to=" + str(creds['whatsapp_to']))

    # Slack parsing
    if (creds.get("slack_token") and
        creds.get("slack_userId")):

        args_list.append("--slack_token=" + str(creds['slack_token']))
        args_list.append("--slack_user_id=" + str(creds['slack_userId']))

    # AWS parsing
    if (creds.get("aws_secretKey") and
        creds.get("aws_accessKey") and
        creds.get("aws_email")):

        args_list.append("--aws_secret_key=" + str(creds['aws_secretKey']))
        args_list.append("--aws_access_key=" + str(creds['aws_accessKey']))
        args_list.append("--aws_email=" + str(creds['aws_email']))

    # Gmail parsing
    if (creds.get("sender_email") and
        creds.get("to_email") and
        creds.get("password")):

        args_list.append("--sender_email=" + str(creds['sender_email']))
        args_list.append("--to_email=" + str(creds['to_email']))
        args_list.append("--password=" + str(creds['password']))

    # AntiVirus parsing
    antivirus = creds.get('antivirus')
    custom_scan = creds.get('custom_scan')
    virustotal_api_key = creds.get('virustotal_api_key')
    update = creds.get('update')
    auto_delete = creds.get('auto_delete')
    monitor_usb = creds.get('monitor_usb')
    monitor_file_changes = creds.get('monitor_file_changes')

    if antivirus:
        if custom_scan:
            args_list.append("--custom-scan=" + str(custom_scan))
        if virustotal_api_key:
            args_list.append("--virustotal-api-key=" + str(virustotal_api_key))
        args_list.append("--update=" + get_integer(update))
        args_list.append("--auto-delete=" + get_integer(auto_delete))
        args_list.append("--monitor-usb=" + get_integer(monitor_usb))
        args_list.append("--monitor-file-changes=" + get_integer(monitor_file_changes))

    # Auto Server Patcher parsing
    asp = creds.get('asp')
    sslvuln = creds.get('sslvuln')
    apache = creds.get('apache')
    login = creds.get('login')
    ssh = creds.get('ssh')
    sysctl = creds.get('sysctl')
    asp_state = False

    if asp:
        if sslvuln:
            args_list.append("--ssl")
            args_list.append("--url=" + str(sslvuln))
            asp_state = True
        if apache:
            args_list.append("--apache")
            asp_state = True
        if login:
            args_list.append("--login")
            asp_state = True
        if ssh:
            args_list.append("--ssh")
            asp_state = True
        if sysctl:
            args_list.append("--sysctl")
            asp_state = True

    if asp_state:
        args_list.append("--auto-server-patcher")

    # System Log Parsing
    sys_log = creds.get('sys_log')
    if sys_log:
        args_list.append("--system_log")

    # Firewall parsing
    firewall = creds.get('firewall')
    if firewall:
        interface = creds.get('inter_face')
        ip_inbound = get_list(creds.get('ip_inbound'))
        inbound_action = get_integer(creds.get('inbound_action'))
        ip_outbound = get_list(creds.get('ip_outbound'))
        outbound_action = get_integer(creds.get('outbound_action'))
        protocols = get_list(creds.get('protocols'))
        protocol_action = get_integer(creds.get('protocol_action'))
        extensions = get_list(creds.get('extensions'))
        scan_load_action = get_integer(creds.get('scan_load_action'))
        sports = get_list(creds.get('sports'))
        sports_action = get_integer(creds.get('sports_action'))
        dest_ports = get_list(creds.get('dest_ports'))
        dest_ports_action = get_integer(creds.get('dest_ports_action'))
        dns = get_list(creds.get('dns'))
        dns_action = get_integer(creds.get('dns_action'))
        time_lb = creds.get('time_lb')
        time_ub = creds.get('time_ub')
        http_req = get_integer(creds.get('http_req'))
        http_resp = get_integer(creds.get('http_resp'))

        # Set default values for time
        if not time_lb:
            time_lb = "00:00"
        if not time_ub:
            time_ub = "23:59"

        if interface:
            args_list.append("--interface=" + str(interface))

        args_list += [
            "--inbound_IP_list=" + str(ip_inbound),
            "--inbound_IP_action=" + str(inbound_action),
            "--outbound_IP_list=" + str(ip_outbound),
            "--outbound_IP_action=" + str(outbound_action),
            "--protocol_list=" + str(protocols),
            "--protocol_action=" + str(protocol_action),
            "--scan_list=" + str(extensions),
            "--scan_action=" + str(scan_load_action),
            "--source_port_list=" + str(sports),
            "--source_port_action=" + str(sports_action),
            "--dest_port_list=" + str(dest_ports),
            "--dest_port_action=" + str(dest_ports_action),
            "--dns_list=" + str(dns),
            "--dns_action=" + str(dns_action),
            "--time_lb=" + str(time_lb),
            "--time_ub=" + str(time_ub),
            "--HTTP_request_action=" + str(http_req),
            "--HTTP_response_action=" + str(http_resp)
        ]

    # Server Log Parsing
    server_log = creds.get('server_log')
    if server_log:
        log_type = get_list(creds.get('log_type'))
        log_file = get_list(creds.get('log_file'))
        window = get_list(creds.get('window'))
        ip_list = get_list(creds.get('ip_list'))
        status_code = get_list(creds.get('status_code'))

        args_list += [
            "--log-type=" + str(log_type),
            "--log-file=" + str(log_file),
            "--window=" + str(window),
            "--ip-list=" + str(ip_list),
            "--status-code=" + str(status_code)
        ]

    # Intrusion Detection System
    ids = creds.get('ids')
    if ids:
        interface = get_list(creds.get('ids_inter_face'))
        threshold = get_list(creds.get('threshold'))
        ethreshold = get_list(creds.get('ethreshold'))
        sfactor = get_list(creds.get('sfactor'))

        args_list += [
            "--interface=" + str(interface),
            "--threshold=" + str(threshold),
            "--eligibility_threshold=" + str(ethreshold),
            "--severity_factor=" + str(sfactor)
        ]

    se_mail_id = get_list(creds.get("se_mail_id"))
    if se_mail_id:
        args_list.append("--social_eng_email=" + str(se_mail_id))

    # Local Web Deface Detection Parsing
    web_deface = creds.get('web_deface')
    if web_deface:
        server_name = get_list(creds.get("server_name"))
        path = get_list(creds.get("path"))

        args_list.append("--web-deface")
        args_list.append("--server-name=" + str(server_name))
        args_list.append("--path=" + str(path))

    # Web Application Firewall Parsing
    waf = creds.get('waf')
    if waf:
        listen_ip = get_list(creds.get("listen_ip"))
        listen_port = get_list(creds.get("listen_port"))
        mode = get_list(creds.get("mode"))
        backend_server_config = get_list(creds.get("backend_server_config"))

        args_list += [
            "--listenIp=" + str(listen_ip),
            "--listenPort=" + str(listen_port),
            "--mode=" + str(mode),
            "--hostMap=" + str(backend_server_config)
        ]

    # IoT Anonymity Checker Parsing
    iot_ano = creds.get('iot_ano')
    if iot_ano:
        shodan_api_key = get_list(creds.get("shodan_api"))
        ip_addr_iot = get_list(creds.get("ip_addr_iot"))

        args_list.append("--iot-checker")
        args_list.append("--shodan-api-key=" + str(shodan_api_key))
        args_list.append("--ip=" + str(ip_addr_iot))

    # Insecure Headers Parsing
    insecure_headers = creds.get('insecure_headers')
    if insecure_headers:
        url = get_list(creds.get("url_ih"))

        args_list.append("--insecure_headers")
        args_list.append("--url=" + str(url))

    try:
        if not processid:
            processid = subprocess.Popen(
                ['python3', '../SecureTea.py'] + args_list,
                stdout=subprocess.PIPE, preexec_fn=os.setsid)
            data = {
                "status": 201
            }
            return Response(data)
        else:
            data = {
                "status": 200
            }
            return Response(data)
    except Exception as e:
        print(e)
    raise Http404

def findpid():
    """Endpoint to find pid of securetea app
        Returns:
            pid of securetea app
    """
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            if any('SecureTea.py' in str(cmd) for cmd in cmdline):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

@api_view(["POST"])
def get_login(request):
    """Get last login details.

    Returns:
        login details of a user
    """
    if not is_logged_in(request):
        raise Http404
    try:
        data = []

        details_regex = r"([a-zA-Z]+\s[a-zA-Z]+\s+[0-9]+\s[0-9]+:[0-9]+)\s+(.*)"
        username_regex = r"^[a-zA-Z0-9]+\s"

        output = subprocess.check_output("last")
        output = output.decode("utf-8").split("\n")

        for line in output:
            username = re.findall(username_regex, line)
            if username != []:
                username = username[0].strip(" ")
                if username != "reboot":
                    details = re.findall(details_regex, line)
                    if details != []:
                        date = details[0][0]
                        status = details[0][1].strip("-")
                        status = status.strip(" ")
                        login_row = {
                            "status": 200,
                            "name": username, 
                            "date": date, 
                            "login_status": status
                        }
                        data.append(login_row)
        data_dict = {
            "status": 200,
            "data": data,
        }
        return Response(data_dict)
    except Exception as e:
        print(e)
    raise Http404
