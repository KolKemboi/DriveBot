FROM osrf/ros:jazzy-desktop-full
# base image

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy	
# prevents apt prompts

ARG USERNAME=kol
ARG USER_UID=1000
ARG USER_GID=1000

# ---- system deps ----
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    cmake \
    python3-pip \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-rosdep \
    python3-argcomplete \
    python3-numpy \
    python3-pyqt5 \
    python3-lxml \
    ripgrep \
    fd-find \
    x11-apps \
    mesa-utils \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# ---- non-root user ----
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# ---- rosdep ----
RUN rosdep init || true
RUN rosdep update

# ---- MoveIt + ros2_control ----
RUN apt-get update && apt-get install -y \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-controller-manager \
    ros-jazzy-joint-state-broadcaster \
    && rm -rf /var/lib/apt/lists/*


# ---- colcon defaults ----
RUN mkdir -p /home/${USERNAME}/.colcon && \
    printf '{\n  "build": {\n    "symlink-install": true,\n    "cmake-args": ["-DCMAKE_BUILD_TYPE=Release"]\n  }\n}\n' \
    > /home/${USERNAME}/.colcon/defaults.yaml && \
    chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.colcon

# ---- workspace ----
RUN mkdir -p /home/${USERNAME}/ws/src \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/ws

WORKDIR /home/${USERNAME}/ws

# ---- bash env ----
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "source ~/ws/install/setup.bash 2>/dev/null" >> /home/${USERNAME}/.bashrc \
    && chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.bashrc

# ---- switch user ----
USER ${USERNAME}
