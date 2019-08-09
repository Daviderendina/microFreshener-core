from unittest import TestCase

from microfreshener.core.model.type import MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY, MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVEY_PROPERTY, MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY
from microfreshener.core.model.microtosca import MicroToscaModel
from microfreshener.core.model.nodes import Service, Database, MessageBroker, MessageRouter
from microfreshener.core.errors import MicroToscaModelError, SelfLoopMicroToscaModelError
from microfreshener.core.model.relationships import InteractsWith


class TestModelRelationships(TestCase):

    @classmethod
    def setUpClass(self):
        self.name = "prova-model"
        self.microtosca = MicroToscaModel(self.name)
        self.service_name = "s1"
        self.database_name = "db1"
        self.messagerouter_name = "mr1"
        self.messagebroker_name = "mb1"

        self.microtosca.add_node(Service(self.service_name))
        self.microtosca.add_node(Database(self.database_name))
        self.microtosca.add_node(MessageBroker(self.messagebroker_name))
        self.microtosca.add_node(MessageRouter(self.messagerouter_name))

    def test_create_interactWith(self):
        source_node = self.microtosca[self.service_name]
        rel = InteractsWith(source_node, self.microtosca[self.database_name])
        self.assertEqual(rel.source, source_node)
        self.assertIsInstance(rel.source, Service)
        self.assertEqual(rel.target, self.microtosca[self.database_name])
        self.assertIsInstance(rel.target, Database)

    def test_add_interaction_from_service(self):
        source = self.microtosca[self.service_name]
        target = self.microtosca[self.database_name]
        rel = source.add_interaction(target)
        self.assertEqual(len(source.interactions), 1)
        self.assertIn(rel, source.interactions)
        self.assertIn(rel, target.incoming_interactions)

    def test_add_interaction_from_messagerouter(self):
        source = self.microtosca[self.messagerouter_name]
        target = self.microtosca[self.service_name]
        rel = source.add_interaction(target)
        self.assertEqual(len(source.interactions), 1)
        self.assertIn(rel, source.interactions)
        self.assertIn(rel, target.incoming_interactions)

    def test_add_interaction_database_error(self):
        # test that database cannot be a source of the interactiwth interaction
        source = self.microtosca[self.database_name]
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.service_name]
            source.add_interaction(target)
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.messagebroker_name]
            source.add_interaction(target)
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.messagerouter_name]
            source.add_interaction(target)
           
    def test_add_interaction_messagebroker_error(self):
        source = self.microtosca[self.messagebroker_name]
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.service_name]
            source.add_interaction(target)
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.messagerouter_name]
            source.add_interaction(target)
        with self.assertRaises(MicroToscaModelError):
            target = self.microtosca[self.database_name]
            source.add_interaction(target)

    def test_add_interaction_selfloop_error(self):
        with self.assertRaises(SelfLoopMicroToscaModelError):
            source = self.microtosca[self.service_name]
            target = self.microtosca[self.service_name]
            source.add_interaction(target)
