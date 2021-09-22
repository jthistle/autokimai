#!/usr/bin/env python3

import requests
import datetime
import yaml

class AutoKimai:
    def __init__(self, config):
        self.config = config
        
        self.HEADERS = {
            "X-AUTH-USER": config["auth"]["user"],
            "X-AUTH-TOKEN": config["auth"]["api-key"],
        }

        action = self.config["action"]

        self.project_id = action["project-id"]
        self.activity_id = action["activity-id"]
        self.date_range = (action["start-date"], action["end-date"])
        self.hours = action["daily-hours"]
        self.desc = action["description"]

    def api(self, route):
        return f"https://kimai.neontribe.net/api/{route}"

    def get(self, route):
        res = requests.get(self.api(route), headers=self.HEADERS)

        if res.status_code != 200:
            print(f"Request for {self.api(route)} did not succeed")
            print(f"Status code {res.status_code}")
            print("Response body:", res.json())
            raise Exception()

        return res

    def post(self, route, body):
        res = requests.post(self.api(route), json=body, headers=self.HEADERS)

        if res.status_code != 200:
            print(f"Request for {self.api(route)} did not succeed")
            print(f"Status code {res.status_code}")
            print("Request body:", res.json())
            print("Response body:", res.json())
            raise Exception()
        
        return res

    def run(self):
        if self.project_id is None:
            self.get_project()

        if self.activity_id is None:
            self.get_activity()

        
        print(f"About to add timesheets between {self.date_range[0].isoformat()} and {self.date_range[1].isoformat()}")
        input("Press ENTER to continue, CTRL+C to cancel")

        # Add timesheets
        print("Adding timesheets, please wait...")
        self.add_multiple()
        print("Done.")

    def get_project(self):
        res = self.get("projects")
        content = sorted(res.json(), key=lambda x: int(x["id"]))

        projects_list = ""
        for project in content:
            projects_list += f"{project['id']}: {project['parentTitle']} - {project['name']}\n"
        print(projects_list)

        self.project_id = int(input("Select project id: "))

    def get_activity(self):
        res = self.get(f"activities?project={self.project_id}")
        content = sorted(res.json(), key=lambda x: int(x["id"]))

        activities_list = ""
        for activity in content:
            activities_list += f"{activity['id']}: {activity['parentTitle'] or 'Global'} - {activity['name']}\n"
        print(activities_list)

        self.activity_id = int(input("Select activity id: "))

    def add_timesheet(self, day: datetime.date):
        end_time = f"{9 + self.hours:02}:00:00"
        self.post("timesheets", {
            "begin": f"{day.isoformat()}T09:00:00",
            "end": f"{day.isoformat()}T{end_time}",
            "project": self.project_id,
            "activity": self.activity_id,
            "description": self.desc,
        })

    def add_multiple(self):
        date = self.date_range[0]
        while date <= self.date_range[1]:
            day = date.weekday()
            if day % 7 < 5:
                self.add_timesheet(date)
            date += datetime.timedelta(days=1)


def main():
    print("Welcome to AutoKimai. Input is not validated, type carefully.\n")

    with open("config.yaml", "r") as fd:
        config = yaml.safe_load(fd.read())

    auto_kimai = AutoKimai(config)
    auto_kimai.run()

    print("Thanks for using AutoKimai ^_^")

main()
