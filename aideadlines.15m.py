#!/usr/bin/env python3

# <xbar.title>AI deadlines counter</xbar.title>
# <xbar.version>v0.1</xbar.version>
# <xbar.author>Jiseob Kim</xbar.author>
# <xbar.author.github>nzer0</xbar.author.github>
# <xbar.desc>Count the days to the submission deadlines of AI conferences.</xbar.desc>
# <xbar.image>https://github.com/nzer0/bitbar-aideadlines/blob/master/aid-screenshot.png?raw=true</xbar.image>
# <xbar.dependencies>python3 (pyyaml, pytz, tzlocal, wget)</xbar.dependencies>
# <xbar.abouturl>https://github.com/nzer0/bitbar-aideadlines</xbar.abouturl>


import os
import re
import sys
import datetime as dt

ME_PATH = os.path.realpath(__file__)
ROOT = os.path.dirname(ME_PATH)
DL_FNAME = os.path.join(ROOT, ".aid.aideadlines.yaml")
DLG_FNAME = os.path.join(ROOT, ".aid.processed.yaml")
SEL_FNAME = os.path.join(ROOT, ".aid.seldl")
SHB_FNAME = os.path.join(ROOT, ".aid.ammend_shebang")
AID_URL = "https://raw.githubusercontent.com/abhshkdz/ai-deadlines/gh-pages/_data/conferences.yml"

"""Write bash script to ammend the shebang"""
if not os.path.exists(SHB_FNAME):
    with open(SHB_FNAME, "w") as sf:
        sf.write("#!/bin/bash\n")
        sf.write("SB=`which python3`\n")
        sf.write('sed -i "" -e "1s:#!/usr/bin/env python3:#!/usr/bin/env $SB:" "$1"\n')
        sf.write('echo ">>> Now refresh the Bitbar <<<"')
    os.chmod(SHB_FNAME, 0o755)

"""Display instructions if the dependencies are not installed"""
try:
    import yaml
    from pytz import timezone
    from tzlocal import get_localzone
    import wget
except:
    print("Install Dependencies")
    print("---")
    print("Please install the dependencies by clicking below | color=black")
    print(
        "$ pip3 install pyyaml pytz tzlocal wget | color=green bash='pip3 install pyyaml pytz tzlocal wget' refresh=true"
    )
    print("---")
    print("If it is still not working, click below | color=black")
    print(f"Ammend shebang | color=green bash='{SHB_FNAME}' param1={ME_PATH}")
    print("then refresh the BitBar | color=black")
    sys.exit(1)

"""Replace UTC with Etc/GMT to be handled by pytz"""


def normalize_tz(tz):
    mo = re.search(r"UTC([+-]\d+)", tz)
    if mo is None:
        return tz
    else:
        return f"Etc/GMT{-int(mo.group(1)):+d}"


"""Parse the string to make a datetime obj with an appropriate local"""


def make_datetime(c, abs=False):
    dl_key = "abstract_deadline" if abs else "deadline"
    # print()
    timezone_ = c["timezone"].replace("GMT", "Etc/GMT")
    timezone_ = normalize_tz(timezone_)
    # print(timezone_)
    try:
        return timezone(timezone_).localize(
            dt.datetime.strptime(c[dl_key], "%Y-%m-%d %H:%M:%S")
        )
    except:
        return timezone(timezone_).localize(
            dt.datetime.strptime(c[dl_key], "%Y-%m-%d %H:%M")
        )


"""Compute the datetime diff with now"""


def get_diff(due):
    return due - get_localzone().localize(dt.datetime.now())


"""main Bitbar display"""


def main():
    if not os.path.exists(DL_FNAME):
        getdl()
    with open(DLG_FNAME, "r") as yf:
        dlg = yaml.safe_load(yf)
    # print("Open www.okex.com | href=https://www.okex.com/")
    # print(
    #     "¥0.00 | image=iVBORw0KGgoAAAANSUhEUgAAABoAAAAeCAYAAAAy2w7YAAAACXBIWXMAABYlAAAWJQFJUiTwAAAAE3RFWHRTb2Z0d2FyZQBtb25lcm8uaG9398/iYQAAAyxJREFUeNrclstrE1EUxu9MJkWrtvWxKmgXRrG4KBRELFUqVtFKqnUnLkRF1L9AwYXBpeBCEVcuXIgbQRG0rYraGokP4iok5KHZqJi0TUwnD9I8/U48I9Mwk7FNcOGBX7i599zz3ee5I7lcLmFh/eAgGAAOsA5IIAm+AA+YBN5GQZQGbXvBJTAMZIP2DWArOASuglfgGnhuFMwowApwG7wEB0x86o1muA88A3fAKiuhTvAYXODOy7Ez4AlYbya0EjzgWTRrQ+AhWG0kdB3sF62zPeBWvdBucJ7L0+BrEwI/wGsun9QGrwld0e2JGxwGsWWIJIATvNDV0f2RSaiPj7Jma4CPO8wtQSQFRsEn0KGrp/u3Q+bRGx1hryRJR3iUVjYP3zG+vEbmJIFBs96VSsWDACMWy5iAjxO+U9Vq1cxnQOa0sshsNptIJpPC7/eLQqHwUZZls2VMoW20VCq5A4GASCQStb4G1kNCaxddcUkS5XJZxONxoaqqCIfDYmFhwYuA9cs4j7oxDMRDPuQ7MzMjIFqLUWcdslEGIOd8Pi/sdvvFTCbTFwqFSMyDwCOcTFWaJUSmWKRXUZTL6CMVi0Vhlut+Giav36Pqx1KMZ7NZBwVEkNoy0nKh7I5EIiKdTvfAZwK+O9HHbJNUEoo2yH8q6CYxzMwRDAZJzAOmaZaYySa0PaU9YF+zHPqNnokpzk2aFXVrrBW2sNgIBD5TO8+ERLbrfbkvrV9BF3NaQcNNLMUj/KFpSygnaWMNNpXEJiFGl7vIy9WrX2rqk8vlRHt7+w0c93taTJS/K2jMplKpIDloJ46ONt0J/C/VLcFmDIQetpJeRDtD9BONRgXizWIgsxQDoqKrq0soPp+P7oodlYM8AiQmWZvNRoON3Way4d3oM0SzisX+3G8ZdW/b2toKCh1HBK6g8iw43kTWpid/mAaou7S0Je6aBo+8DM5x5m6VfQCntcOlP4ZpcAy8aYHIe3CUM7rheZ/jbH63CZH7/GUUs/oKyoBTLLiU2dETQfnwhH4mf/NdN87Qw0U5bhdngE4tqfKT/w5MWO2v1OANaanJ4h/Z/yf0S4ABAI1oQOxFaPzhAAAAAElFTkSuQmCC\n---\nLive chart | href='https://www.monero.how/monero-chart'\nMonero.how homepage | href='https://www.monero.how'"
    # )

    try:
        """If there is a selected deadline"""
        with open(SEL_FNAME, "r") as sf:
            sell = sf.readline().rstrip("\n").split(" ")
        cells = []
        # print(sell)
        for sel in sell:
            # print(sel)
            if sel not in dlg["full"].keys():
                continue
            conf = dlg["full"][sel]
            name = conf["title"]
            dl = make_datetime(conf)
            diff = get_diff(dl)
            days = f"+{-diff.days}" if diff.days < 0 else f"-{diff.days}"
            hours = f"{diff.seconds//3600}"
            cells.append({"name": name, "conf": conf, "days": days, "hours": hours})
            # print("--------------")
        sorted_cells = sorted(cells, key=lambda k: -1*int(k["days"]))
        # print([cell["days"] for cell in sorted_cells])
        for cell in sorted_cells:
            name, conf, days, hours = cell["name"], cell["conf"], cell["days"], cell["hours"]
            # print(f"{name} D{days} {hours}h+")
            print(f"{name} D{days}")# {hours}h+")
            print("---")
            # print(f"About {name} {conf['year']}")
            # print(f"--:date: {conf['date']}")
            # print(f"--:round_pushpin: {conf['place']}")
            # print(f"--:house: Go to Website | href={conf['link']}")
            # print("-----")
            
            if "abstract_deadline" in conf.keys():
                abs_dl = make_datetime(conf, abs=True)
                print(
                    f"--Abs: {abs_dl.strftime('%Y-%m-%d %H:%M')} ({conf['timezone']})"
                )
            print(f"--Due: {dl.strftime('%Y-%m-%d %H:%M')} ({conf['timezone']})")
    except Exception as e:
        print(e)
        name = "N/A"
        print("Select the conference")

    print("---")
    for urg in dlg["urgent"][:10]:
        conf = dlg["full"][urg]
        outstr = f"{conf['title']} | bash='{ME_PATH}' param1='seldl' param2='{conf['title']}' terminal=false refresh=true"
        if conf["title"] == name:
            outstr += " checked=true"
        print(outstr)
    print("More...")
    for sub_name, sub in dlg["subs"].items():
        print(f"--{sub_name}")
        for t in sub:
            conf = dlg["full"][t]
            outstr = f"----{conf['title']} | bash='{ME_PATH}' param1='seldl' param2='{conf['title']}' terminal=false refresh=true"
            if get_diff(make_datetime(conf)).days < 0:
                outstr += " color=red"
            print(outstr)
    print("---")
    print(
        f"Update Conferences Info | bash='{ME_PATH}' param1='getdl' terminal=false refresh=true"
    )
    print("Go to aideadlin.es | href='https://aideadlin.es'")
    print("About this plugin | href='https://github.com/hany606/xbar-aideadlines")


"""Select a particular deadline"""


def seldl(conf_title):
    with open(SEL_FNAME, "w") as sf:
        sf.write(conf_title)


"""Get the deadlines list from aideadlin.es and process it"""


def getdl():
    if os.path.exists(DL_FNAME):
        os.remove(DL_FNAME)
    print("Updating...")
    wget.download(AID_URL, DL_FNAME, False)
    print("Done")
    with open(DL_FNAME, "r") as yf:
        dl = yaml.safe_load(yf)
    # print(dl)
    full = {}
    subs = {}
    for conf in dl:
        # print(type(conf["start"]))
        # print(conf.keys())
        now = dt.datetime.now()
        # if "deadline" not in conf.keys():
        #     conf["deadline"] = dt.date(conf["year"], now.month, now.day).strftime('%m/%d/%y %H:%M:%S')
        
        deadline = conf["deadline"]
        # print(deadline)
        # print(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            deadline_datetime_object = dt.datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
        except:
            deadline_datetime_object = dt.datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        if deadline_datetime_object < now:#dt.date(now.year, now.month, now.day):
            # print(conf["start"], conf["year"], conf["title"])
            continue
        full[conf["title"]] = conf
        sub = conf["sub"]
        # if conf["title"] == "ICLR":
            # print(sub)
            # print(full["ICLR"])
        if sub in subs.keys():
            subs[sub].append(conf["title"])
        else:
            subs[sub] = [conf["title"]]
    # print(full["ICLR"])
    # print(sub)
    urgent = sorted(list(full.keys()), key=lambda t: make_datetime(full[t]))
    urgent = [t for t in urgent if get_diff(make_datetime(full[t])).days > -7]

    for sub in subs.values():
        sub.sort(key=lambda t: make_datetime(full[t]))

    print("Write.....")
    # print(full.keys())
    # print(dict(full=full, subs=subs, urgent=urgent))
    with open(DLG_FNAME, "w") as yf:
        yaml.safe_dump(dict(full=full, subs=subs, urgent=urgent), yf)
    print("Done")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()

    elif sys.argv[1] == "seldl":
        seldl(sys.argv[2])

    elif sys.argv[1] == "getdl":
        getdl()
