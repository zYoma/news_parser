import subprocess


def df_h():
    result = subprocess.run('df -h|grep /dev/vda1', stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    out = result.stdout
    return out
def top():
    result = subprocess.run('free -m', stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    out = result.stdout
    return out
def ban():
    result = subprocess.run('cat /var/log/fail2ban.log', stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    out = result.stdout
    return out
