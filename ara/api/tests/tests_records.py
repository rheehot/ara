#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class RecordTestCase(APITestCase):
    def test_record_factory(self):
        record = factories.RecordFactory(key="test")
        self.assertEqual(record.key, "test")

    def test_record_serializer(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.RecordSerializer(
            data={"key": "test", "value": "value", "type": "text", "playbook": playbook.id}
        )
        serializer.is_valid()
        record = serializer.save()
        record.refresh_from_db()
        self.assertEqual(record.key, "test")
        self.assertEqual(record.value, "value")
        self.assertEqual(record.type, "text")

    def test_get_no_records(self):
        request = self.client.get("/api/v1/records")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_record(self):
        record = factories.RecordFactory()
        request = self.client.get("/api/v1/records")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(record.key, request.data["results"][0]["key"])

    def test_delete_record(self):
        record = factories.RecordFactory()
        self.assertEqual(1, models.Record.objects.all().count())
        request = self.client.delete("/api/v1/records/%s" % record.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Record.objects.all().count())

    def test_create_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        request = self.client.post(
            "/api/v1/records", {"key": "test", "value": "value", "type": "text", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())

    def test_partial_update_record(self):
        record = factories.RecordFactory()
        self.assertNotEqual("update", record.key)
        request = self.client.patch("/api/v1/records/%s" % record.id, {"key": "update"})
        self.assertEqual(200, request.status_code)
        record_updated = models.Record.objects.get(id=record.id)
        self.assertEqual("update", record_updated.key)