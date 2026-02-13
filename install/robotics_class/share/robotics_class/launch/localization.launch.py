import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.conditions import IfCondition
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy


def generate_launch_description():
    # 1. Configurações e Argumentos
    # Define um QoS para tópicos "latched"
    map_qos = QoSProfile(
        reliability=QoSReliabilityPolicy.RELIABLE,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        depth=1,
    )
    autostart = LaunchConfiguration("autostart")
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")
    use_sim_time = LaunchConfiguration("use_sim_time")
    params_file = LaunchConfiguration("params_file")

    # Lista de nós para o Lifecycle Manager gerenciar
    lifecycle_nodes = ["map_server", "amcl"]

    declare_autostart_cmd = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically startup the nav2 stack",
    )
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        "use_lifecycle_manager",
        default_value="true",
        description="Enable bond connection during node activation",
    )
    declare_use_sim_time_argument = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use simulation/Gazebo clock"
    )
    declare_params_file_cmd = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(
            get_package_share_directory("robotics_class"), "params", "default.yaml"
        ),
        description="Full path to the ROS2 parameters file",
    )
    declare_map_yaml_cmd = DeclareLaunchArgument(
        "map",
        default_value=os.path.join(
            get_package_share_directory("robotics_class"), "maps", "class_map.yaml"
        ),
        description="Full path to map yaml file",
    )

    static_map_to_odom = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="map_to_odom_broadcaster",
        output="screen",
        arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
    )

    start_map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            params_file,
            {"yaml_filename": LaunchConfiguration("map"), "use_sim_time": use_sim_time},
        ],
    )

    start_amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[params_file, {"use_sim_time": use_sim_time}],
    )

    start_lifecycle_manager = Node(
        condition=IfCondition(use_lifecycle_manager),
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"autostart": True},
            {"node_names": lifecycle_nodes},
        ],
    )

    ld = LaunchDescription()

    # Adiciona os argumentos
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_lifecycle_manager)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_params_file_cmd)

    # Adiciona os nós
    ld.add_action(start_map_server)
    ld.add_action(start_amcl)
    ld.add_action(static_map_to_odom)
    ld.add_action(start_lifecycle_manager)

    return ld
