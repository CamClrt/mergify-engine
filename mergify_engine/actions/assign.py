# -*- encoding: utf-8 -*-
#
#  Copyright © 2020 Mehdi Abaakouk <sileht@mergify.io>
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

import httpx
import voluptuous

from mergify_engine import actions


class AssignAction(actions.Action):
    validator = {voluptuous.Required("users", default=[]): [str]}

    silent_report = True

    def run(self, pull, sources, missing_conditions):
        wanted = set(self.config["users"])
        already = set((user["login"] for user in pull.data["assignees"]))
        assignees = list(wanted - already)
        try:
            pull.client.post(
                f"issues/{pull.data['number']}/assignees",
                json={"assignees": assignees},
            )
        except httpx.HTTPClientSideError as e:  # pragma: no cover
            return (
                None,
                "Unable to add assignees",
                f"GitHub error: [{e.status_code}] `{e.message}`",
            )

        return ("success", "Assignees added", ", ".join(self.config["users"]))