from __future__ import print_function

import argparse
import os
import sys

from gazebo_msgs.srv import SpawnModel
from gazebo_msgs.srv import SpawnModelRequest
from rospy import ServiceProxy
from xacro import parse
from xacro import process_doc


def main():
    parser = argparse.ArgumentParser('Spawn vehicle.')
    parser.add_argument('vehicle_type', choices=['iris', 'plane'])
    parser.add_argument('suffix', default='')
    parser.add_argument('-x', type=float, default=0.0)
    parser.add_argument('-y', type=float, default=0.0)
    parser.add_argument('--color', choices=['blue', 'gold'])
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    spawn(args.vehicle_type, args.suffix, args.x, args.y, args.color, args.debug)


def spawn(vehicle_type, suffix, x, y, color, debug):
    srv = ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)

    model_filename = os.path.join(
        os.path.dirname(__file__), '..', '..', '..', '..',
        'share', 'uctf', 'models',
        '%s' % vehicle_type, '%s.sdf' % vehicle_type)
    with open(model_filename, 'r') as h:
        model_xml = h.read()

    kwargs = {
        'mappings': {},
    }
    if color:
        material_name = 'Gazebo/%s' % color.capitalize()
        kwargs['mappings']['visual_material'] = material_name
    model_xml = xacro(model_xml, **kwargs)
    if debug:
        print(model_xml)

    req = SpawnModelRequest()
    unique_name = vehicle_type + suffix
    req.model_name = unique_name
    req.model_xml = model_xml
    req.robot_namespace = unique_name
    req.initial_pose.position.x = x
    req.initial_pose.position.y = y
    req.initial_pose.position.z = 0.0
    req.initial_pose.orientation.x = 0.0
    req.initial_pose.orientation.y = 0.0
    req.initial_pose.orientation.z = 0.0
    req.initial_pose.orientation.w = 1.0
    req.reference_frame = ''

    resp = srv(req)
    if resp.success:
        print(resp.status_message)
        return 0
    else:
        print(resp.status_message, file=sys.stderr)
        return 1


def xacro(template_xml, **kwargs):
    doc = parse(template_xml)
    process_doc(doc, **kwargs)
    return doc.toprettyxml(indent='  ')
