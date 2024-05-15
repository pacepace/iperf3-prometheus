from flask import Flask, request, jsonify
import json
import multiprocessing
import os
from prometheus_client import Gauge, generate_latest, REGISTRY, push_to_gateway
from prometheus_client.core import CollectorRegistry
import psutil
import socket
import subprocess
import time

# constants
JOB_NAME = 'iperf3'

# update metrics
def update_metrics(zero=False):

    # metric registry
    registry = CollectorRegistry()

    iperf3_bits_per_second_receive = Gauge('iperf3_bits_per_second_receive', 'Bits per second', registry=registry)
    iperf3_bits_per_second_sent = Gauge('iperf3_bits_per_second_sent', 'Bits per second', registry=registry)
    iperf3_bits_per_second_reverse_receive = Gauge('iperf3_bits_per_second_reverse_receive', 'Bits per second', registry=registry)
    iperf3_bits_per_second_reverse_sent = Gauge('iperf3_bits_per_second_reverse_sent', 'Bits per second', registry=registry)
    iperf3_bytes_receive = Gauge('iperf3_bytes_receive', 'Bytes', registry=registry)
    iperf3_bytes_sent = Gauge('iperf3_bytes_sent', 'Bytes', registry=registry)
    iperf3_bytes_reverse_receive = Gauge('iperf3_bytes_reverse_receive', 'Bytes', registry=registry)
    iperf3_bytes_reverse_sent = Gauge('iperf3_bytes_reverse_sent', 'Bytes', registry=registry)
    iperf3_jitter_receive = Gauge('iperf3_jitter_receive', 'Jitter in milliseconds', registry=registry)
    iperf3_jitter_sent = Gauge('iperf3_jitter_sent', 'Jitter in milliseconds', registry=registry)
    iperf3_jitter_reverse_receive = Gauge('iperf3_jitter_reverse_receive', 'Jitter in milliseconds', registry=registry)
    iperf3_jitter_reverse_sent = Gauge('iperf3_jitter_reverse_sent', 'Jitter in milliseconds', registry=registry)
    iperf3_packets_lost_receive = Gauge('iperf3_packets_lost_receive', 'Lost packets', registry=registry)
    iperf3_packets_lost_sent = Gauge('iperf3_packets_lost_sent', 'Lost packets', registry=registry)
    iperf3_packets_lost_reverse_receive = Gauge('iperf3_packets_lost_reverse_receive', 'Lost packets', registry=registry)
    iperf3_packets_lost_reverse_sent = Gauge('iperf3_packets_lost_reverse_sent', 'Lost packets', registry=registry)
    iperf3_packets_lost_percentage_receive = Gauge('iperf3_packets_lost_percentage_receive', 'Lost packets percentage', registry=registry)
    iperf3_packets_lost_percentage_sent = Gauge('iperf3_packets_lost_percentage_sent', 'Lost packets percentage', registry=registry)
    iperf3_packets_lost_percentage_reverse_receive = Gauge('iperf3_packets_lost_percentage_reverse_receive', 'Lost packets percentage', registry=registry)
    iperf3_packets_lost_percentage_reverse_sent = Gauge('iperf3_packets_lost_percentage_reverse_sent', 'Lost packets percentage', registry=registry)
    iperf3_out_of_order_receive = Gauge('iperf3_out_of_order_receive', 'Out of order packets', registry=registry)
    iperf3_out_of_order_sent = Gauge('iperf3_out_of_order_sent', 'Out of order packets', registry=registry)
    iperf3_out_of_order_reverse_receive = Gauge('iperf3_out_of_order_reverse_receive', 'Out of order packets', registry=registry)
    iperf3_out_of_order_reverse_sent = Gauge('iperf3_out_of_order_reverse_sent', 'Out of order packets', registry=registry)

    try:
        if not zero:
            # read json log
            with open('./iperf3_log.json', 'r') as f:
                data = f.read()
            data = '[' + data.replace('}\n{', '},{') + ']'
            # print(f'data: {data}')
            jsondata = json.loads(data)

            # find last 'end' section
            end_data = None
            for entry in jsondata:
                if 'end' in entry:
                    end_data = entry['end']

            if end_data:
                # TODO: better logic here to handle different formats of 'end' section
                try:
                    sum_receive = end_data['sum_received']
                except KeyError:
                    sum_receive = {}
                    try:
                        sum_receive = end_data['sum']
                        if end_data['sum']['sender'] == True:
                            sum_receive = {}
                    except KeyError:
                        sum_receive = {}
                try:
                    sum_sent = end_data['sum_sent']
                except KeyError:
                    sum_sent = {}
                    try:
                        sum_receive = end_data['sum']
                        if end_data['sum']['sender'] == False:
                            sum_sent = {}
                    except KeyError:
                        sum_receive = {}
                try:
                    sum_reverse_receive = end_data['sum_received_bidir_reverse']
                except KeyError:
                    sum_reverse_receive = {}
                try:
                    sum_reverse_sent = end_data['sum_sent_bidir_reverse']
                except KeyError:
                    sum_reverse_sent = {}
            else:
                sum_receive = {}
                sum_sent = {}
                sum_reverse_receive = {}
                sum_reverse_sent = {}
        else:
            sum_receive = {}
            sum_sent = {}
            sum_reverse_receive = {}
            sum_reverse_sent = {}
        
        iperf3_bits_per_second_receive.set(sum_receive.get('bits_per_second', 0))
        iperf3_bits_per_second_sent.set(sum_sent.get('bits_per_second', 0))
        iperf3_bits_per_second_reverse_receive.set(sum_reverse_receive.get('bits_per_second', 0))
        iperf3_bits_per_second_reverse_sent.set(sum_reverse_sent.get('bits_per_second', 0))
        iperf3_bytes_receive.set(sum_receive.get('bytes', 0))
        iperf3_bytes_sent.set(sum_sent.get('bytes', 0))
        iperf3_bytes_reverse_receive.set(sum_reverse_receive.get('bytes', 0))
        iperf3_bytes_reverse_sent.set(sum_reverse_sent.get('bytes', 0))
        iperf3_jitter_receive.set(sum_receive.get('jitter_ms', 0))
        iperf3_jitter_sent.set(sum_sent.get('jitter_ms', 0))
        iperf3_jitter_reverse_receive.set(sum_reverse_receive.get('jitter_ms', 0))
        iperf3_jitter_reverse_sent.set(sum_reverse_sent.get('jitter_ms', 0))
        iperf3_packets_lost_receive.set(sum_receive.get('lost_packets', 0))
        iperf3_packets_lost_sent.set(sum_sent.get('lost_packets', 0))
        iperf3_packets_lost_reverse_receive.set(sum_reverse_receive.get('lost_packets', 0))
        iperf3_packets_lost_reverse_sent.set(sum_reverse_sent.get('lost_packets', 0))
        iperf3_packets_lost_percentage_receive.set(sum_receive.get('lost_percent', 0))
        iperf3_packets_lost_percentage_sent.set(sum_sent.get('lost_percent', 0))
        iperf3_packets_lost_percentage_reverse_receive.set(sum_reverse_receive.get('lost_percent', 0))
        iperf3_packets_lost_percentage_reverse_sent.set(sum_reverse_sent.get('lost_percent', 0))
        iperf3_out_of_order_receive.set(sum_receive.get('out_of_order', 0))
        iperf3_out_of_order_sent.set(sum_sent.get('out_of_order', 0))
        iperf3_out_of_order_reverse_receive.set(sum_reverse_receive.get('out_of_order', 0))
        iperf3_out_of_order_reverse_sent.set(sum_reverse_sent.get('out_of_order', 0))
        
        # push to gateway
        push_to_gateway('localhost:9200', job=JOB_NAME, registry=registry)
        
    except FileNotFoundError:
        print("iperf3_log.json file not found")
    except json.JSONDecodeError as err:
        print(f'json.JSONDecodeError: {err}')
    except Exception as err:
        print(f'Exception: {err}')

# iperf3 server
def iperf3_server():
    while True:
        try:
            # remove log file
            try:
                print('... removing log ...')
                os.remove('./iperf3_log.json')
            except FileNotFoundError:
                pass
            print('... iperf3 server running ...')
            iperf3_server = subprocess.Popen(['iperf3', '-s', '--json', '--one-off', '--logfile', 'iperf3_log.json'])
            stdout, _ = iperf3_server.communicate()
            # print(stdout.decode())
            # update the metrics for retrieval after test completion
            print('... updating metrics ...')
            update_metrics()
        except Exception as err:
            print(f'Exception: {err}')
            time.sleep(5)

# iperf3 monitor
def iperf3_monitor(iperf3pid):

    def network_activity_check(pid, port, proto):
        active = False
        try:
            # get process
            proc = psutil.Process(pid)
            # get process children
            children = proc.children(recursive=True)
            # check childr connections
            for child in children:
                connections = child.connections(kind='inet')
                # print(f'connections: {connections}')
                for conn in connections:
                    # udp
                    if proto == 'udp':
                        if conn.laddr.port == port and conn.type == socket.SOCK_DGRAM:
                            # check if there is remote address
                            if conn.raddr:
                                active = True
                    # tcp
                    elif proto == 'tcp':
                        if conn.laddr.port == port and conn.type == socket.SOCK_STREAM:
                            # check if there is remote address
                            if conn.raddr:
                                active = True
        except psutil.NoSuchProcess:
            active = False
        except Exception as err:
            print(f'-- exception: {err}')
            active = False
        return active

    while True:
        time.sleep(1)
        if (not network_activity_check(iperf3pid, 5201, 'udp')) and (not network_activity_check(iperf3pid, 5201, 'tcp')):
            time.sleep(5)
            if (not network_activity_check(iperf3pid, 5201, 'udp')) and (not network_activity_check(iperf3pid, 5201, 'tcp')):
                # print('... iperf3 server not connected ...')
                update_metrics(zero=True)

# create and start iperf3_server
iperf3 = multiprocessing.Process(target=iperf3_server)
iperf3.daemon = True
iperf3.start()

# create and start iperf3 monitoring process
iperf3monitor = multiprocessing.Process(target=iperf3_monitor, args=(iperf3.pid,)) # yes it needs the comma
iperf3monitor.daemon = True
iperf3monitor.start()

# flask app
app = Flask(__name__)

# metrics store
metrics_store = {JOB_NAME: {}}

# push gateway
@app.route('/metrics/job/<job_name>', methods=['PUT'])
def metrics_put(job_name):

    # get data from request
    data = request.get_data(as_text=True)

    # store data
    metrics_store[job_name] = data
    
    # return success
    return jsonify({"status": "success"}), 200

# return metrics for scraping
@app.route('/metrics', methods=['GET'])
def metrics_get():
    # return metrics
    return metrics_store[JOB_NAME], 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9200)
