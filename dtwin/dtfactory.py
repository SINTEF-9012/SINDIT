"""
Factory graph class 

"""
import jsonpickle
import json
import networkx as nx
import matplotlib.pyplot as plt
import py2neo
import random
import dtwin.dtmachine as dtMachine
import dtwin.dtqueue as dtQueue
import dtwin.dtsensor as dtSensor
import dtwin.dtpart as dtPart
import dtwin.dttypes as dtTypes
import matplotlib.artist as ma
import itertools
import pandas as pd
import datetime
import numpy as np
import dtwin.flux as f
import math
from aas import model
import uuid as id
from aas.adapter.xml import write_aas_xml_file
from aas.adapter import aasx
from config import global_config as cfg
import simpy
import matplotlib.animation as animation

PRINT_DEBUG_INFO = False
#Graph stuff
import saas.ass_factory
from saas.ass_factory import AASFactory
from saas.semantic_factory import SemanticFactory


class dtFactory(object):
    """
    Base class for digital  twin factories.
    
    """
    def __init__(self,
                 flushAAS:bool=False,
                 name=None,
                 description=None,
                 graph=nx.DiGraph(),
                 file_path="",
                 env = simpy.Environment()):

        self.graph = graph

        #@todo: graph and machines, sensors, and queues have redundant information 
        # need to be kept in sync at all times. This needs to be properly addressed

        self.machines = []
        self.queues = []
        self.sensors = []
        self.parts = []
        self.groups = []
        self.name = name
        self.description = description

        #ass
        if self.name is None or self.name.isspace():
            self.name = "SINDIT_Default_Factory_Name"
        if self.description is None or self.description.isspace():
            self.description = "SINDIT factory"

        # if flushAAS:
        #     AASFactory.instance().flush()
        #
        # nameplate = AASFactory.instance().create_Nameplate(name=self.name+"_Nameplate",
        #                                                    manufacturerName="SINDIT_Default_Manufacturer_Name",
        #                                                    manufacturerProductDesignation=self.description)
        # dictionary = AASFactory.instance().create_ConceptDictionary(name=self.name+"_ConceptDictionary",
        #                                                             concepts={SemanticFactory.instance().getNameplate(),
        #                                                                       SemanticFactory.instance().getManufacturerName(),
        #                                                                       SemanticFactory.instance().getManufacturerProductDesignation()})
        # self.aas = AASFactory.instance().create_aas(name=self.name,
        #                                             description=self.description,
        #                                             submodels={nameplate},
        #                                             concept_dictionary={dictionary})

        #plotting 
        self.picked = False
        self.visiblesensors = []
        self.visiblesensortext = []
        self.fig = None
        self.ax = None
        self.time_text = None
        self.goods_text = None
        self.txt = ''
        self.expl = ''
        self.explarr = ''


        # serializing 
        if file_path != "":
            self.deserialize(serial_type="json", file_path_or_uri=file_path)

        # discrete event simulation
        self.env = env
        self.sim_hours = 10

    def _print_debug(self, print_str=''):
        if PRINT_DEBUG_INFO:
            print(print_str)

    def set_simulation_environment(self):
        for m in self.machines:
            m.env=self.env

        for q in self.queues:
            q.env = self.env
            q.create_store()

        self.populate_networkx_graph()
        print('Simulation environment is set')

    def set_parts_uri(self, uri):
        part_g = py2neo.Graph(uri)
        for part in self.parts:
            part.py2neo_graph = part_g
        return True

    def get_source_queues(self):
        source_buffers = []
        for node in self.graph.nodes():
            machine=self.get_machine_by_name(node.name)
            if machine.type == dtTypes.dtTypes.SOURCE:
                for edge in self.graph.out_edges(node, data=True):
                    source_buffers.append(self.get_queue_by_name(edge[2]['name']))

        return source_buffers

    def run(self, use_kafka_and_neo4j = True, is_real_time = True):

        #total working time (hours)
        total_time = self.sim_hours

        #new environment
        if is_real_time:
            self.env = simpy.RealtimeEnvironment(initial_time=0, factor=5, strict=False)
        else:
            self.env = simpy.Environment()

        self.set_simulation_environment()

        print('----------------------------------')
        print('SIMULATION OF {0} HOURS INITIALIZING'.format(total_time))
        print('----------------------------------')
        processes = []
        for machine in self.machines:
            # set the processes
            in_queues = []
            out_queues = []
            for edge_in in self.graph.in_edges(machine, data=True):
                in_queues.append(self.get_queue_by_name(edge_in[2]['name']))

            for edge_out in self.graph.out_edges(machine, data=True):
                out_queues.append(self.get_queue_by_name(edge_out[2]['name']))

            self._print_debug('{0} {1} has {2} in queues and {3} out queues'.format(
                machine.type.name, machine.name, len(in_queues), len(out_queues)))

            if machine.type == dtTypes.dtTypes.PROCESS or machine.type == dtTypes.dtTypes.MACHINE:
                processes.append(self.env.process(machine.run(in_queues,out_queues,use_kafka_and_neo4j)))

        print('----------------------------------')
        print('SIMULATION OF {0} TIME STARTED'.format(total_time))
        print('----------------------------------')

        if total_time>0:
            self.env.run(until = total_time)

        print('----------------------------------')
        sim_results = []
        for node in self.graph.nodes():
            machine=self.get_machine_by_name(node.name)
            if machine.type == dtTypes.dtTypes.EXIT:
                for edge in self.graph.in_edges(node, data=True):
                    amount_produced = self.get_queue_by_name(edge[2]['name']).amount
                    print('There is {0} amount on EXIT {1} after {2} hours'.format(
                        amount_produced,edge[2]['name'],self.env.now))
                    sim_results.append({'name': edge[2]['name'], 'amount': amount_produced})

            if machine.type == dtTypes.dtTypes.SOURCE:
                for edge in self.graph.out_edges(node, data=True):
                    amount_left = self.get_queue_by_name(edge[2]['name']).amount
                    print('There is {0} amount on SOURCE {1} after {2} hours'.format(
                        amount_left,edge[2]['name'],self.env.now))

        print('----------------------------------')
        print('SIMULATION COMPLETED')
        print('----------------------------------')

        # write back the parts
        self.parts = []
        for q in self.queues:
            if q.type == dtTypes.dtTypes.BUFFER:
                for p in q.store.items:
                    self.parts.append(p)

        return sim_results

    #Interactive stuff:
    def on_pick(self, event):
        art = event.artist
        art.stale=False

        if self.picked:
            ma.setp(self.picked, facecolor = 'grey', edgecolor = 'grey')
        self.picked = art
        ma.setp(art,facecolor ='blue', edgecolor='blue')

        art.figure.canvas.draw_idle()

        l = ma.getp(art, 'label')

        for m in self.machines:
            if l == m.name:
                self.visiblesensors, self.visiblesensortext = \
                    m.draw_expl(self.expl, \
                                self.explarr, \
                                self.txt, \
                                self.ax, \
                                self.visiblesensors,
                                self.visiblesensortext)
                break

        for q in self.queues:
            if l == q.name:
                self.visiblesensors, self.visiblesensortext = \
                    q.draw_explarr(self.expl,
                                   self.explarr,
                                   self.txt,
                                   self.visiblesensors,
                                   self.visiblesensortext)
                break

        for s in self.sensors:
            if l == s.name:
                ma.setp(art,facecolor ='black', edgecolor='black')
                s.plot_timeseries()
                break


    def create_node_pos(self):
        top = list(nx.algorithms.dag.topological_sort(self.graph))
        xpos = 0
        ypos = 10
        pos = {}
        #print('Pos: ', pos)
        for i in range(len(top)-1):
            pos[top[i]] = tuple((xpos, ypos))
            if (top[i], top[i+1]) in self.graph.edges():
                xpos += 2
            else:
                ypos -= 2
            pos[top[i+1]] = tuple((xpos, ypos))

        return pos

    def get_machine_by_name(self, name=''):
        for m in self.machines:
            if m.name == name:
                return m

        # if no machine found return empty dtMachine
        return dtMachine.dtMachine()

    def get_queue_by_name(self, name=''):
        for q in self.queues:
            if q.name == name:
                return q

    def get_out_queue_by_machine_name(self, name=''):
        for q in self.queues:
            if q.frm.name == name:
                return q

    def get_sensor_by_name(self, name=''):
        for s in self.sensors:
            if s.name == name:
                return s

        # if no sensor found return empty dtSensor
        return dtSensor.dtSensor(name=name)

    def get_part_by_name(self, name=''):
        for p in self.parts:
            if p.name == name:
                return p

        # if no part found return None
        return None

    def get_part_by_uuid(self, uuid=''):
        for p in self.parts:
            if p.uuid == uuid:
                return p
        # if no part found return None
        return None

    def animate(self,i):
        """perform animation step"""
        num_goods = 0
        exit_edge_names = []

        for node in self.graph.nodes():
            machine=self.get_machine_by_name(node.name)
            if machine.type == dtTypes.dtTypes.EXIT:
                for edge in self.graph.in_edges(node, data=True):
                    exit_edge_names.append(edge[2]['name'])

        for e in exit_edge_names:
            for entry in self.get_queue_by_name(e).monitor:
                if entry[0]>=i:
                    num_goods=entry[1]
                    break

        self.time_text.set_text('time = %i h' % i)
        self.goods_text.set_text('goods = %i' % num_goods)

        return self.time_text, self.goods_text

    def init(self):
        """initialize animation"""
        self.time_text.set_text('')
        self.goods_text.set_text('')
        return self.time_text, self.goods_text

    def draw_graph(self, fig_id = 1):
        self.fig = plt.figure(fig_id, figsize=(15, 10))
        self.fig.clf()
        self.ax  = self.fig.add_subplot()
        pos = self.create_node_pos()


        for node in self.graph.nodes():
            rec = plt.Rectangle(pos[node], 1,1, color='grey',
                                picker=5, label=node.name)
            self.ax.add_patch(rec)
            self.txt = plt.text(pos[node][0],pos[node][1], node)

        for edge in self.graph.edges(data=True):
            x1 = pos[edge[0]][0]+.5
            x2 = pos[edge[1]][0]+.5
            y1 = pos[edge[0]][1]+.5
            y2 = pos[edge[1]][1]+.5

            if x1 < x2:
                x1 += .6
                x2 -= .7
            elif x2 < x1:
                x1 -= .6
                x2 += .7
            if y1 < y2:
                y1 += .6
                y2 -= .7
            elif y2 < y1:
                y1 -= .6
                y2 += .7
            arr = plt.arrow(x1,y1, x2-x1, y2-y1, color='grey',
                            picker=15, width=.04, label=edge[2]['name'])

            self.ax.add_patch(arr)
            self.txt = plt.text(x1,y1+.2, edge[2]['name'])

        self.expl = plt.Rectangle((10,-2),2,2, color='blue', visible=False)
        self.ax.add_patch(self.expl)
        self.explarr = plt.arrow(10, 0, 2, 0, color='blue', width=.05, visible=False)
        self.ax.add_patch(self.explarr)

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

        self.ax.set_title(self.name)

        self.time_text = self.ax.text(0.90, 0.03, '', transform=self.ax.transAxes)
        self.goods_text = self.ax.text(0.90, 0.01, '', transform=self.ax.transAxes)

        ani = animation.FuncAnimation(self.fig, self.animate,
                                      init_func=self.init,
                                      frames=self.sim_hours, blit=True,interval=1000)

        plt.show()

        return True

        # writes graph to JSON file
    def serialize(self, serial_type="networkx-json", file_path_or_uri="factory_graph.json", plot = False, **kwargs):
        ret_val=False
        if serial_type == "networkx-json":
            '''Function to serialize a NetworkX DiGraph to a JSON file.'''
            if not isinstance(self.graph, nx.DiGraph):
                raise Exception('the graph has be an instance of networkx.DiGraph')

            with open(file_path_or_uri, 'w+') as _file:
                _file.write(jsonpickle.encode(nx.readwrite.json_graph.adjacency_data(self.graph)))
            ret_val=True
        elif serial_type == "json":
            jsondata = {}
            # factory spec
            jsondata["factory"] = {}
            jsondata["factory"]["name"] = self.name
            jsondata["factory"]["sim_hours"] = self.sim_hours
            group_list = []
            for group in self.groups:
                group_list.append(group)

            jsondata["factory"]["groups"] = group_list

            # machines  
            jsondata["machines"] = []
            for m in self.machines:
                jsondata["machines"].append(m.serialize())

                # queues
            jsondata["queues"] = []
            for q in self.queues:
                jsondata["queues"].append(q.serialize())

                #sensors
            jsondata["sensors"] = []
            for s in self.sensors:
                jsondata["sensors"].append(s.serialize())

            # parts
            jsondata["parts"] = []
            for p in self.parts:
                jsondata["parts"].append(p.serialize())

            with open(file_path_or_uri, 'w+') as _file:
                json.dump(jsondata, _file, indent=4)
            ret_val=True
        elif serial_type == "aasx":
            # see https://git.rwth-aachen.de/acplt/pyi40aas/-/blob/master/aas/examples/tutorial_aasx.py
            #object_store = model.DictObjectStore([self.aas, self.asset])
            file_store = aasx.DictSupplementaryFileContainer()
            with aasx.AASXWriter(file_path_or_uri) as writer:
                writer.write_aas(aas_id=self.aas.identification,
                                 object_store= AASFactory.instance().assetStore,
                                 file_store=file_store,
                                 submodel_split_parts=False)  # for compatibility with AASX Package Explorer



        elif serial_type == "aas":
            #data: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
            #data.add(self.aas)
            #data.add(self.asset)
            with open(file_path_or_uri, 'wb') as f:
                write_aas_xml_file(file=f, data=AASFactory.instance().assetStore)

        elif serial_type == "neo4j":
            if 'need_auth' in kwargs:
                if kwargs.get("need_auth").lower() == 'false':
                    g = py2neo.Graph(file_path_or_uri)
                else:
                    g = py2neo.Graph(file_path_or_uri, **kwargs)
            else:
                g = py2neo.Graph(file_path_or_uri, **kwargs)
            #first we delete everything
            g.delete_all()
            tx = g.begin()
            # just a dummy to collect graph properties it is not connected to the factory graph
            # but maybe it makes sense to connect if we would like to keep more than a single
            # factory in the database
            graph_property_node = py2neo.Node('GRAPH_PROP_NODE',
                                              name=self.name,
                                              sim_hours=self.sim_hours,
                                              groups=self.groups)
            tx.create(graph_property_node)
            for machine in self.machines:
                m = py2neo.Node(machine.type.name,
                                name=machine.name,
                                description=machine.description,
                                group=machine.group,
                                num_parts_in=machine.num_parts_in,
                                num_parts_out=machine.num_parts_out,
                                amount_in=machine.amount_in,
                                amount_out=machine.amount_out,
                                processing_time=machine.processing_time,
                                position_on_dash=machine.position_on_dash,
                                size_on_dash=machine.size_on_dash,
                                shape_on_dash=machine.shape_on_dash,
                                color_on_dash=machine.color_on_dash)
                tx.create(m)
                for sensor in machine.sensors:
                    s=py2neo.Node(dtTypes.dtTypes.SENSOR.name,
                                  name=sensor.name,
                                  type=sensor.type,
                                  description=sensor.description)
                    tx.create(s)
                    tx.create(py2neo.Relationship(m, "HAS_SENSOR", s))

            for buffer in self.queues:
                b = py2neo.Node(buffer.type.name,
                                name=buffer.name,
                                description=buffer.description,
                                group=buffer.group,
                                capacity=buffer.capacity,
                                amount=buffer.amount,
                                position_on_dash=buffer.position_on_dash,
                                size_on_dash=buffer.size_on_dash,
                                shape_on_dash=buffer.shape_on_dash,
                                color_on_dash=buffer.color_on_dash)
                tx.create(b)
                for part in buffer.parts:
                    p=py2neo.Node(part.type.name,
                                  name=part.name,
                                  type=part.type.name,
                                  description=part.description,
                                  uuid=part.uuid)
                    tx.create(p)
                    tx.create(py2neo.Relationship(b, "HAS_PART", p))
            tx.commit()

            nodes = py2neo.matching.NodeMatcher(g)
            tx = g.begin()
            for queue in self.queues:
                m1 = nodes.match(queue.frm.type.name, name=queue.frm.name).first()
                b = nodes.match(queue.type.name, name=queue.name).first()
                m2 = nodes.match(queue.to.type.name, name=queue.to.name).first()
                tx.create(py2neo.Relationship(m1, "DELIVERS_TO", b, type='INLET'))
                tx.create(py2neo.Relationship(b, "DELIVERS_TO", m2, type='OUTLET'))

            tx.commit()
            print('Serialized to neo4j successfully')
            ret_val=True

        else:
            print("I don't know how to do that. factory was not serialized")
            return False

        if plot:
            plt.figure(2)
            nx.draw(self.graph, node_color='lightblue',
                    with_labels=True,
                    node_size=500)

        return ret_val

    def populate_factory_from_json(self, json_data):

        # factory spec
        factory_spec_json = json_data['factory']
        self.name = factory_spec_json["name"]
        self.sim_hours = factory_spec_json["sim_hours"]

        #sensors
        sensors_json = json_data['sensors']
        self.sensors = []
        for s_j in sensors_json:
            self.sensors.append(dtSensor.dtSensor(json_data=s_j))

        #machines    
        machines_json = json_data['machines']
        self.machines = []
        for m_j in machines_json:
            machine = dtMachine.dtMachine(json_data=m_j)
            sensors_for_this_machine = []
            for s_name in machine.sensors:
                sensors_for_this_machine.append(self.get_sensor_by_name(s_name))
            machine.sensors = sensors_for_this_machine
            self.machines.append(machine)

        #parts
        parts_json = json_data['parts']
        self.parts = []
        for p_j in parts_json:
            self.parts.append(dtPart.dtPart(json_data=p_j))

        #queues
        queues_json = json_data['queues']
        self.queues = []
        for q_j in queues_json:
            queue = dtQueue.dtQueue(json_data=q_j)
            #we can do this because we already filled in the machine objects
            queue.frm = self.get_machine_by_name(q_j['frm'])
            queue.to = self.get_machine_by_name(q_j['to'])
            sensors_for_this_queue = []
            for s_name in queue.sensors:
                #we can do this because we already filled in the sensor objects
                sensors_for_this_queue.append(self.get_sensor_by_name(s_name))
            queue.sensors = sensors_for_this_queue
            parts_on_this_queue = []
            for p_uuid in queue.parts:
                #we can do this because we already filled in the parts objects
                parts_on_this_queue.append(self.get_part_by_uuid(p_uuid))
            queue.parts = parts_on_this_queue
            self.queues.append(queue)

        # put everything into the graph
        self.populate_networkx_graph()

    # reads graph from JSON file
    def deserialize(self, serial_type="networkx-json", file_path_or_uri="factory_graph.json", plot = False, **kwargs):
        #clean start
        self.__init__(flushAAS=True)
        if serial_type == "networkx-json":
            '''Function to deserialize a NetworkX DiGraph from a JSON file.'''
            call_graph = None
            with open(file_path_or_uri, 'r+') as _file:
                call_graph = nx.readwrite.json_graph.adjacency_graph(
                    jsonpickle.decode(_file.read()),
                    directed=True
                )
            self.graph = call_graph
            self.machines = self.graph.graph["machines"]
            self.queues = self.graph.graph["queues"]
            self.sensors = self.graph.graph["sensors"]
            self.parts = self.graph.graph["parts"]
        elif serial_type == "json":
            with open(file_path_or_uri, 'r+') as _file:
                json_data=json.load(_file)
                self.populate_factory_from_json(json_data)

        elif serial_type == "neo4j":
            if 'need_auth' in kwargs:
                if kwargs.get("need_auth").lower() == 'false':
                    g = py2neo.Graph(file_path_or_uri)
                else:
                    g = py2neo.Graph(file_path_or_uri, **kwargs)
            else:
                g = py2neo.Graph(file_path_or_uri, **kwargs)

            sensor_nodes = py2neo.matching.NodeMatcher(g).match("SENSOR")
            machine_nodes = py2neo.matching.NodeMatcher(g).match("MACHINE")
            process_nodes = py2neo.matching.NodeMatcher(g).match("PROCESS")
            buffer_nodes = py2neo.matching.NodeMatcher(g).match("BUFFER")
            container_nodes = py2neo.matching.NodeMatcher(g).match("CONTAINER")
            source_nodes = py2neo.matching.NodeMatcher(g).match("SOURCE")
            exit_nodes = py2neo.matching.NodeMatcher(g).match("EXIT")
            processed_part_nodes = py2neo.matching.NodeMatcher(g).match("PROCESSED_PART")
            single_part_nodes = py2neo.matching.NodeMatcher(g).match("SINGLE_PART")
            sensor_edges = py2neo.matching.RelationshipMatcher(g).match(r_type="HAS_SENSOR")
            part_edges = py2neo.matching.RelationshipMatcher(g).match(r_type="HAS_PART")

            graph_property_node = py2neo.matching.NodeMatcher(g).match('GRAPH_PROP_NODE').first()
            self.name = graph_property_node['name']
            self.sim_hours = graph_property_node['sim_hours']
            self.groups = graph_property_node['groups']

            self.parts = []
            self.sensors = []
            self.machines = []
            self.queues = []

            for s in sensor_nodes:
                if isinstance(s, py2neo.Node):
                    self.sensors.append(dtSensor.dtSensor(name=s['name'],
                                                          type=s['type'],
                                                          description=s['description']))

            for nodes_set in [processed_part_nodes, single_part_nodes]:
                for p in nodes_set:
                    if isinstance(p, py2neo.Node):
                        self.parts.append(dtPart.dtPart(name=p['name'],
                                                        type=dtTypes.dtTypes[p['type']],
                                                        description=p['description'],
                                                        uuid=p['uuid']))

            for nodes_set in [machine_nodes,process_nodes,source_nodes,exit_nodes]:
                for m in nodes_set:
                    if isinstance(m, py2neo.Node):
                        dtype = dtTypes.dtTypes[list(m.labels)[0]]
                        self.machines.append(dtMachine.dtMachine(name=m['name'],
                                                                 sensors=[],
                                                                 type = dtype,
                                                                 group = m['group'],
                                                                 description = m['description'],
                                                                 num_parts_in=m['num_parts_in'],
                                                                 num_parts_out=m['num_parts_out'],
                                                                 amount_in=m['amount_in'],
                                                                 amount_out=m['amount_out'],
                                                                 processing_time=m['processing_time'],
                                                                 position_on_dash=m['position_on_dash'],
                                                                 size_on_dash=m['size_on_dash'],
                                                                 shape_on_dash=m['shape_on_dash'],
                                                                 color_on_dash=m['color_on_dash']))


            for nodes_set in [buffer_nodes, container_nodes]:
                for b in nodes_set:
                    b_inlet =  py2neo.matching.RelationshipMatch(g, nodes = {b,b},r_type="DELIVERS_TO").where(type='INLET').first()
                    b_outlet = py2neo.matching.RelationshipMatch(g, nodes = {b,b},r_type="DELIVERS_TO").where(type='OUTLET').first()
                    if isinstance(b_inlet, py2neo.Relationship) and isinstance(b_outlet, py2neo.Relationship):
                        dtype = dtTypes.dtTypes[list(b.labels)[0]]
                        self._print_debug(dtype.name + ' {0}: amount: {1}'.format(b['name'],b['amount']))
                        self.queues.append(dtQueue.dtQueue(self.get_machine_by_name(b_inlet.nodes[0]['name']),
                                                           self.get_machine_by_name(b_outlet.nodes[1]['name']),
                                                           capacity=b['capacity'],
                                                           amount=b['amount'],
                                                           name=b['name'],
                                                           description=b['description'],
                                                           group=b['group'],
                                                           qtype=dtype,
                                                           position_on_dash=b['position_on_dash'],
                                                           size_on_dash=b['size_on_dash'],
                                                           shape_on_dash=b['shape_on_dash'],
                                                           color_on_dash=b['color_on_dash']))


            for e in sensor_edges:
                sensor_for_this_machine = self.get_sensor_by_name(e.nodes[1]['name'])
                self.get_machine_by_name(e.nodes[0]['name']).sensors.append(sensor_for_this_machine)

            for p in part_edges:
                queue_with_part = self.get_queue_by_name(p.nodes[0]['name'])
                part_for_this_queue = self.get_part_by_uuid(p.nodes[1]['uuid'])
                queue_with_part.parts.append(part_for_this_queue)

            self.populate_networkx_graph()

        else:
            print("I don't know how to do that. factory was not serialized")
            return False
        if plot:
            plt.figure(3)
            nx.draw(self.graph, node_color='lightblue',
                    with_labels=True,
                    node_size=500)



    def cytoscape_json_data(self):
        """Returns data in Cytoscape JSON format (cyjs).
        
    
        Returns
        -------
        data: list
        A list with cyjs formatted data.
            
        """
        USE_GROUPS = False
        # Define dictionary of empty network
        jsondata = []
        if USE_GROUPS:
            for g in self.groups:
                #{'data': {'id': 'pbox', 'label': 'Parent Box'}},
                n = {
                    'data': {'id': [],'label': []},
                    'style': {'shape':'','background-color':'','height':'','width':'' }
                }
                n["data"]["id"] = g
                n["data"]["label"] = g
                n["data"]["type"] = 'GROUP'
                n["classes"] = 'GROUP'

                if g != 'NONE':
                    jsondata.append(n)

        for machine in self.machines:
            #{'data': {'id': 'three', 'label': 'Node 3', 'parent': 'pbox'},
            #'position': {'x': 0, 'y': 300},
            #'style': {'shape': 'star',
            #          'color': 'green',
            #          'background-color': 'purple'}}
            n = {
                'data': {'id': [],'label': [], 'type': [], 'parent': []},
                'group': [],
                'classes': [],
                'position': {'x':[],'y':[] },
                'style': {'shape':'','background-color':'','height':'','width':'' }
            }

            #{'data': {'id': 'four', 'label': 'Node 4', 'parent': 'pbox'}
            n["data"]["id"] = machine.name
            n["data"]["label"] = machine.description
            n["data"]["type"] = machine.type.name
            if machine.group != 'NONE' and USE_GROUPS:
                n["data"]["parent"] = machine.group
            n["group"] = 'nodes'
            n["classes"] = machine.type.name
            #'position': {'x': -100, 'y': 300},
            n["position"]["x"] = machine.position_on_dash[0]
            n["position"]["y"] = machine.position_on_dash[1]
            n["style"]["shape"] = machine.shape_on_dash
            n["style"]["background-color"] = machine.color_on_dash
            n["style"]["width"] = machine.size_on_dash[0]
            n["style"]["height"] = machine.size_on_dash[1]
            #if machine.type == dtTypes.dtTypes.EXIT or machine.type == dtTypes.dtTypes.SOURCE:
            #    n["style"]["opacity"] = 0
            jsondata.append(n)


            for s in machine.sensors:
                n = {
                    'data': {'id': [],'label': [], 'type': []},
                    'group': [],
                    'classes': [],
                    'position': {'x':[],'y':[] }
                }
                n["data"]["id"] = s.name
                n["data"]["label"] = s.description
                n["data"]["type"] = s.type
                n["group"] = 'nodes'
                if machine.group != 'NONE' and USE_GROUPS:
                    n["data"]["parent"] = machine.group
                n["classes"] = 'SENSOR'
                #'position': {'x': -100, 'y': 300},
                n["position"]["x"] = machine.position_on_dash[0] + machine.size_on_dash[0]*0.3
                n["position"]["y"] = machine.position_on_dash[1] + machine.size_on_dash[1]*0.3
                jsondata.append(n)

        for queue in self.queues:
            n = {
                'data': {'id': [],'label': [], 'type': [], 'weight': [],'color':[],'parent': []},
                'group': [],
                'classes': [],
                'position': {'x':[],'y':[] },
                'style': {'shape':'','background-color':'','height':'','width':'' }
            }
            #{'data': {'id': 'four', 'label': 'Node 4', 'parent': 'pbox'}
            buffer_color_code = "black"
            if len(queue.parts) <= 1:
                buffer_color_code = "green"
            elif len(queue.parts) <=3:
                buffer_color_code = "#ff7b00" #orange
            else:
                buffer_color_code = "red"
            n["data"]["id"] = queue.name
            n["data"]["weight"] = queue.amount
            n["data"]["color"] = buffer_color_code
            n["data"]["label"] = queue.description
            n["data"]["type"] = queue.type.name
            if queue.group != 'NONE' and USE_GROUPS:
                n["data"]["parent"] = queue.group
            n["group"] = 'nodes'
            n["classes"] = queue.type.name
            n["position"]["x"] = queue.position_on_dash[0]
            n["position"]["y"] = queue.position_on_dash[1]
            n["style"]["shape"] = queue.shape_on_dash
            n["style"]["background-color"] = queue.color_on_dash
            #n["style"]["border-color"] = buffer_color_code
            #n["style"]["color"] = buffer_color_code
            n["style"]["width"] = queue.size_on_dash[0]
            n["style"]["height"] = queue.size_on_dash[1]
            jsondata.append(n)

            # create part nodes
            num_of_parts = len(queue.parts)
            buffer_center = queue.position_on_dash
            def PointsInCircum(r=10,n=100,C=(0,0)):
                points = []
                if n>0:
                    points = [[math.cos(2*math.pi/n*x)*r+ C[0],math.sin(2*math.pi/n*x)*r+ C[1]]  for x in range(0,n+1)]
                return points

            parts_locations = PointsInCircum(r=20, n=num_of_parts, C=buffer_center) # locations on dash around buffer
            for (p, pt) in zip(queue.parts, parts_locations):
                if p is None:
                    continue
                n = {
                    'data': {'id': [],'label': [], 'type': [], 'name': []},
                    'group': [],
                    'classes': [],
                    'position': {'x':[],'y':[] }
                }
                n["data"]["id"] = p.uuid
                n["data"]["label"] = p.description
                n["data"]["type"] = p.type.name
                n["data"]["name"] = p.name
                n["group"] = 'nodes'
                n["classes"] = p.type.name
                n["position"]["x"] = pt[0]
                n["position"]["y"] = pt[1]
                jsondata.append(n)

        for queue in self.queues:
            n = {
                'data': {'source': [],'target': []},
                'classes': []
            }
            n["data"]["source"] = queue.frm.name#machine
            n["data"]["target"] = queue.name#buffer            
            n["group"] = 'edges'
            n["classes"] = 'machine_edge'
            jsondata.append(n)

            n = {
                'data': {'source': [],'target': []},
                'classes': []
            }
            n["data"]["source"] = queue.name#buffer
            n["data"]["target"] = queue.to.name#machine 
            n["group"] = 'edges'
            n["classes"] = 'machine_edge'
            jsondata.append(n)

            # create edges between parts and buffers 
            for p in queue.parts:
                if p is None:
                    continue
                n = {
                    'data': {'source': [],'target': []},
                    'classes': []
                }
                n["data"]["source"] = queue.name#buffer
                n["data"]["target"] = p.uuid
                n["group"] = 'edges'
                n["classes"] = 'part_edge'
                jsondata.append(n)

        # create edges between sensors and machines    
        for machine in self.machines:
            for sensor in machine.sensors:
                n = {
                    'data': {'source': [],'target': []},
                    'classes': [],
                    'style': {}
                }
                n["data"]["source"] = machine.name
                n["data"]["target"] = sensor.name
                n["group"] = 'edges'
                n["classes"] = 'sensor_edge'
                jsondata.append(n)


        return jsondata

    def populate_networkx_graph(self):
        if 0 == len(self.machines) or 0 == len(self.queues):
            return False

        # create random graph
        self.graph = nx.DiGraph()

        # add machines as nodes and queues as edges
        for m in self.machines:
            self.graph.add_node(m,
                                name=m.name,
                                description=m.description,
                                group=m.group,
                                type=m.type,
                                num_parts_in=m.num_parts_in,
                                num_parts_out=m.num_parts_out,
                                amount_in=m.amount_in,
                                amount_out=m.amount_out,
                                processing_time=m.processing_time,
                                position_on_dash=m.position_on_dash)

        for q in self.queues:
            self.graph.add_edge(q.frm, q.to,
                                capacity=q.capacity,
                                amount=q.amount,
                                description=q.description,
                                name=q.name,
                                group=q.group,
                                position_on_dash=q.position_on_dash,
                                type=q.type)

        return True

    def generate_random_factory_topology(self, num_of_machines = 15):

        self.name = "Random example factory"
        # probability of a queue being created between machines that are nodes
        # the lower the less connections between machnes
        p = 0.00001
        MAX_NUM_OF_SENSORS_PER_MACHINE = 3
        MAX_QUEUE_CAPACITY = 1000
        KINDS_OF_SENSORS = ['temperature', 'vibration', 'counter']

        # create machines
        self.machines = []
        for idx in range(num_of_machines):
            self.machines.append(dtMachine.dtMachine('M'+str(idx)))

        self.sensors = []
        # create sensors
        for m in self.machines:
            number_of_sensors_for_this_machine = random.randint(0,MAX_NUM_OF_SENSORS_PER_MACHINE)
            m.sensors = []
            for idx in range(number_of_sensors_for_this_machine):
                s = dtSensor.dtSensor('S'+m.name[1:]+'_'+str(idx), random.choice(KINDS_OF_SENSORS))
                m.sensors.append(s)
            # append sensors to a machine
            self.sensors.extend(m.sensors)

        #create queues
        n = len(self.machines)
        edges = itertools.combinations(range(n), 2)
        self.queues = []

        # sorted by the key   
        for _, node_edges in itertools.groupby(edges, key=lambda x: x[0]):
            node_edges = list(node_edges)
            random_edge = random.choice(node_edges)
            self.queues.append(dtQueue.dtQueue(self.machines[random_edge[0]],
                                               self.machines[random_edge[1]],
                                               capacity=random.randint(1,MAX_QUEUE_CAPACITY)))

            for e in node_edges:
                if random.random() < p:
                    self.queues.append(dtQueue.dtQueue(self.machines[e[0]],
                                                       self.machines[e[1]],
                                                       capacity=random.randint(1,MAX_QUEUE_CAPACITY)))

        # create random graph
        self.populate_networkx_graph()

        exit_nodes = [x for x in self.graph.nodes() if self.graph.out_degree(x)==0]
        source_nodes = [x for x in self.graph.nodes() if self.graph.in_degree(x)==0]

        # make exits out of leaves with ingoing edges
        for machine in exit_nodes:
            self.get_machine_by_name(machine.name).type = dtTypes.dtTypes.EXIT
            self.get_machine_by_name(machine.name).name = self.get_machine_by_name(machine.name).name.replace('M','E')
            self.get_machine_by_name(machine.name).num_parts_in = 0
            self.get_machine_by_name(machine.name).num_parts_out = 0

        # setting up the inventory:
        NUM_OF_PARTS = 100
        self.parts = []
        for idx in range(NUM_OF_PARTS):
            self.parts.append(dtPart.dtPart('Pa'+str(idx), type=dtTypes.dtTypes.SINGLE_PART))

            # make sources out of leaves with outgoing edges
        for machine in source_nodes:
            for edge in self.graph.edges(machine, data=True):
                self.get_queue_by_name(edge[2]['name']).capacity = 1000
                self.get_queue_by_name(edge[2]['name']).parts = self.parts
                self.get_queue_by_name(edge[2]['name']).create_store()

            self.get_machine_by_name(machine.name).type = dtTypes.dtTypes.SOURCE
            self.get_machine_by_name(machine.name).name = self.get_machine_by_name(machine.name).name.replace('M','S')
            self.get_machine_by_name(machine.name).num_parts_in = 0
            self.get_machine_by_name(machine.name).num_parts_out = 0

        # repopulate graph as we changed the member machines and queues
        self.populate_networkx_graph()

        return True

    def generate_factory_data(self, duration_h=3):
        c = f.DTPrototypeInfluxDbClient(cfg.PATH_TO_CONFIG)

        date_rng = pd.date_range(start=pd.Timestamp(datetime.datetime.now()-datetime.timedelta(hours=duration_h)), end=pd.Timestamp(datetime.datetime.now()), freq='1T')

        df = pd.DataFrame(date_rng, columns=['time_ms'])
        df['data 0'] = np.random.randint(0,50,size=(len(date_rng)))
        df['data 1'] = np.random.randint(0,100,size=(len(date_rng)))

        time_ms_array = np.zeros(len(date_rng))
        for index, row in df.iterrows():
            time_ms_array[index] = int(row['time_ms'].timestamp()*1000)

        df['data 2'] = np.sin(time_ms_array)*70
        df['data 3'] = np.random.randint(0,100,size=(len(date_rng)))+np.sin(time_ms_array)*5

        for m in self.machines:
            for s in m.sensors:
                tags = {'machine': m.name, 'sensor': s.name}
                print("machine=%s, sensor=%s: " % (m.name, s.name))
                c.store_any_measurement(str(s.type), tags, df['data '+ str(random.randint(0,3))].to_numpy().tolist(), time_ms_array)

    def create_sim_graph(self):

        self.name = "Example factory for discrete event simulation"

        S1_1 = dtSensor.dtSensor('S1_1', 'temperature')
        self.sensors = [S1_1]

        #create machines as objects:
        M1 = dtMachine.dtMachine('M1', sensors=[S1_1], description='This is a really cool machine', type=dtTypes.dtTypes.MACHINE, position_on_dash=(300,350))

        S1 = dtMachine.dtMachine('S1', sensors=[], description='Source', type=dtTypes.dtTypes.SOURCE, position_on_dash=(100,400))
        S1.num_parts_in = 0
        S1.num_parts_out = 0
        E1 = dtMachine.dtMachine('E1', sensors=[], description='Exit', type=dtTypes.dtTypes.EXIT, position_on_dash=(500,400))
        E1.num_parts_out = 0
        E1.num_parts_in = 0
        self.machines = [S1, M1, E1]

        self.parts = []
        for idx in range(3):
            self.parts.append(dtPart.dtPart('Pa'+str(idx), type=dtTypes.dtTypes.SINGLE_PART))

        #creating queues as objects:
        Q1 = dtQueue.dtQueue(S1, M1, capacity=10, parts = self.parts, name='Q1', description='This is a big buffer', position_on_dash=(200,400))
        Q2 = dtQueue.dtQueue(M1, E1, capacity=10, name='Q2',description='This is a small buffer', position_on_dash=(400,400))
        self.queues = [Q1, Q2]

        #create graph
        self.populate_networkx_graph()

        return True

    def create_example_graph(self):

        self.name = "Example factory"

        #create sensors as objects:
        S1_1 = dtSensor.dtSensor('S1_1', 'temperature')
        S1_2 = dtSensor.dtSensor('S1_2', 'vibration')
        S2_1 = dtSensor.dtSensor('S2_1', 'temperature')
        S3_1 = dtSensor.dtSensor('S3_1', 'temperature')
        S4_1 = dtSensor.dtSensor('S4_1', 'vibration')
        S4_2 = dtSensor.dtSensor('S4_2', 'temperature')
        self.sensors = [S1_1, S1_2, S2_1, S3_1, S4_1, S4_2]

        #create machines as objects:
        M1 = dtMachine.dtMachine('M1', sensors=[S1_1, S1_2], description='This is a really cool machine.', position_on_dash=(100,150))
        M2 = dtMachine.dtMachine('M2', sensors=[S2_1], description='This machine produces stuff.', position_on_dash=(200,250))
        M3 = dtMachine.dtMachine('M3', sensors=[S3_1], description='This machine is amazing.', position_on_dash=(300,250))
        M3.processing_time = 2
        M4 = dtMachine.dtMachine('M4', sensors=[S4_1, S4_2], description='Wow, what a nice machine!', position_on_dash=(300,300))
        M5 = dtMachine.dtMachine('M5', sensors=[], description='Oh look, another Machine.', position_on_dash=(400,250))
        S1 = dtMachine.dtMachine('S1', sensors=[], description='Source machine.', type=dtTypes.dtTypes.SOURCE, position_on_dash=(100,100))
        S1.num_parts_in = 0
        S1.num_parts_out = 0
        E1 = dtMachine.dtMachine('E1', sensors=[], description='Exit machine.', type=dtTypes.dtTypes.EXIT, position_on_dash=(500,250))
        E1.num_parts_in = 0
        E1.num_parts_out = 0
        self.machines = [S1, M1, M2, M3, M4, M5, E1]

        # setting up the inventory:
        NUM_OF_PARTS = 10
        self.parts = []
        for idx in range(NUM_OF_PARTS):
            self.parts.append(dtPart.dtPart('Pa'+str(idx), type=dtTypes.dtTypes.SINGLE_PART))

        #creating queues as objects:
        Q_S1 = dtQueue.dtQueue(S1, M1, capacity=30, parts=self.parts, position_on_dash=(100,100))
        Q1_2 = dtQueue.dtQueue(M1, M2, capacity=5, position_on_dash=(150,200))
        Q2_3 = dtQueue.dtQueue(M2, M3, capacity=5, position_on_dash=(250,250))
        Q3_5 = dtQueue.dtQueue(M3, M5, capacity=5, position_on_dash=(350,300))
        Q4_5 = dtQueue.dtQueue(M4, M5, capacity=5, position_on_dash=(250,250))
        Q_E1 = dtQueue.dtQueue(M5, E1, capacity=50, position_on_dash=(250,250))
        Q2_4 = dtQueue.dtQueue(M2, M4, capacity=5, position_on_dash=(500,250))
        self.queues = [Q_S1, Q1_2, Q2_3, Q3_5, Q4_5, Q2_4, Q_E1]

        #create graph        
        self.populate_networkx_graph()

        return True