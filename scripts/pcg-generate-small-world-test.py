# !/usr/bin/env python
# Copyright (c) 2020 - The Procedural Generation for Gazebo authors
# For information on the respective copyright owner see the NOTICE file
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import argparse
import datetime
from pcg_gazebo.simulation import SimulationModel, \
    add_custom_gazebo_resource_path
from pcg_gazebo.generators.creators import extrude
from pcg_gazebo.generators.shapes import random_rectangles, \
    random_rectangle, random_points_to_triangulation
from pcg_gazebo.generators import WorldGenerator


if __name__ == '__main__':
    description = \
        'Generates a sample world with walls ' \
        'and objects as primitives'
    usage_text = '''Usage:
    pcg-generate-sample-world-with-walls --n-rectangles 1
    pcg-generate-sample-world-with-walls --n-rectangles 10
    pcg-generate-sample-world-with-walls --n-points 20
    pcg-generate-sample-world-with-walls --n-rectangles 10 --n-cubes 5 --n-spheres 5 --n-cylinders 5
    pcg-generate-sample-world-with-walls --n-rectangles 10 --n-cubes 5 --n-spheres 5 --n-cylinders 5 --set-random-roll --set-random-pitch
    pcg-generate-sample-world-with-walls --n-points 20 --n-cubes 10 --preview
    '''
    parser = argparse.ArgumentParser(
        description=description,
        epilog=usage_text,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--n-rectangles',
        '-r',
        type=int,
        help='Number of rectangles to merge to generate the room')
    parser.add_argument(
        '--n-points',
        '-p',
        type=int,
        help='Number of points to triangulate to generate the room')
    parser.add_argument(
        '--wall-thickness',
        '-t',
        type=float,
        default=0.1,
        help='Thickness of the walls')
    parser.add_argument(
        '--wall-height',
        '-g',
        type=float,
        default=2.0,
        help='Height of the walls')
    parser.add_argument(
        '--n-cubes',
        '-c',
        type=int,
        default=0,
        help='Number of cubes to place in the world')
    parser.add_argument(
        '--n-cylinders',
        '-l',
        type=int,
        default=0,
        help='Number of cylinders to place in the world')
    parser.add_argument(
        '--n-spheres',
        '-s',
        type=int,
        default=0,
        help='Number of spheres to place in the world')
    parser.add_argument(
        '--set-random-roll',
        action='store_true',
        help='Set the roll angle of the placed objects with a random variable')
    parser.add_argument(
        '--set-random-pitch',
        action='store_true',
        help='Set the pitch angle of the placed objects with a random variable')
    parser.add_argument(
        '--x-room-range',
        '-x',
        type=float,
        default=50,
        help='Range in X to generate the rectangles or points')
    parser.add_argument(
        '--y-room-range',
        '-y',
        type=float,
        default=50,
        help='Range in Y to generate the rectangles or points')
    parser.add_argument(
        '--world-name',
        '-n',
        type=str,
        default='pcg_sample',
        help='Name of output world')
    parser.add_argument(
        '--export-world-dir',
        type=str,
        default=os.path.join(os.path.expanduser('~'), '.gazebo', 'worlds'),
        help='Export the world')
    parser.add_argument(
        '--export-models-dir',
        type=str,
        default=os.path.join(os.path.expanduser('~'), '.gazebo', 'models'),
        help='Export the models generated')
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Show 3D preview of the created world')

    args = parser.parse_args()

    assert args.n_cubes >= 0, \
        'Number of cubes must be greater or equal to 0'
    assert args.n_cylinders >= 0, \
        'Number of cylinders must be greater or equal to 0'
    assert args.n_spheres >= 0, \
        'Number of spheres must be greater or equal to 0'
    assert args.wall_height > 0, \
        'Wall height must be greater than 0'
    assert args.wall_thickness > 0, \
        'Wall thickness must be greater than 0'
    assert args.x_room_range > 0, \
        'X room range must be greater than 0'
    assert args.y_room_range > 0, \
        'Y room range must be greater than 0'

    if args.world_name is not None:
        world_name = args.world_name
    else:
        world_name = datetime.datetime.now().isoformat()
        world_name = world_name.replace(':', '_')
        world_name = world_name.replace('.', '_')

    # Generate the reference polygon for the wall boundaries
    if args.n_rectangles is not None:
        if args.n_rectangles > 1:
            wall_polygon = random_rectangles(
                n_rect=args.n_rectangles,
                x_center_min=-args.x_room_range / 2.,
                x_center_max=args.x_room_range / 2.,
                y_center_min=-args.y_room_range / 2.,
                y_center_max=args.y_room_range / 2.,
                delta_x_min=args.x_room_range / 2.,
                delta_x_max=args.x_room_range,
                delta_y_min=args.y_room_range / 2.,
                delta_y_max=args.y_room_range)
        elif args.n_rectangles == 1:
            wall_polygon = random_rectangle(
                delta_x_min=args.x_room_range / 2.,
                delta_x_max=args.x_room_range,
                delta_y_min=args.y_room_range / 2.,
                delta_y_max=args.y_room_range)
        else:
            raise ValueError(
                'Number of rectangles is invalid, provided={}'.format(
                    args.n_rectangles))
    elif args.n_points is not None:
        if args.n_points < 3:
            raise ValueError(
                'Number of points for triangulation must be at least 3,'
                ' provided={}'.format(args.n_points))
        wall_polygon = random_points_to_triangulation(
            args.n_points)
    else:
        raise ValueError(
            'No number of rectangles and no number of points for'
            ' triangulation were provided')

    # Create the wall model based on the extruded
    # boundaries of the polygon
    walls_model = extrude(
        polygon=wall_polygon,
        thickness=args.wall_thickness,
        height=args.wall_height,
        pose=[0, 0, args.wall_height / 2., 0, 0, 0],
        extrude_boundaries=True,
        color='xkcd')
    walls_model.name = world_name + '_walls'

    # Create a world generator to place
    # objects in the world
    world_generator = WorldGenerator()

    # Add walls and ground plane to the world
    world_generator.world.add_model(
        tag=walls_model.name,
        model=walls_model)
    world_generator.world.add_model(
        tag='ground_plane',
        model=SimulationModel.from_gazebo_model('ground_plane'))

    # Retrieve the free space polygon where objects
    # can be placed within the walls
    free_space_polygon = world_generator.world.get_free_space_polygon(
        ground_plane_models=[walls_model.name],
        ignore_models=['ground_plane'])

    # Add the workspace constraint to the
    # generator
    world_generator.add_constraint(
        name='room_workspace',
        type='workspace',
        frame='world',
        geometry_type='polygon',
        polygon=free_space_polygon
    )

    # Add constraint to place all object
    # tangent to the ground
    world_generator.add_constraint(
        name='tangent_to_ground_plane',
        type='tangent',
        frame='world',
        reference=dict(
            type='plane',
            args=dict(
                origin=[0, 0, 0],
                normal=[0, 0, 1]
            )
        )
    )

    # Add assets
    models = dict()
    if args.n_cubes is not None and args.n_cubes > 0:
        world_generator.add_asset(
            tag='box',
            description=dict(
                type='box',
                args=dict(
                    size="__import__('numpy').random.uniform(0.1, 1, 3)",
                    name='cuboid',
                    color='xkcd'
                )
            )
        )
        models['box'] = args.n_cubes

    if args.n_cylinders is not None and args.n_cylinders > 0:
        world_generator.add_asset(
            tag='cylinder',
            description=dict(
                type='cylinder',
                args=dict(
                    radius="__import__('numpy').random.uniform(0.1, 1)",
                    length="__import__('numpy').random.uniform(0.1, 1)",
                    name='cylinder',
                    color='xkcd'
                )
            )
        )
        models['cylinder'] = args.n_cylinders

    if args.n_spheres is not None and args.n_spheres > 0:
        world_generator.add_asset(
            tag='sphere',
            description=dict(
                type='sphere',
                args=dict(
                    radius="__import__('numpy').random.uniform(0.1, 1)",
                    name='sphere',
                    color='xkcd'
                )
            )
        )
        models['sphere'] = args.n_spheres

    orientation_dofs = ['yaw']
    if args.set_random_roll:
        orientation_dofs.append('roll')
    if args.set_random_pitch:
        orientation_dofs.append('pitch')

    # Add placement policy
    placement_policy = dict(
        models=list(models.keys()),
        config=[
            dict(
                dofs=['x', 'y'],
                tag='workspace',
                workspace='room_workspace'
            ),
            dict(
                dofs=orientation_dofs,
                tag='uniform',
                mean=0,
                min=-3.141592653589793,
                max=3.141592653589793
            )
        ]
    )

    # Set local constraints
    local_constraints = list()
    for m in models:
        local_constraints.append(
            dict(model=m, constraint='tangent_to_ground_plane'))

    # Place objects randomly on the free
    # space within the walls
    world_generator.add_engine(
        tag='placement_engine',
        engine_name='random_pose',
        models=list(models.keys()),
        max_num=models,
        model_picker='random',
        no_collision=True,
        min_distance=0.0,
        policies=[placement_policy],
        constraints=local_constraints
    )

    # Run placement engine
    world_generator.run_engines(attach_models=True)
    world_generator.world.name = world_name
    if args.preview:
        world_generator.world.show()

    add_custom_gazebo_resource_path(args.export_models_dir)

    # Export world to file and walls model as Gazebo model
    full_world_filename = world_generator.export_world(
        output_dir=args.export_world_dir,
        filename=world_generator.world.name + '.world',
        models_output_dir=args.export_models_dir,
        overwrite=True)

    print('World file: {}'.format(full_world_filename))
