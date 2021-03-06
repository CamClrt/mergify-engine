# -*- encoding: utf-8 -*-
#
#  Copyright © 2018 Mehdi Abaakouk <sileht@sileht.net>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random
from urllib import parse

import voluptuous

from mergify_engine import actions
from mergify_engine import check_api
from mergify_engine import context
from mergify_engine import rules
from mergify_engine import signals
from mergify_engine.clients import http


class LabelAction(actions.Action):
    validator = {
        voluptuous.Required("add", default=[]): [str],
        voluptuous.Required("remove", default=[]): [str],
        voluptuous.Required("remove_all", default=False): bool,
    }

    silent_report = True

    async def run(
        self, ctxt: context.Context, rule: rules.EvaluatedRule
    ) -> check_api.Result:
        labels_changed = False

        pull_labels = {label["name"] for label in ctxt.pull["labels"]}

        if self.config["add"]:
            all_label = [
                label["name"]
                async for label in ctxt.client.items(f"{ctxt.base_url}/labels")
            ]
            for label in self.config["add"]:
                if label not in all_label:
                    color = f"{random.randrange(16 ** 6):06x}"  # nosec
                    try:
                        await ctxt.client.post(
                            f"{ctxt.base_url}/labels",
                            json={"name": label, "color": color},
                        )
                    except http.HTTPClientSideError:
                        continue

            missing_labels = set(self.config["add"]) - pull_labels
            if missing_labels:
                await ctxt.client.post(
                    f"{ctxt.base_url}/issues/{ctxt.pull['number']}/labels",
                    json={"labels": list(missing_labels)},
                )
                labels_changed = True

        if self.config["remove_all"]:
            if ctxt.pull["labels"]:
                await ctxt.client.delete(
                    f"{ctxt.base_url}/issues/{ctxt.pull['number']}/labels"
                )
                labels_changed = True

        elif self.config["remove"]:
            for label in self.config["remove"]:
                if label in pull_labels:
                    label_escaped = parse.quote(label, safe="")
                    try:
                        await ctxt.client.delete(
                            f"{ctxt.base_url}/issues/{ctxt.pull['number']}/labels/{label_escaped}"
                        )
                    except http.HTTPClientSideError:
                        continue
                    labels_changed = True

        if labels_changed:
            await signals.send(ctxt, "action.label")
            return check_api.Result(
                check_api.Conclusion.SUCCESS, "Labels added/removed", ""
            )
        else:
            return check_api.Result(
                check_api.Conclusion.SUCCESS, "No label to add or remove", ""
            )
