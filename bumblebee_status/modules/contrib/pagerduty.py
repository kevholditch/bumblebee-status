

"""

"""

import shutil
import requests

import core.module
import core.widget
import core.decorators
import core.input

import util.format
import re
from datetime import datetime, timedelta


class Module(core.module.Module):
    @core.decorators.every(minutes=5)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.pagerduty))

        self.__label = ""
        self.background = True
        self.__requests = requests.Session()
        self.__requests.headers.update(
        {
            "authorization": "Token token=" + self.parameter("token", ""),
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json"
        })

        self.__workspace = self.parameter("workspace", "")
        self.__scheduleId = self.parameter("scheduleId", "")
        if self.parameter("format", "fullname").lower() == "initials":
            self.__format_func = lambda name: "".join(list(map(lambda x: x[0], re.findall(r"[\w']+", name))))
        else:
            self.__format_func = lambda x: x


        cmd = "xdg-open"
        if not shutil.which(cmd):
            cmd = "x-www-browser"

        core.input.register(
            self,
            button=core.input.LEFT_MOUSE,
            cmd="{} https://{}.pagerduty.com/schedules#{}".format(cmd, self.__workspace, self.__scheduleId),
        )

    def pagerduty(self, _):
        return self.__label

    def update(self):
        try:
            url = "https://api.pagerduty.com/schedules/{}/users?since={}&until={}"
            since = datetime.now()
            until = since + timedelta(seconds=1)
            date_fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
            r = self.__requests.get(url.format(self.__scheduleId, since.strftime(date_fmt), until.strftime(date_fmt)))
            if r.status_code != 200:
                self.__label = "error"
                return

            self.__label = " " + self.__format_func(r.json()["users"][0]["name"])


        except Exception as err:
            self.__label = "error"



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
